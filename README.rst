===========
edi.checkin
===========

@Ideen von Holger Zingsheim

Mit diesem Plone Add-On kann der Zutritt zu Büros, Besprechungs- oder Veranstaltungsräumen mittels Check-In Verfahren geregelt werden.
Das Add-On wurde entwickelt, um umsichtige, verantwortungsvolle und individuelle Lösungen zur Sicherstellung des Infektionsschutzes im 
Zuge der Corona [COVID-19] Pandemie zu ermöglichen.

Eine Person, die das Checkin Verfahren nutzt, macht folgende Angaben:

1. Die eigene E-Mail-Adresse
2. Eine Bestätigung, dass die aktuell gültigen Regelungen zum Infektionsschutz (im jeweiligen Bundesland) befolgt wurden.
3. Eine Bestätigung der persönlichen Gesundheit und Fitness, Fieber oder trockener Husten wird explizit ausgeschlossen. 

Für den entsprechenden Raum können folgende Dinge festgelegt werden:

- Name des Raumes
- Maximale Besetzung des Raumes
- Maximale Aufenthaltsdauer einer Person im Raum
- Festlegung der Arbeitszeiten (Bürozeiten) in dem betreffenden Raum
- optional: Festlegung bzw. Identifikation der für den betreffenden Raum zugelassenen Personen mittels E-Mail-Adresse

Features
--------

- Inhaltstyp "Office" = Container
- Inhaltstyp "Checkin" = Item (können nur im Inhaltstyp Office angelegt werden)
- Formular für den Checkin als Standardansicht des Inhaltstyps Office
- View zur Bestätigung des Checkins bzw. zur Ablehnung des Zutritts zum Office
- E-Mail mit Check-In Card incl. QR-Code zur Online-Prüfung der Gültigkeit 
- E-Mail mit Bescheid bei Ablehnung des Zutritts
- Online-Verfahren zur Gültigkeitsprüfung des QR-Codes
- Durch Speicherung der "Checkin" Objekte im Ordner "Office" können nachträglich mögliche Infektionsketten zurückverfolgt werden

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
