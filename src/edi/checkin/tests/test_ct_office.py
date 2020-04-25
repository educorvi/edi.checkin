# -*- coding: utf-8 -*-
from edi.checkin.testing import EDI_CHECKIN_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName


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
        schema_name = portalTypeToSchemaName('Office')
        self.assertEqual(schema_name, schema.getName())

    def test_ct_office_fti(self):
        fti = queryUtility(IDexterityFTI, name='Office')
        self.assertTrue(fti)

    def test_ct_office_factory(self):
        fti = queryUtility(IDexterityFTI, name='Office')
        factory = fti.factory
        obj = createObject(factory)


    def test_ct_office_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Office',
            id='office',
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
