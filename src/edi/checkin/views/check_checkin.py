# -*- coding: utf-8 -*-

from plone import api as ploneapi
import hashlib
import datetime
from edi.checkin import _
from Products.Five.browser import BrowserView

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class CheckCheckin(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('check_checkin.pt')

    def check(self):
        heute = datetime.datetime.now().strftime('%d.%m.%Y').encode('utf-8')
        portal = ploneapi.portal.get().EffectiveDate().encode('utf-8')
        m = hashlib.sha256()
        #m.update(self.request.get('email').encode('utf-8'))
        m.update(heute)
        m.update(portal)       
        refcode = m.hexdigest()
        if refcode == self.request.get('checksum'):
            return 'Valid'
        else:
            return 'Not Valid' 

    def __call__(self):
        # Implement your own actions:
        self.msg = self.check()
        return self.index()
