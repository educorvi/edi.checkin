===========
edi.checkin
===========

@frühe Ideen von Holger Zingsheim (formerly known as CologneQueueApp)

Mit diesem Plone Add-On kann der Zutritt zu Büros, Besprechungs- und Veranstaltungsräumen oder Kantinen mittels Check-In Verfahren geregelt werden.
Das Add-On wurde entwickelt, um umsichtige, verantwortungsvolle und individuelle Lösungen zur Sicherstellung des Infektionsschutzes und zur Hygiene
am Arbeitsplatz im Zuge der Corona [COVID-19] Pandemie zu ermöglichen.

Eine Person, die das Checkin Verfahren nutzt, macht folgende Angaben:

1. Die eigene E-Mail-Adresse
2. Eine Bestätigung, dass die aktuell gültigen Regelungen zum Infektionsschutz (im jeweiligen Bundesland) befolgt wurden.
3. Eine Bestätigung der persönlichen Gesundheit und Fitness, Fieber oder trockener Husten werden explizit ausgeschlossen. 

Für den entsprechenden Raum können folgende Dinge festgelegt werden:

- Name des Raumes
- E-Mail Adresse zur Mitteilung abgelehnter Checkins
- Maximale Besetzung des Raumes
- Maximale Aufenthaltsdauer einer Person im Raum
- Festlegung der Öffnungszeiten für den betreffenden Raum
- optional: Angabe einer Zeitzugabe für Verspätungen, Raumwechsel, etc.
- optional: Festlegung bzw. Identifikation der für den betreffenden Raum zugelassenen Personen mittels E-Mail-Adresse

Wird ein Raum als Besprechungsraum genutzt können in diesem Raum Artikel vom Typ "Veranstaltung" angelegt werden. Der Checkin erfolgt dann nicht
für den Raum, sondern für die Veranstaltung. Eigenschaften des Raumes werden der Veranstaltung, also z.B. dem Besprechungstermin vererbt.

Features
--------

- Inhaltstyp "Raum/Office" = Container
- Inhaltstyp "Veranstaltung" = Container (kann nur im Artikeltyp Raum/Office angelegt werden)
- Inhaltstyp "Checkin" = Item (können nur in den Artikeltypen Raum/Office und Veranstaltung angelegt werden)
- Formular für den Checkin als Standardansicht die Artikeltypen Raum/Office und Veranstaltung
- Kontrolle der Gültigkeit des Zeitraumes beim Checkin und der Einhaltung der maximalen Personenzahl
- Automatische Suche nach freien Zeiträumen für den Zugang zum Raum in 5 Minuten Schritten
- View zur Bestätigung des Checkins bzw. zur Ablehnung des Zutritts zum Raum
- E-Mail mit Check-In Pass incl. QR-Code zur Online-Prüfung der Gültigkeit 
- E-Mail mit Bescheid bei Ablehnung des Zutritts*
- Online-Verfahren zur Gültigkeitsprüfung des QR-Codes**
- Durch Speicherung der "Checkin" Objekte im Ordner "Office" können nachträglich mögliche Infektionsketten zurückverfolgt werden

Datenschutz
-----------

Bei abgelehnten Checkins erfolgt eine Benachrichtigung an die angegebene E-Mail-Adresse. In der E-Mail-Adresse wird der Grund der Ablehnung
(Regelverstoss gegen den Infektionsschutz oder aufgetretene Krankheitssymptome) nicht gespeichert.

ToDo (Coming Soon)
------------------

- Möglichkeit zur Angabe einer Wunschzeit für den Checkin
- Möglichkeit zur Stornierung von Checkins


Examples
--------

Ein Beispiel kann unter folgender URL aufgerufen werden:

https://www.educorvi.de/letrafactory


Translations
------------

Das Add-On steht momentan ausschließlich in Deutscher Sprache zur Verfügung.

Installation
------------

Installation von edi.checkin durch Hinzufügen des Add-Ons zur buildout.cfg::

    [buildout]

    ...

    eggs =
        edi.checkin


Danach Ausführung von: ``bin/buildout``


Das Add-On muss über das Plone-Controlpanel installiert werden. Danach muss im Plone-Controlpanel ein redaktioneller Benutzer angegeben werden
mit dem im Hintergrund die Checkins angelegt werden.

Contribute
----------

- Issue Tracker: https://github.com/educorvi/edi.checkin/issues
- Source Code: https://github.com/educorvi/edi.checkin


Support
-------

info@educorvi.de

License
-------

The project is licensed under the GPLv2.
