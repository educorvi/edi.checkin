# -*- coding: utf-8 -*-
import datetime
import qrcode
from zope import schema
import hashlib
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
from edi.checkin.views.alert_danger_embedded import create_userbody as dangerbody
from edi.checkin.views.alert_success_embedded import create_userbody as successbody
from base64 import encodestring
from plone import api as ploneapi
import plone.app.z3cform
import plone.z3cform.templates


from edi.checkin import _

class ICheckin(model.Schema):

    email = schema.TextLine(title=u"Meine E-Mail-Adresse", required=True)
    rules = schema.Bool(title=u"Ich habe die Regeln zum Infektionsschutz befolgt. Es gelten die Regeln des Bundeslandes in dem Du wohnst.", 
                        description=u"Es gelten die Regeln des Bundeslandes indem Du Deinen Hauptwohnsitz hast.",
                        required=True)

    healthy = schema.Bool(title=u"Ich fühle mich gesund und fit. Ich habe keine Erkältungssymptome. Ich habe kein Fieber oder trockenen Husten.",
                         description=u"Ich habe keine Erkältungssymptome. Ich habe kein Fieber und keinen trockenen Husten.",
                         required=True)


class CheckinForm(AutoExtensibleForm, form.Form):

    label = u"Check In"
    description = u"Ein erfolgreich durchgeführter Checkin ist Voraussetzung für den Zutritt zu diesem Büro.\
                    Zur Gewährleistung des Infektionsschutzes besteht eine Pflicht zu wahren und vollständigen Angaben."
    ignoreContext = True

    schema = ICheckin

    def create_qrcode(self, data):
        heute = datetime.datetime.now().strftime('%d.%m.%Y').encode('utf-8')
        portal = ploneapi.portal.get().EffectiveDate().encode('utf-8')
        m = hashlib.sha256()
        #m.update(encodestring(data.get('email').encode('utf-8')))
        m.update(heute)
        m.update(portal)
        url = "https://www.educorvi.de/checkcheckin?email=%s&checksum=%s" %(encodestring(data.get('email').encode('utf-8')), m.hexdigest())
        filename = "qr.png"
        img = qrcode.make(url)
        img.save(filename)
        return img
    
    def sendmails(self, data):
        mime_msg = MIMEMultipart('related')
        mime_msg['Subject'] = u"Status des Checkins: %s (%s)" %(data.get('status'), data.get('email'))
        mime_msg['From'] = u"educorvi@web.de"
        mime_msg['To'] = data.get('email')
        mime_msg['CC'] = 'info@educorvi.de'
        mime_msg.preamble = 'This is a multi-part message in MIME format.'
        msgAlternative = MIMEMultipart('alternative')
        mime_msg.attach(msgAlternative)

        if data.get('status') == 'success':
            htmltext = successbody(data)
        else:
            htmltext = dangerbody(data)

        msg_txt = MIMEText(htmltext, _subtype='html', _charset='utf-8')
        msgAlternative.attach(msg_txt)

        img = self.create_qrcode(data)
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
        if errors:
            url = ploneapi.portal.get().absolute_url() + '/checkin'
            ploneapi.portal.show_message(message="Bitte trage Deine E-Mail-Adresse ein und versuche es erneut.", request=self.request, type='error')
            return self.request.response.redirect(url)

        url = ploneapi.portal.get().absolute_url() + '/checked-message'
        if data.get('rules') and data.get('healthy'):
            data['status'] = u'success'
            data['class'] = u'card border-success'
            data['date'] = datetime.datetime.now().strftime('%d.%m.%Y')
            qrimage = self.create_qrcode(data)
            qrfile = open('qr.png', 'rb')
            qrfile.seek(0)
            data['qrimage'] = '<img src="cid:image1" alt="img" />'
        else:
            data['status'] = u'fail'
            data['class'] = u'card text-white bg-danger'
            data['date'] = (datetime.datetime.now() + datetime.timedelta(days=14)).strftime('%d.%m.%Y')
        
        mails = self.sendmails(data)

        url = url + '?status=%s&class=%s&date=%s' %(data.get('status'), data.get('class'), data.get('date'))        
        return self.request.response.redirect(url)
