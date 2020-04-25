# -*- coding: utf-8 -*-
from edi.checkin.content.office import IOffice  # NOQA E501
from edi.checkin.testing import EDI_CHECKIN_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class OfficeIntegrationTest(unittest.TestCase):

    layer = EDI_CHECKIN_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_office_schema(self):
        fti = queryUtility(IDexterityFTI, name='Office')
        schema = fti.lookupSchema()
        self.assertEqual(IOffice, schema)

    def test_ct_office_fti(self):
        fti = queryUtility(IDexterityFTI, name='Office')
        self.assertTrue(fti)

    def test_ct_office_factory(self):
        fti = queryUtility(IDexterityFTI, name='Office')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IOffice.providedBy(obj),
            u'IOffice not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_office_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Office',
            id='office',
        )

        self.assertTrue(
            IOffice.providedBy(obj),
            u'IOffice not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('office', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('office', parent.objectIds())

    def test_ct_office_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Office')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_office_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Office')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'office_id',
            title='Office container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
