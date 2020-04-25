# -*- coding: utf-8 -*-
from edi.checkin.content.checkin import ICheckin  # NOQA E501
from edi.checkin.testing import EDI_CHECKIN_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class CheckinIntegrationTest(unittest.TestCase):

    layer = EDI_CHECKIN_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'Office',
            self.portal,
            'parent_container',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_checkin_schema(self):
        fti = queryUtility(IDexterityFTI, name='Checkin')
        schema = fti.lookupSchema()
        self.assertEqual(ICheckin, schema)

    def test_ct_checkin_fti(self):
        fti = queryUtility(IDexterityFTI, name='Checkin')
        self.assertTrue(fti)

    def test_ct_checkin_factory(self):
        fti = queryUtility(IDexterityFTI, name='Checkin')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ICheckin.providedBy(obj),
            u'ICheckin not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_checkin_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Checkin',
            id='checkin',
        )

        self.assertTrue(
            ICheckin.providedBy(obj),
            u'ICheckin not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('checkin', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('checkin', parent.objectIds())

    def test_ct_checkin_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Checkin')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )
