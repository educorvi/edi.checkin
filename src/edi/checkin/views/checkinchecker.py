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
        date_range = {
            'query': (
                DateTime(datetime.datetime.combine(datetime.date.today(), datetime.time(0,0))),
                DateTime(datetime.datetime.combine(datetime.date.today(), datetime.time(23,59))),
            ),
            'range': 'min:max',
        }
        office_path = '/'.join(self.context.getPhysicalPath())
        portal_catalog = ploneapi.portal.get_tool('portal_catalog')
        brains = portal_catalog.unrestrictedSearchResults(portal_type="Checkin", path=office_path, id=self.request.get('checksum'))
        if brains:
            if brains[0].start <= datetime.datetime.now() <= brains[0].end:
                return 'Valid'
        return 'Not Valid'

    def __call__(self):
        # Implement your own actions:
        self.msg = self.check()
        return self.index()
