# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope import schema
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five.browser import BrowserView

from plone.z3cform import layout
from plone.supermodel import model
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper

class ICheckinSettings(model.Schema):
    """
    """

    adminuser = schema.TextLine(title=u"Redaktioneller Benutzer zum Schreiben der Checkin-Daten")
    adminpassword = schema.Password(title=u"Passwort für redaktionellen Benutzer")

class CheckinSettingsEditForm(RegistryEditForm):
    """
    """
    schema = ICheckinSettings
    label = u"Einstellungen für edi.checkin"

CheckinSettingsView = layout.wrap_form(CheckinSettingsEditForm, ControlPanelFormWrapper)
CheckinSettingsView.label = u"Einstellungen edi.checkin"
