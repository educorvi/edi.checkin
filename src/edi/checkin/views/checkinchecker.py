# -*- coding: utf-8 -*-
from plone import api as ploneapi
import hashlib
import datetime
from DateTime import DateTime
from edi.checkin import _
from Products.Five.browser import BrowserView

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class CheckinChecker(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('check_checkin.pt')

    def check(self):
        test = self.context.get(self.request.get('checksum'))
        if test:
            return True 
        return False

    def __call__(self):
        # Implement your own actions:
        check = self.check()
        if check:
            self.msg = 'Der Pass ist gültig'
            self.cssclass = 'display-4 bg-success text-white p-4'
        else:
            self.msg = 'Der Pass ist ungültig'
            self.cssclass = 'display-4 bg-danger text-white p-4'
        return self.index()
