# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


from edi.checkin import _


class IOffice(model.Schema):
    """ Marker interface and Dexterity Python Schema for Office
    """

    notification_mail = schema.TextLine(title=_(u"E-Mail-Adresse für Benachrichtigungen über fehlgeschlagene Checkins"),
                                        required=True)

    adressen = schema.List(title=_(u"Gültige E-Mail-Adressen für diesen Raum"),
                           description=_(u"Hier legen Sie fest, welche Adressen für diesen Raum einchecken dürfen. Wenn hier keine\
                                         Adressen eingetragen wurden findet auch keine Überprüfung der Adressen statt."),
                           value_type=schema.TextLine(),
                           required=False)

    beginn = schema.TextLine(title=_(u"Frühester Zutritt zu diesem Raum (Format: HH:MM)"),
                             required=True)

    ende = schema.TextLine(title=_(u"Späteste Schließung des Raumes (Format: HH:MM)"),
                           required=True)

    maxtime = schema.Int(title=_(u"Maximale Aufenthaltsdauer pro Person in diesem Raum"),
                         description=_(u"Angaben von 1-24 werden als Stunden, darüber hinaus als Minuten interpretiert."),
                         required=True)

    maxperson = schema.Int(title=_(u"Maximale Anzahl von Personen in diesem Raum"),
                           required=True)

    overtime = schema.Int(title=_(u"Zeitzugabe in Minuten für Raumwechsel, Verspätungen und Verzögerungen"),
                          description=_(u"Die Zeitzugabe wird nur bei den internen Berechnungen zur maximalen Raumbesetzung verwendet.\
                          Die Angabe von 0 heisst: keine Zeitzugabe."),
                          default=0,
                          required=True)

    wunschzeit = schema.Bool(title=_(u"Das Feld markieren, wenn die Person eine Wunschzeit auswählen soll"),
                          description=_(u"Die Wunschzeit wird innerhalb der Raumöffnungszeit in 15 Minuten Schritten zur Auswahl angeboten.")) 


@implementer(IOffice)
class Office(Container):
    """
    """
