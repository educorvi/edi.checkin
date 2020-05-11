from plone import api as ploneapi

def send_invitation(veranstaltung, event):

    if veranstaltung.invitation:

        subject = u'Einladung zum Checkin für: {0}'.format(veranstaltung.title)
        message = u"""\
Bitte checken Sie für die Veranstaltung mit dem folgenden Link ein: 

{0}

Bitte beachten Sie, dass Sie erst am Veranstaltungstag einchecken können.
""".format(veranstaltung.absolute_url())

        sender = ploneapi.portal.get_registry_record('plone.email_from_address')

        import pdb;pdb.set_trace()

        for i in veranstaltung.adressen:
            ploneapi.portal.send_email(
                recipient=i,
                sender=sender,
                subject=subject,
                body=message,
            )
