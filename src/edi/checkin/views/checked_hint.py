# -*- coding: utf-8 -*-
from edi.checkin import _
from Products.Five.browser import BrowserView

class CheckedMessage(BrowserView):

    def __call__(self):
        self.status = self.request.get('status')
        self.cssclass = self.request.get('class')
        self.date = self.request.get('date')
        self.start = self.request.get('start')
        self.end = self.request.get('end')
        self.reason = self.request.get('reason')
        return self.index()
