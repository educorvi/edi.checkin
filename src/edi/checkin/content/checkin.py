# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer


from edi.checkin import _


class ICheckin(model.Schema):
    """ Marker interface and Dexterity Python Schema for Checkin
    """

    start = schema.Datetime(title=_(u"Beginn der Checkin-Zeit"))
    end = schema.Datetime(title=_(u"Ende der Checkin-Zeit"))


@implementer(ICheckin)
class Checkin(Item):
    """
    """
