# -*- coding: utf-8 -*-
import datetime
import requests
import qrcode
import hashlib
from DateTime import DateTime
from zope import schema
from z3c.form import button, form, field
from plone.supermodel import model
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from collective.beaker.interfaces import ISession
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile
from plone import api as ploneapi
from edi.classroom.forms.mailconfig import create_edibody
from edi.classroom.forms.receipt import create_userbody
import z3c.form
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from edi.checkin.browser.alert_danger_embedded import create_userbody as dangerbody
from edi.checkin.browser.alert_success_embedded import create_userbody as successbody
from base64 import encodestring
from plone import api as ploneapi
import plone.app.z3cform
import plone.z3cform.templates


from edi.checkin import _

class ICheckin(model.Schema):

    email = schema.TextLine(title=_(u"Meine E-Mail-Adresse"), required=True)
    rules = schema.Bool(title=_(u"Ich habe die Regeln zum Infektionsschutz befolgt. Es gelten die Regeln des Bundeslandes in dem Du wohnst."), 
                        description=_(u"Es gelten die Regeln des Bundeslandes indem Du Deinen Hauptwohnsitz hast."),
                        required=True)

    healthy = schema.Bool(title=_(u"Ich fühle mich gesund und fit. Ich habe keine Erkältungssymptome. Ich habe kein Fieber oder trockenen Husten."),
                         description=_(u"Ich habe keine Erkältungssymptome. Ich habe kein Fieber und keinen trockenen Husten."),
                         required=True)


