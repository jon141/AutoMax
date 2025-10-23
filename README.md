# AutoMax
Automatische Essensbestellung bei MensaMax mit nützlichen Features! 
...in Arbeit

- AutoMax: soweit funktionsfähig (config.json muss im Ordner sein)
- Untis: aktuell keine Verbindung und Funktion in AutoMax
- GUI: experimentelle Gui für Eventerstellung; Funktion nicht auf AutoMax abgestimmt

# Funktion von Automax
- in auftraege.json kann man Aufträge erstellen:
  - Daueraufträge:
      - an einem, oder mehr Wochentagen
      - in einem festgelegten Gültigkeitszeitraum
      - Ausnahmedaten
  - Einzelaufträge:
      - einmalige Bestellung an ausgewähltem Datum
- ein Auftrag kann mehrere Menüs enthalten
- es können Fallback Menüs eingetragen werden, die bestellt werden, wenn es zu fehlern bei der anderen Bestellung gab (Funktionstüchtigkeit ungewiss)
- Nach Abschluss aller fälligen Bestellungen wird eine Email gesendet, was bestellt wurde
