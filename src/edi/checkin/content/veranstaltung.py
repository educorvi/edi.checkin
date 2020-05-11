# -*- coding: utf-8 -*-
import datetime
from plone.dexterity.content import Container
from plone.supermodel import model
from z3c.form import validator
from zope import schema
import zope.component
from zope.interface import implementer
from zope.interface import invariant, Invalid
from edi.checkin.content.office import validate_adressen

from edi.checkin import _

class IVeranstaltung(model.Schema):
    """ Marker interface and Dexterity Python Schema for Veranstaltung
    """
    start = schema.Datetime(title=_(u"Beginn der Veranstaltung"), required=True)
    end = schema.Datetime(title=_(u"Ende der Veranstaltung"), required=True)

    adressen = schema.List(title=_(u"Gültige E-Mail-Adressen für diese Veranstaltung"),
                           description=_(u"Hier legen Sie fest, welche Adressen für diese Veranstaltung einchecken dürfen."),
                           value_type=schema.TextLine(),
                           constraint = validate_adressen,
                           required=True)

    invitation = schema.Bool(title=_(u"Checkin Einladungen versenden"),
                             description=_(u"Bei Markierung dieses Feldes werden die Einladungen mit dem Link zum Checkin automatisch\
                             versendet."))

    @invariant
    def start_before_end(data):
        if data.start > data.end:
            raise Invalid(_(u'Der Beginn der Veranstaltung muss vor dem Ende liegen.'))

    @invariant
    def same_day(data):
        if data.start.date() != data.end.date():
            raise Invalid(_(u'Veranstaltungsbeginn und Veranstaltungsende müssen am gleichen Tag liegen.'))


class AdressenValidator(validator.SimpleFieldValidator):
    """
    """

    def validate(self, value):
        """
        """
        super(AdressenValidator, self).validate(value)
 
        if len(value) > self.context.maxperson:
            raise Invalid(_(u'Die Anzahl der eingetragenen Adressen überschreitet die maximale Anzahl von Personen für diesen Raum.'))


class StartValidator(validator.SimpleFieldValidator):
    """
    """

    def validate(self, value):
        """
        """
        super(StartValidator, self).validate(value)

        room_start = self.context.beginn.split(':')
        room_time_start = datetime.time(int(room_start[0]), int(room_start[1]))
        if value.time() < room_time_start:
            raise Invalid(_(u'Der Beginn der Veranstaltung darf nicht vor Öffnung des Raumes liegen.'))


class EndValidator(validator.SimpleFieldValidator):
    """
    """

    def validate(self, value):
        """
        """
        super(EndValidator, self).validate(value)

        room_end = self.context.ende.split(':')
        room_time_end = datetime.time(int(room_end[0]), int(room_end[1]))
        if value.time() > room_time_end:
            raise Invalid(_(u'Dad Ende der Veranstaltung darf nicht nach Schließung des Raumes liegen.'))


adressen = validator.WidgetValidatorDiscriminators(
    AdressenValidator,
    field=IVeranstaltung['adressen']
    )

start = validator.WidgetValidatorDiscriminators(
    StartValidator,
    field=IVeranstaltung['start']
    )

end = validator.WidgetValidatorDiscriminators(
    EndValidator,
    field=IVeranstaltung['end']
    )


zope.component.provideAdapter(AdressenValidator)
zope.component.provideAdapter(StartValidator)
zope.component.provideAdapter(EndValidator)


@implementer(IVeranstaltung)
class Veranstaltung(Container):
    """
    """
