# -*- coding: utf-8 -*-

from edi.checkin import _
from Products.Five.browser import BrowserView

# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class CheckedMessage(BrowserView):
    # If you want to define a template here, please remove the template from
    # the configure.zcml registration of this view.
    # template = ViewPageTemplateFile('checked_message.pt')

    def __call__(self):
        # Implement your own actions:
        self.status = self.request.get('status')
        self.cssclass = self.request.get('class')
        self.date = self.request.get('date')
        self.raum = self.context.title
        return self.index()
