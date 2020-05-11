# -*- coding: utf-8 -*-
import datetime
import requests
import qrcode
import hashlib
import z3c.form
import plone.app.z3cform
import plone.z3cform.templates
from DateTime import DateTime
from zope import schema
from z3c.form import button, form, field
from plone.supermodel import model
from plone.autoform import directives
from plone.autoform.form import AutoExtensibleForm
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile as FiveViewPageTemplateFile
from plone import api as ploneapi
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from edi.checkin.browser.alert_danger_embedded import create_userbody as dangerbody
from edi.checkin.browser.alert_success_embedded import create_userbody as successbody
from base64 import encodestring
from plone import api as ploneapi
from edi.checkin.content.office import validate_email

from edi.checkin import _

class ICheckin(model.Schema):

    email = schema.TextLine(title=_(u"Meine E-Mail-Adresse"), 
                            constraint=validate_email,
                            required=True)

    rules = schema.Bool(title=_(u"Ich habe die Regeln zum Infektionsschutz befolgt. Es gelten die Regeln des Bundeslandes\
                                  in dem Du wohnst."), 
                        required=True)

    healthy = schema.Bool(title=_(u"Ich fühle mich gesund und fit. Ich habe keine Erkältungssymptome. Ich habe kein Fieber\
                                  oder trockenen Husten."),
                         required=True)


