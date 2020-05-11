# -*- coding: utf-8 -*-
import datetime
from edi.checkin import _
from Products.Five.browser import BrowserView
from plone import api as ploneapi
# from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile


class EventsView(BrowserView):


    def get_upcoming_veranstaltungen(self):
        
        entries = []
        eventquery = {'query': (datetime.datetime.now()), 'range':'min'}
        contents = ploneapi.content.find(context=self.context, portal_type="Veranstaltung", 
                                         start=eventquery, sort_on="start", sort_order="ascending")
        for i in contents:
            entry = {}
            entry['title'] = i.Title
            entry['description'] = i.Description
            entry['url'] = i.getURL()
            entry['day'] = i.start.strftime('%d.%m.')
            entry['time'] = "%s - %s" %(i.start.strftime('%H:%M'), i.end.strftime('%H:%M'))
            if datetime.date.today() == i.start.date():
                entry['btnclass'] = u'btn btn-primary btn-lg'
                entry['comment'] = u''
            else:
                entry['btnclass'] = u'btn btn-primary btn-lg disabled'
                entry['comment'] = u'Ein Checkin ist aus Gründen des Infektionsschutzes erst am Tag der Veranstaltung möglich'
            entries.append(entry)
        return entries
            

    def __call__(self):

        # Implement your own actions:
        self.veranstaltungen = self.get_upcoming_veranstaltungen()
        return self.index()
