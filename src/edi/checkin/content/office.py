# -*- coding: utf-8 -*-
import re
from plone.dexterity.content import Container
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zope.interface import Invalid

from edi.checkin import _

def validate_email(value):
    regex = re.compile('^.+@.+\.[^.]{2,}$')
    if not regex.match(value):
        raise Invalid(_(u'Bitte geben Sie eine korrekte E-Mail-Adresse an.'))
    return True
        
def validate_adressen(value):
    regex = re.compile('^.+@.+\.[^.]{2,}$')
    for i in value:
        if not regex.match(i):
            raise Invalid(_(u'%s ist keine korrekte E-Mail-Adresse' %i))
    return True

def validate_zeit(value):
    regex = re.compile('^([01]?\d|2[0-3]):([0-5]?\d)$')
    if not regex.match(value):
        raise Invalid(_(u'Bitte geben Sie ein korrektes Format für die Uhrzeit an (HH:MM)'))
    return True

def validate_maxtime(value):
    if value == 0:
        raise Invalid(_(u'Eine Angabe von 0 Stunden ergibt in diesem Kontext keinen Sinn. Bitte korrigieren.'))
    return True

class IOffice(model.Schema):
    """ Marker interface and Dexterity Python Schema for Office
    """

    notification_mail = schema.TextLine(title=_(u"E-Mail-Adresse für Benachrichtigungen über fehlgeschlagene Checkins"),
                                        constraint = validate_email,
                                        required=True)

    adressen = schema.List(title=_(u"Gültige E-Mail-Adressen für diesen Raum"),
                           description=_(u"Hier legen Sie fest, welche Adressen für diesen Raum einchecken dürfen. Wenn hier keine\
                                         Adressen eingetragen wurden findet auch keine Überprüfung der Adressen statt."),
                           value_type=schema.TextLine(),
                           constraint = validate_adressen, 
                           required=False)

    beginn = schema.TextLine(title=_(u"Frühester Zutritt zu diesem Raum (Format: HH:MM)"),
                             constraint = validate_zeit,
                             required=True)

    ende = schema.TextLine(title=_(u"Späteste Schließung des Raumes (Format: HH:MM)"),
                           constraint = validate_zeit,
                           required=True)

    maxtime = schema.Int(title=_(u"Maximale Aufenthaltsdauer pro Person in diesem Raum"),
                         description=_(u"Angaben von 1-24 werden als Stunden, darüber hinaus als Minuten interpretiert."),
                         constraint = validate_maxtime,
                         required=True)

    maxperson = schema.Int(title=_(u"Maximale Anzahl von Personen in diesem Raum"),
                           required=True)

    overtime = schema.Int(title=_(u"Zeitzugabe in Minuten für Raumwechsel, Verspätungen und Verzögerungen"),
                          description=_(u"Die Zeitzugabe wird nur bei den internen Berechnungen zur maximalen Raumbesetzung verwendet.\
                          Die Angabe von 0 heisst: keine Zeitzugabe."),
                          default=0,
                          required=True)


@implementer(IOffice)
class Office(Container):
    """
    """
