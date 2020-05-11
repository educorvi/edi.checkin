# -*- coding: utf-8 -*-
from plone import api as ploneapi
import hashlib
import datetime
from DateTime import DateTime
from edi.checkin import _
from Products.Five.browser import BrowserView


class CheckinChecker(BrowserView):

    def check(self):
        test = self.context.get(self.request.get('checksum'))
        if test:
            return True 
        return False

    def __call__(self):
        check = self.check()
        if check:
            self.msg = 'Der Pass ist gültig'
            self.cssclass = 'display-4 bg-success text-white p-4'
        else:
            self.msg = 'Der Pass ist ungültig'
            self.cssclass = 'display-4 bg-danger text-white p-4'
        return self.index()