class CheckinForm(AutoExtensibleForm, form.Form):

    label = _(u"Check In")
    description = _(u"Ein erfolgreich durchgeführter Checkin ist Voraussetzung für den Zutritt zu diesem Raum.\
                    Zur Gewährleistung des Infektionsschutzes besteht eine Pflicht zu wahren und vollständigen Angaben.")

    ignoreContext = True

    schema = ICheckin

    def check_times(self):
        """Prueft, ob der Checkin vor oder während der Öffnungszeit erfolgt und gibt den möglichen
           Zeitraum der Anwesenheit zurück.
           Es gilt: 
             Checkin vor Öffnungszeit -> Start = Bürozeit | Ende = Start + max Aufenthaltsdauer
             Checkin während der Öffnungszeit -> Start = Aktuelle Zeit | Ende = Aktuelle Zeit + max Aufenthaltsdauer oder Schliesszeit
        """
        start_data = [int(i) for i in self.context.beginn.split(':')]
        beginn = datetime.time(start_data[0], start_data[1])
        end_data = [int(i) for i in self.context.beginn.split(':')]
        ende = datetime.time(end_data[0], end_data[1])
        heute = datetime.date.today() #Datum
        jetzt = datetime.time(datetime.datetime.now().hour, datetime.datetime.now().minute) #Uhrzeit
        timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        if jetzt <= beginn:
            start = datetime.datetime.combine(heute, beginn, tzinfo=timezone)
            if self.context.maxtime <= 24:
                end = datetime.datetime.combine(heute, beginn, tzinfo=timezone) + datetime.timedelta(hours=self.context.maxtime)
            else:
                end = datetime.datetime.combine(heute, beginn, tzinfo=timezone) + datetime.timedelta(minutes=self.context.maxtime)
            checktimes = (start, end)
            return checktimes #Datetime-Objekte mit Angabe der Zeitzone
        elif beginn < jetzt < ende:
            start = datetime.datetime.combine(heute, jetzt, tzinfo=timezone)
            finaltime = datetime.datetime.combine(heute, ende, tzinfo=timezone)
            end = finaltime
            if self.context.maxtime <= 24:
                if (start + datetime.timedelta(hours=self.context.maxtime)) <= finaltime:
                    end = start + datetime.timedelta(hours=self.context.maxtime)
            else:
                if (start + datetime.timedelta(minutes=self.context.maxtime)) <= finaltime:
                    end = start + datetime.timedelta(minutes=self.context.maxtime)
            checktimes = (start, end)
            return checktimes #Datetime-Objekte mit Angabe der Zeitzone
        else:
            return None

    def alternate_checktimes(self, checktimes):
        """ Sucht innerhalb der Öffnungszeit in 5 Minuten Schritten nach alternativen Checkinzeiten. 
        """
        portal_catalog = ploneapi.portal.get_tool('portal_catalog')
        office_path = '/'.join(self.context.getPhysicalPath())
        end_hour = int(self.context.ende.split(':')[0])
        end_minutes = int(self.context.ende.split(':')[1])
        ende = datetime.time(end_hour, end_minutes)
        heute = datetime.date.today()
        timezone = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        schliessung = datetime.datetime.combine(heute, ende, tzinfo=timezone)
        available_time = True
        check_start = checktimes[0]
        check_end = checktimes[1]
        maxtime = self.context.maxtime
        overtime = self.context.overtime
        maxperson = self.context.maxperson
        while available_time:
            check_start = check_start + datetime.timedelta(minutes=5)
            check_end = check_end + datetime.timedelta(minutes=5)
            query_current = {}
            if self.context.maxtime <= 24:
                query_current['start'] = {'query':(
                     DateTime(check_start - datetime.timedelta(hours=maxtime) - datetime.timedelta(minutes=overtime)),
                     DateTime(check_start + datetime.timedelta(minutes=1))),
                     'range': 'min:max'}
            else:
                query_current['start'] = {'query':(
                    DateTime(check_start - datetime.timedelta(minutes=maxtime) - datetime.timedelta(minutes=overtime)),
                    DateTime(check_start + datetime.timedelta(minutes=1))),
                    'range': 'min:max'}
            query_current['portal_type'] = "Checkin"
            query_current['path'] = office_path
            brains = portal_catalog.unrestrictedSearchResults(**query_current)
            if len(brains) < maxperson:
                return (check_start, check_end) # neue Checkinzeit wird zurückgegeben
            else:
                if self.context.maxtime <= 24:
                    if schliessung - datetime.timedelta(hours=maxtime) < check_start:
                        available_time = False
                else:
                    if schliessung - datetime.timedelta(minutes=maxtime) < check_start:
                        available_time = False
        return () # es wurde keine alternative Checkinzeit gefunden


    def check_persons(self, email, checktimes):
        """ Prüft die Checkins (Personenzahl) im entsprechenden Zeitraum und legt einen neuen Checkin an,
            wenn der Zeitraum verfügbar ist.
        """
        portal_catalog = ploneapi.portal.get_tool('portal_catalog')
        office_path = '/'.join(self.context.getPhysicalPath())
        query_current = {}
        overtime = self.context.overtime #Zeitzugabe
        maxtime = self.context.maxtime #max. Aufenthaltsdauer
        maxperson = self.context.maxperson #max. Personenzahl
        if maxtime <= 24:
            query_current['start'] = {'query':(
                DateTime(checktimes[0] - datetime.timedelta(hours=maxtime) - datetime.timedelta(minutes=overtime)),
                DateTime(checktimes[0] + datetime.timedelta(minutes=5))),
                'range': 'min:max'}
        else:
            query_current['start'] = {'query':(
                DateTime(checktimes[0] - datetime.timedelta(minutes=maxtime) - datetime.timedelta(minutes=overtime)),
                DateTime(checktimes[0] + datetime.timedelta(minutes=5))),
                'range': 'min:max'}
        query_current['portal_type'] = "Checkin"
        query_current['path'] = office_path
        query_current['Title'] = email
        brains = portal_catalog.unrestrictedSearchResults(**query_current)
        if len(brains) > 0:
            return {'status':'warning', 'reason':u'alreadychecked'}
        del query_current['Title']
        brains = portal_catalog.unrestrictedSearchResults(**query_current)
        if len(brains) >= maxperson:
            checktimes = self.alternate_checktimes(checktimes)
            if checktimes:
                retcode = self.create_checkin(email, checktimes)
            else:
                return {'status':'warning', 'reason':u'maxpersons'}
        else:
            retcode = self.create_checkin(email, checktimes)
        if retcode == 201:
            return {'status':'success', 'times':checktimes}
        return {'status':'error'}

    def create_checkin(self, email, checktimes):
        portal = ploneapi.portal.get().EffectiveDate().encode('utf-8')
        m = hashlib.sha256()
        m.update(portal)
        m.update(checktimes[0].isoformat().encode('utf-8'))
        m.update(email.encode('utf-8'))
        objid = m.hexdigest()
        endtime = checktimes[1] + datetime.timedelta(minutes=self.context.overtime)
        objjson = {'@type':'Checkin', 'id':objid, 'title':email, 'start':checktimes[0].isoformat(), 'end':endtime.isoformat()}
        retcode = requests.post(self.context.absolute_url(), headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, 
                                json=objjson, auth=('admin', 'admin'))
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
        filename = "qr.png" #here we need a Temporary File
        img = qrcode.make(url)
        img.save(filename)
        return img
    
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
            ploneapi.portal.show_message(message=_(u"Bitte überprüfe Deine E-Mail-Adresse und versuche es erneut."), 
                                                  request=self.request, type='error')
            return self.request.response.redirect(url)
 
        if self.context.adressen:
            if data.get('email') not in self.context.adressen:
                ploneapi.portal.show_message(message=_("Mit dieser E-Mail-Adresse kannst Du nicht in diesen Raum einchecken."), 
                                             request=self.request, type='error')
                return self.request.response.redirect(url)

        if data.get('rules') and data.get('healthy'):
            checktimes = self.check_times()
            if checktimes: #Tuple mit Datetime Objekten
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
        url += '?status=%s&class=%s&date=%s&start=%s&end=%s&reason=%s' %(data.get('status'), data.get('class'), data.get('date'), data.get('start'),
                                                               data.get('end'), data.get('reason'))        
        return self.request.response.redirect(url)
