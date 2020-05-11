# -*- coding: utf-8 -*-
from edi.checkin.content.veranstaltung import IVeranstaltung  # NOQA E501
from edi.checkin.testing import EDI_CHECKIN_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest




class VeranstaltungIntegrationTest(unittest.TestCase):

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

    def test_ct_veranstaltung_schema(self):
        fti = queryUtility(IDexterityFTI, name='Veranstaltung')
        schema = fti.lookupSchema()
        self.assertEqual(IVeranstaltung, schema)

    def test_ct_veranstaltung_fti(self):
        fti = queryUtility(IDexterityFTI, name='Veranstaltung')
        self.assertTrue(fti)

    def test_ct_veranstaltung_factory(self):
        fti = queryUtility(IDexterityFTI, name='Veranstaltung')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IVeranstaltung.providedBy(obj),
            u'IVeranstaltung not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_veranstaltung_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='Veranstaltung',
            id='veranstaltung',
        )

        self.assertTrue(
            IVeranstaltung.providedBy(obj),
            u'IVeranstaltung not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('veranstaltung', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('veranstaltung', parent.objectIds())

    def test_ct_veranstaltung_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Veranstaltung')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_veranstaltung_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Veranstaltung')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'veranstaltung_id',
            title='Veranstaltung container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
