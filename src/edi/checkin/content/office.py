# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


from edi.checkin import _


class IOffice(model.Schema):
    """ Marker interface and Dexterity Python Schema for Office
    """

    adressen = schema.List(title=_(u"Gültige E-Mail-Adressen für diesen Raum"),
                           description=_(u"Hier legen Sie fest, welche Adressen für diesen Raum einchecken dürfen. Wenn hier keine\
                                         Adressen eingetragen wurden findet auch keine Überprüfung der Adressen statt."),
                           value_type=schema.TextLine(),
                           required=False)

    beginn = schema.TextLine(title=_(u"Frühester Arbeitsbeginn in diesem Office (Format: HH:MM)"),
                             required=True)

    ende = schema.TextLine(title=_(u"Spätestes Arbeitsende in diesem Office (Format: HH:MM)"),
                           required=True)

    maxtime = schema.Int(title=_(u"Maximale Aufenthaltsdauer pro Person in diesem Office (Format: H)"),
                           required=True)

    maxperson = schema.Int(title=_(u"Maximale Bürobesetzung in Personen an Arbeitstagen"),
                           required=True)


@implementer(IOffice)
class Office(Container):
    """
    """
