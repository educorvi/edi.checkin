# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer

from edi.checkin import _

class IVeranstaltung(model.Schema):
    """ Marker interface and Dexterity Python Schema for Veranstaltung
    """
    start = schema.Datetime(title=_(u"Beginn der Veranstaltung"), required=True)
    end = schema.Datetime(title=_(u"Ende der Veranstaltung"), required=True)

    adressen = schema.List(title=_(u"Gültige E-Mail-Adressen für diese Veranstaltung"),
                           description=_(u"Hier legen Sie fest, welche Adressen für diese Veranstaltung einchecken dürfen."),
                           value_type=schema.TextLine(),
                           required=True)

    invitation = schema.Bool(title=_(u"Checkin Einladungen versenden"),
                             description=_(u"Bei Markierung dieses Feldes werden die Einladungen mit dem Link zum Checkin automatisch\
                             versendet."))


@implementer(IVeranstaltung)
class Veranstaltung(Container):
    """
    """
