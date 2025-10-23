import json


from datetime import datetime, date, timedelta


def datum_in_zwei_wochen_bis_freitag():
    heute = date.today()
    in_zwei_wochen = heute + timedelta(days=14)
    wochentag = in_zwei_wochen.weekday()

    # Bis Freitag auffüllen
    tage_bis_freitag = 4 - wochentag
    izw = in_zwei_wochen + timedelta(days=tage_bis_freitag)

    return izw.strftime("%Y%m%d")

datum_heute = date.today().strftime("%Y%m%d")
datum_in_zwei_Wochen = datum_in_zwei_wochen_bis_freitag()


def datum_zwischen(test_datum: str, start: str, ende: str) -> bool:
    """Prüft, ob test_datum zwischen start und ende (inklusive) liegt."""
    fmt = "%Y%m%d"  # Datumsformat wie 20251022

    test = datetime.strptime(test_datum, fmt)
    start_d = datetime.strptime(start, fmt)
    ende_d = datetime.strptime(ende, fmt)

    return start_d <= test <= ende_d


from datetime import date, datetime

def wochen_offset(datum_str: str) -> int:
    """Gibt zurück, ob das Datum in der 0., 1. oder 2. Woche (ab heute) liegt."""
    fmt = "%Y%m%d"
    heute = date.today()
    datum = datetime.strptime(datum_str, fmt).date()

    # Montag dieser Woche finden (damit Wochen sauber starten)
    wochenstart = heute - timedelta(days=heute.weekday())

    # Differenz in Tagen
    diff = (datum - wochenstart).days

    # Wochennummer relativ zu dieser Woche
    if diff < 0:
        return -1  # liegt in der Vergangenheit
    else:
        return diff // 7  # 0 = diese Woche, 1 = nächste, 2 = übernächste

print(wochen_offset("20251107"))  # Beispielaufruf


def ist_datum_in_vergangenheit(datum_str: str) -> bool:
    """Prüft, ob das Datum in der Vergangenheit liegt (vor heute)."""
    fmt = "%Y%m%d"
    heute = date.today()
    datum = datetime.strptime(datum_str, fmt).date()

    return datum < heute

from datetime import date, timedelta, datetime

def daten_fuer_wochentag(wochentag: str, max_offset: int = 2):
    """
    Gibt alle zukünftigen Daten (YYYYMMDD) für den gegebenen Wochentag zurück,
    die innerhalb der nächsten 'max_offset'-Wochen liegen.
    
    wochentag: z. B. 'Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So'
    """
    tage = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    ziel_index = tage.index(wochentag)
    heute = date.today()

    # Montag dieser Woche finden
    wochenstart = heute - timedelta(days=heute.weekday())

    ergebnisse = []
    for woche in range(max_offset + 1):
        tag = wochenstart + timedelta(weeks=woche, days=ziel_index)
        if tag >= heute:
            ergebnisse.append(tag.strftime("%Y%m%d"))
    
    return ergebnisse


def get_auftraege_nach_wochen():


    with open('auftraege.json', 'r', encoding='utf-8') as file:
        auftraege_dict = json.load(file)  #  laden


    auftraege_nach_wochen_dict = {0: {}, 1: {}, 2: {}}
    # dann immer datum, gerichte, fallback, name (wegen falsesetzung von done)


    einzelauftraege = auftraege_dict['einzelauftraege']
    dauerauftraege = auftraege_dict['dauerauftraege']

    datum_heute = date.today().strftime("%Y%m%d")

    for auftrag in einzelauftraege: # auftrag gibt name des aufgrags zurück
        if einzelauftraege[auftrag]['aktiv'] and not einzelauftraege[auftrag]['done']: # muss aktiv sein und nicht erledigt
            datum_auftrag = einzelauftraege[auftrag]['datum']
            wochen_offset_v_auftrag = wochen_offset(datum_auftrag)
            if wochen_offset_v_auftrag in [0, 1, 2] and not ist_datum_in_vergangenheit(datum_auftrag): # diese nächste, oder übernächste woche (weiter kann man nicht bestellen)
                auftraege_nach_wochen_dict[wochen_offset_v_auftrag][f'{auftrag}_._{datum_auftrag}_e'] = {"datum": datum_auftrag,
                                                                            "gerichte": einzelauftraege[auftrag]['gerichte'],
                                                                            "fallback": einzelauftraege[auftrag]['fallback'],
                                                                            "einzelauftrag": True,}
                print('muss ausgeführt werden', datum_auftrag)

    print(auftraege_nach_wochen_dict)

    for auftrag in dauerauftraege: # auftrag gibt name des aufgrags zurück
        if dauerauftraege[auftrag]['aktiv']: # muss aktiv sein

            start_datum = dauerauftraege[auftrag]['gueltigszeitraum']['start']
            ende_datum = dauerauftraege[auftrag]['gueltigszeitraum']['ende']

            if datum_zwischen(datum_heute, start_datum, ende_datum):
                alle_auftrag_daten = []

                auftrag_exeption_dates = dauerauftraege[auftrag]['exeptions']


                for wochentag in dauerauftraege[auftrag]['wochentage']:
                    alle_auftrag_daten.extend(daten_fuer_wochentag(wochentag))
                
                for element in auftrag_exeption_dates: # daten von ausnahmen entfernen
                    if element in alle_auftrag_daten:
                        alle_auftrag_daten.remove(element)

                for datum in alle_auftrag_daten:

                    if datum not in dauerauftraege[auftrag]['done_dates']:
                        wochen_offset_v_auftrag = wochen_offset(datum)
                        auftraege_nach_wochen_dict[wochen_offset_v_auftrag][f'{auftrag}_._{datum}_d'] = {"datum": datum,
                                                                            "gerichte": dauerauftraege[auftrag]['gerichte'],
                                                                            "fallback": dauerauftraege[auftrag]['fallback'],
                                                                            "einzelauftrag": False}
    return auftraege_nach_wochen_dict

