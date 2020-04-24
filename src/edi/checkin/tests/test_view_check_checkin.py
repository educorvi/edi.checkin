# -*- coding: utf-8 -*-
from edi.checkin.testing import EDI_CHECKIN_FUNCTIONAL_TESTING
from edi.checkin.testing import EDI_CHECKIN_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = EDI_CHECKIN_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, 'Folder', 'other-folder')
        api.content.create(self.portal, 'Document', 'front-page')

    def test_check_checkin_is_registered(self):
        view = getMultiAdapter(
            (self.portal['other-folder'], self.portal.REQUEST),
            name='check-checkin'
        )
        self.assertTrue(view.__name__ == 'check-checkin')
        # self.assertTrue(
        #     'Sample View' in view(),
        #     'Sample View is not found in check-checkin'
        # )

    def test_check_checkin_not_matching_interface(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal['front-page'], self.portal.REQUEST),
                name='check-checkin'
            )


class ViewsFunctionalTest(unittest.TestCase):

    layer = EDI_CHECKIN_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