class CheckinForm(AutoExtensibleForm, form.Form):

    label = _(u"Check In")
    description = _(u"Ein erfolgreich durchgeführter Checkin ist Voraussetzung für den Zutritt zu diesem Büro.\
                    Zur Gewährleistung des Infektionsschutzes besteht eine Pflicht zu wahren und vollständigen Angaben.")

    ignoreContext = True

    schema = ICheckin

    def check_times(self):
        b_hour = int(self.context.beginn.split(':')[0])
        b_minutes = int(self.context.beginn.split(':')[1])
        beginn = datetime.time(b_hour, b_minutes)
        e_hour = int(self.context.ende.split(':')[0])
        e_minutes = int(self.context.ende.split(':')[1])
        ende = datetime.time(e_hour, e_minutes)
        heute = datetime.date.today()
        jetzt = datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute)
        if jetzt <= beginn:
            start = datetime.datetime.combine(heute, beginn)
            end = datetime.datetime.combine(heute, beginn) + datetime.timedelta(hours=self.context.maxtime)
            return (start, end)
        elif beginn < jetzt < ende:
            start = datetime.datetime.combine(heute, jetzt)
            finaltime = datetime.datetime.combine(heute, ende)
            if (start + datetime.timedelta(hours=self.context.maxtime)) <= finaltime:
                end = start + datetime.timedelta(hours=self.context.maxtime)
            else:
                end = finaltime
            return (start, end)
        else:
            return None

    def check_persons(self, email, checktimes):
        date_range = {
            'query': (
                DateTime(datetime.datetime.combine(datetime.date.today(), datetime.time(0,0))),
                DateTime(datetime.datetime.combine(datetime.date.today(), datetime.time(23,59))),
            ),
            'range': 'min:max',
        }
        office_path = '/'.join(self.context.getPhysicalPath())
        portal_catalog = ploneapi.portal.get_tool('portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults(portal_type="Checkin", path=office_path, start=date_range, Title=email)
        if len(brains) > 0:
            return {'status':'warning', 'reason':u'alreadychecked'}
        brains = portal_catalog.unrestrictedSearchResults(portal_type="Checkin", path=office_path, start=date_range)
        if len(brains) >= self.context.maxperson:
            return {'status':'warning', 'reason':u'maxpersons'}
        retcode = self.create_checkin(email, checktimes)
        if retcode == 201:
            return {'status':'success'}
        return {'status':'error'}

    def create_checkin(self, email, checktimes):
        portal = ploneapi.portal.get().EffectiveDate().encode('utf-8')
        m = hashlib.sha256()
        m.update(portal)
        m.update(datetime.date.today().isoformat().encode('utf-8'))
        m.update(email.encode('utf-8'))
        objid = m.hexdigest()
        objjson = {'@type':'Checkin', 'id':objid, 'title':email, 'start':checktimes[0].isoformat(), 'end':checktimes[1].isoformat()}
        try:
            retcode = requests.post(self.context.absolute_url(), headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, 
                                    json=objjson, auth=('admin', 'krks.d3print'))
            status = retcode.status_code
        except:
            print('Error Second Request')
            status = 500
        return status

    def create_qrcode(self, data, checktimes):
        portal = ploneapi.portal.get().EffectiveDate().encode('utf-8')
        m = hashlib.sha256()
        m.update(portal)
        m.update(datetime.date.today().isoformat().encode('utf-8'))
        m.update(data.get('email').encode('utf-8'))
        checksum = m.hexdigest()
        url = self.context.absolute_url() + "/checkinchecker?checksum=%s" % checksum
        filename = "qr.png" #here we need a Temporary File
        img = qrcode.make(url)
        img.save(filename)
        return img
    
    def sendmails(self, data, checktimes):
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = u"Status des Checkins: %s (%s)" %(data.get('status'), data.get('email'))
        mime_msg['From'] = u"educorvi@web.de" #replace with portal from address
        mime_msg['To'] = data.get('email')
        mime_msg.preamble = 'This is a multi-part message in MIME format.'
        msgAlternative = MIMEMultipart('alternative')
        mime_msg.attach(msgAlternative)

        if data.get('status') == 'success':
            htmltext = successbody(data, checktimes)
        else:
            htmltext = dangerbody(data)

        msg_txt = MIMEText(htmltext, _subtype='html', _charset='utf-8')
        msgAlternative.attach(msg_txt)

        img = self.create_qrcode(data, checktimes)
        qrimage = open('qr.png', 'rb')
        qrimage.seek(0)
        msgImage = MIMEImage(qrimage.read())

        msgImage.add_header('Content-ID', '<image1>')
        mime_msg.attach(msgImage)

        mail_host = ploneapi.portal.get_tool(name='MailHost')
        mail_host.send(mime_msg.as_string())


    @button.buttonAndHandler(u'Checkin durchführen')
    def handleApply(self, action):
        data, errors = self.extractData()
        url = self.context.absolute_url()
        if errors:
            ploneapi.portal.show_message(message="Bitte trage Deine E-Mail-Adresse ein und versuche es erneut.", request=self.request, type='error')
            return self.request.response.redirect(url)
 
        if self.context.adressen:
            if data.get('email') not in self.context.adressen:
                ploneapi.portal.show_message(message="Mit dieser E-Mail-Adresse kannst Du nicht in dieses Office einchecken.", 
                                             request=self.request, type='error')
                return self.request.response.redirect(url)

        if data.get('rules') and data.get('healthy'):
            checktimes = self.check_times()
            if checktimes:
                checkpersons = self.check_persons(data.get('email'), checktimes)
                if checkpersons.get('status') == u'warning':
                    data['status'] = u'warning'
                    data['class'] = u'card text-white bg-warning'
                    data['date'] = datetime.datetime.now().strftime('%d.%m.%Y')
                    data['reason'] = checkpersons.get('reason')
                elif checkpersons.get('status') == u'success':
                    data['status'] = u'success'
                    data['class'] = u'card border-success'
                    data['date'] = datetime.datetime.now().strftime('%d.%m.%Y')
                    data['start'] = checktimes[0].strftime('%H:%M')
                    data['end'] = checktimes[1].strftime('%H:%M')
                    data['qrimage'] = '<img src="cid:image1" alt="img" />'
                    checkpersons = self.check_persons(data.get('email'), checktimes)
                else:
                    ploneapi.portal.show_message(message="Ein Fehler ist aufgetreten. Bitte benachrichtige den Administrator.",
                                                 request=self.request, type='error')
                    return self.request.response.redirect(url)
            else:
                data['status'] = u'warning'
                data['class'] = u'card text-white bg-warning'
                data['date'] = datetime.datetime.now().strftime('%d.%m.%Y')
                data['reason'] = 'outoftime'
        else:
            data['status'] = u'fail'
            data['class'] = u'card text-white bg-danger'
            data['date'] = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime('%d.%m.%Y')

        if data['status'] in ['success', 'fail']:        
            mails = self.sendmails(data, checktimes)

        url += '/checked-hint'
        url += '?status=%s&class=%s&date=%s&start=%s&end=%s&reason=%s' %(data.get('status'), data.get('class'), data.get('date'), data.get('start'),
                                                               data.get('end'), data.get('reason'))        
        return self.request.response.redirect(url)
