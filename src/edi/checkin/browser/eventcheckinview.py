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
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile
from plone import api as ploneapi
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
from edi.checkin.browser.checkinview import ICheckin

from edi.checkin import _


class CheckinForm(AutoExtensibleForm, form.Form):

    label = _(u"Check In")
    description = _(u"Ein erfolgreich durchgeführter Checkin ist Voraussetzung für den Zutritt zu dieser Veranstaltung.\
                    Zur Gewährleistung des Infektionsschutzes besteht eine Pflicht zu wahren und vollständigen Angaben.")

    ignoreContext = True

    schema = ICheckin

    def check_times(self):
        """Prueft, ob der Checkin vor oder während der Veranstaltungszeit erfolgt.
           Es gilt: 
             Checkin vor Veranstaltungsbeginn -> Start = Aktuelle Veranstaltungsbeginn| Ende = Veranstaltungsende 
             Checkin vor Ende der Veranstaltung -> Start = Aktuelle Zeit | Ende = Veranstaltungsende
             Checkin nach Ende der Veranstaltung = Kein Checkin möglich
        """
        beginn = self.context.start
        ende = self.context.end
        timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        current_datetime = datetime.datetime.now()
        if current_datetime <= beginn:
            start = beginn.replace(tzinfo=timezone)
            end = ende.replace(tzinfo=timezone)
            return (start, end)
        elif beginn < current_datetime < ende:
            start = current_datetime.replace(tzinfo=timezone)
            end = ende.replace(tzinfo=timezone)
            return (start, end)
        else:
            return None

    def check_persons(self, email, checktimes):
        """ Prüft die Checkins im Zeitraum und legt einen neuen Checkin an, wenn der Zeitraum verfügbar ist.
        """
        portal_catalog = ploneapi.portal.get_tool('portal_catalog')
        office_path = '/'.join(self.context.getPhysicalPath())
        query_current = {}
        query_current['start'] = {'query':(
            DateTime(self.context.start - datetime.timedelta(minutes=5)),
            DateTime(self.context.end + datetime.timedelta(minutes=5))),
            'range': 'min:max'}
        query_current['portal_type'] = "Checkin"
        query_current['path'] = office_path
        query_current['Title'] = email
        brains = portal_catalog.unrestrictedSearchResults(**query_current)
        if len(brains) > 0:
            return {'status':'warning', 'reason':u'alreadychecked'}
        del query_current['Title']
        print(query_current)
        brains = portal_catalog.unrestrictedSearchResults(**query_current)
        if len(brains) >= self.context.maxperson:
            return {'status':'warning', 'reason':u'maxpersons'}
        else:
            retcode = self.create_checkin(email, checktimes)
        if retcode == 201:
            return {'status':'success', 'times':checktimes}
        return {'status':'error'}

    def create_checkin(self, email, checktimes):
        adminuser = ploneapi.portal.get_registry_record('edi.checkin.browser.settings.ICheckinSettings.adminuser')
        adminpassword = ploneapi.portal.get_registry_record('edi.checkin.browser.settings.ICheckinSettings.adminpassword')
        portal = ploneapi.portal.get().EffectiveDate().encode('utf-8')
        m = hashlib.sha256()
        m.update(portal)
        m.update(checktimes[0].isoformat().encode('utf-8'))
        m.update(email.encode('utf-8'))
        objid = m.hexdigest()
        endtime = checktimes[1] + datetime.timedelta(minutes=self.context.overtime)
        objjson = {'@type':'Checkin', 'id':objid, 'title':email, 'start':checktimes[0].isoformat(), 'end':endtime.isoformat()}
        retcode = requests.post(self.context.absolute_url(), headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, 
                                json=objjson, auth=(adminuser, adminpassword))
        status = retcode.status_code
        return status

    def create_qrcode(self, data, checktimes):
        portal = ploneapi.portal.get().EffectiveDate().encode('utf-8')
        m = hashlib.sha256()
        m.update(portal)
        m.update(checktimes[0].isoformat().encode('utf-8'))
        m.update(data.get('email').encode('utf-8'))
        checksum = m.hexdigest()
        url = self.context.absolute_url() + "/checkinchecker?checksum=%s" % checksum
        filehandle = tempfile.TemporaryFile()
        img = qrcode.make(url)
        img.save(filehandle)
        return filehandle
    
    def sendmails(self, data, checktimes):
        portal = ploneapi.portal.get().absolute_url()
        logo = portal + '/++theme++plonetheme.siguv/logo/bg-etem.svg'
        checkinurl = self.context.absolute_url() 
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = u"Status des Checkins: %s (%s)" %(data.get('status'), data.get('email'))
        mime_msg['From'] = ploneapi.portal.get_registry_record('plone.email_from_address')
        if data.get('status') == 'fail':
            mime_msg['CC'] = self.context.notification_mail
        mime_msg['To'] = data.get('email')
        mime_msg.preamble = 'This is a multi-part message in MIME format.'
        msgAlternative = MIMEMultipart('alternative')
        mime_msg.attach(msgAlternative)

        if data.get('status') == 'success':
            htmltext = successbody(data, checktimes, self.context.title, portal, logo, checkinurl)
        else:
            htmltext = dangerbody(data, self.context.title, portal, logo, checkinurl)

        msg_txt = MIMEText(htmltext, _subtype='html', _charset='utf-8')
        msgAlternative.attach(msg_txt)


        if data.get('status') == 'success':
            filehandle = self.create_qrcode(data, checktimes)
            filehandle.seek(0)
            msgImage = MIMEImage(filehandle.read())
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
                ploneapi.portal.show_message(message="Mit dieser E-Mail-Adresse kannst Du nicht in diesen Raum einchecken.", 
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
                    checktimes = checkpersons.get('times')
                    data['status'] = u'success'
                    data['class'] = u'card border-success'
                    data['date'] = datetime.datetime.now().strftime('%d.%m.%Y')
                    data['start'] = checktimes[0].strftime('%H:%M')
                    data['end'] = checktimes[1].strftime('%H:%M')
                    data['qrimage'] = '<img src="cid:image1" alt="img" />'
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
            checktimes = None
            data['status'] = u'fail'
            data['class'] = u'card text-white bg-danger'
            data['date'] = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime('%d.%m.%Y')

        if data['status'] in ['success', 'fail']:        
            mails = self.sendmails(data, checktimes)

        url += '/checked-hint'
        url += '?status=%s&class=%s&date=%s&start=%s&end=%s&reason=%s' %(data.get('status'), 
                                                                         data.get('class'), 
                                                                         data.get('date'), 
                                                                         data.get('start'),
                                                                         data.get('end'), 
                                                                         data.get('reason'))        
        return self.request.response.redirect(url)
