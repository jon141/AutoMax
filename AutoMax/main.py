import time
import socket
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import *

import threading
from datetime import datetime
from mail import sent_mail
from relevante_auftraege import get_auftraege_nach_wochen

def sent_mail_threaded(fromMail, passwort, smtp_server, smtp_port, toMail, subject, message, bcc):
    wait_for_internet()
    thread = threading.Thread(target=sent_mail, args=(fromMail, passwort, smtp_server, smtp_port, toMail, subject, message, bcc))
    thread.start()



with open('config.json', 'r', encoding='utf-8') as file:
    configurations = json.load(file)  # config daten laden

system = configurations['os']

# Headless Chrome konfigurieren
options = Options()
#options.add_argument("--headless") # wenn aktiviert läuft es im Hintergrund
#options.add_argument("--no-sandbox") # wenn aktiviert läuft es im Hintergrund
#options.add_argument("--disable-dev-shm-usage") # wenn aktiviert läuft es im Hintergrund


if system == 'linux':
    # WebDriver starten
    driver = webdriver.Chrome(options=options)
else:
    # WebDriver starten
    service = Service(executable_path=r'C:\Pfad\zum\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)


wait = WebDriverWait(driver, 10) # wartefunktion, die bis zu 10 s warten kann, ob eine aktion ausführbar ist



projekt = configurations['projekt']
einrichtung = configurations['einrichtung']
benutzername = configurations['benutzername']
passwort = configurations['passwort']


def wait_for_internet(host="8.8.8.8", port=53, timeout=3): # wenn das Skript mit crontab automatisch beim boot gestartet werden soll, ist erstmal bzw. bis zum Anmelden keine Verbindung vorhande
    while True:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            print("Internetverbindung verfügbar!")
            break
        except socket.error:
            print("Keine Internetverbindung. Neuer Versuch in 5 Sekunden...")
            time.sleep(5)


def login():
    # Seite öffnen
    driver.get('https://mensastadt.de/Login.aspx')

    # irgendwie mit js loginvariablen setzen
    driver.execute_script(f"document.getElementById('tbxProjekt').value = '{projekt}';")
    driver.execute_script(f"document.getElementById('tbxEinrichtung').value = '{einrichtung}';")
    driver.execute_script(f"document.getElementById('tbxBenutzername').value = '{benutzername}';")
    driver.execute_script(f"document.getElementById('tbxKennwort').value = '{passwort}';")

    # Events manuell auslösen (wichtig!) # keine Ahnung was hier passiert, aber funktioniert
    for field_id in ["tbxProjekt", "tbxEinrichtung", "tbxBenutzername", "tbxKennwort"]:
        driver.execute_script(f"""
            let e = new Event('input', {{ bubbles: true }});
            document.getElementById('{field_id}').dispatchEvent(e);
        """)

    # login mit drücken des Button abschließen
    login_button = driver.find_element("id", "btnLogin")
    login_button.click()
    print('login')
    time.sleep(1) # ladezeit




def essensseite_laden(): # funktioniert
    # In den "navigationFrame" wechseln
    driver.switch_to.default_content()
    driver.switch_to.frame("navigationFrame")

    # 1. Klick auf "Essensbestellung"
    essensbestellung_div = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[text()='Essensbestellung']"))
    )
    essensbestellung_div.click()

    # 2. Nur das td-Element klicken, das direkt unter "Essensbestellung" steht
    essen_bestellen_td = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[text()='Essensbestellung']/following::td[normalize-space()='Essen bestellen / stornieren'][1]"
        ))
    )
    essen_bestellen_td.click()

    # 3. In den contentFrame wechseln
    driver.switch_to.default_content()
    driver.switch_to.frame("contentFrame")
    time.sleep(5)



def wochenansicht_auslesen():
    driver.switch_to.default_content() # gibt anscheinend mehrere Frames, im content Frame ist die Essensbestellung
    driver.switch_to.frame("contentFrame")

    print("🕵️ HTML der Wochenansicht wird geladen...")
    print(driver.page_source)  # gesammter code der seite wird ausgegeben - in <li> elementen findet man alle Gerichtnamen

    # das darunter funktioniert nicht so richtig, es wird nur Tomate Mozarella Rap ausgegeben
    tage = driver.find_elements(By.XPATH, "//td[contains(text(), 'Mo') or contains(text(), 'Di') or contains(text(), 'Mi') or contains(text(), 'Do') or contains(text(), 'Fr')]")
    for tag in tage:
        print("📅", tag.text)


def aktuelle_wochenposition_auslesen():
    driver.switch_to.default_content()
    driver.switch_to.frame("contentFrame")  # sicherstellen, dass du im richtigen Frame bist

    span_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "lblWoche"))
    )
    woche_text = span_element.text
    print("Angezeigete Woche:", woche_text)
    return woche_text



def woche_vor(): # im plan eine Woche weiter gehen
    print('woche_vor()')
    vor_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btnVor"))
    )
    vor_button.click()
    time.sleep(5)

def woche_zurueck(): # im plan eine Woche zurück gehen

    print('woche_zurück()')
    zurueck_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "btnZurueck"))
    )
    zurueck_button.click()
    time.sleep(5)


def pruefe_ist_bestellt(datum: str, essens_id: str) -> bool:
    td_id = f"td{datum}_{essens_id}"
    print('prüfe ob bestellt: ', datum, td_id)

    div_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, td_id))
    )

    select_element = div_element.find_element(By.TAG_NAME, "select") # die combobox im div

    # Aktuell ausgewählten Wert holen
    value = select_element.get_attribute("value")

    print(f"Aktueller Value: {value}")

    return value != "0" # wenn value ungleich 0 ist, ist es bestellt



def essen_bestellen_abbestellen(datum: str, essens_id: str): # bestellt essen einmal, oder bestellt es ab, wenn es schon bestellt wurde
    # ID des <td> ist "td{date}_{essens_id}"
    td_id = f"td{datum}_{essens_id}"
    print('vor wait')
    # Warte, bis das Element klickbar ist
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, td_id))
    ) # die Funktion wird ausgeführt, weil das wait nicht abgewartet wird, aber es wird kein essen bestellt

    print(element)
    print('---------------------')
    print(element.text)

    

    essensname = element.text.split('\n')[0].split('(')[0]
    print('essensname:-----', essensname)

    print('nach wait')
    # Klicke das <td> (löst showBitteWarten() und addMenu() aus)
    #element.click()

    xpath = f"//td[@id='td{datum}_{essens_id}']//ul"
    print(xpath)
    #print(xpath.text)
    bestell_click_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, xpath))
    )
    driver.execute_script("arguments[0].click();", bestell_click_element) # funktionniert, aber man muss halt erst die richtige bestell id finden, sonst geht es nicht un din der richtigen woche sein

    bestellung = {'date': datum, 'essensid': essens_id, 'essensname': essensname}

    return bestellung
#

#testbestellung = essen_bestellen()
print(5*'\n')
#print(testbestellung)


alle_gerichtnamen = ['Menü1', 'Menü2', 'Saiten, 1 Paar', 'LKW', 'Schnitzelweck (vegan)', 'Schnitzelweck (Schwein)', 'Schnitzelweck (Geflügel)', 'Maultaschen', 'Maultaschen VEGAN', 'Großer Salatteller VEGAN', 'Kleiner Salat VEGAN', 'Kartoffelsalat VEGAN', 'Wrap Hühnchen', 'Wrap Tomate/Mozzarella', 'Wrap Schinken/Käse', 'Wrap Hummus/Gemüse VEGAN', 'z. Zt. nicht bestellbar Pizzaschnitte vegetarisch', 'Pizzaschnitte Salami', 'z. Zt. nicht bestellbar Pizzaschnitte Schinken',]



def finde_essensid_für_gerichte_an_datum(datum: str, gerichtnamen: list):
    driver.switch_to.default_content()
    driver.switch_to.frame("contentFrame")

    # Alle td-Elemente mit ID, die zum Datum passt
    td_elements = driver.find_elements(By.XPATH, f"//td[starts-with(@id, 'td{datum}_')]")

    essen_liste = []
    for td in td_elements:
        td_id = td.get_attribute("id")
        essens_id = td_id.split('_')[1]

        # Nur den Namen rausholen – das ist immer im ersten <li>
        try:
            name_element = td.find_element(By.XPATH, ".//li[1]")
            name = name_element.text.strip()
        except:
            name = "[kein Name gefunden]"

        essen_liste.append((essens_id, name))

    print(f"🍽 Essen am {datum}:")

    essen_id_bestell_liste = [datum]

    for index, (eid, name) in enumerate(essen_liste):

        if index == 0 and 'Menü1' in gerichtnamen:
            #essensid = eid
            print('gericht detected: ', eid)
            essen_id_bestell_liste.append(eid)

        elif index == 1 and 'Menü2' in gerichtnamen:
            #essensid = eid
            print('gericht detected: ', eid)
            essen_id_bestell_liste.append(eid)

        elif name in gerichtnamen:
            #essensid = eid
            print('gericht detected: ', eid)
            essen_id_bestell_liste.append(eid)

        print(f"  - ID: {eid} | {name}")

    
    return essen_id_bestell_liste


relevante_auftraege = get_auftraege_nach_wochen()
for i in range(3):
    last_key = list(relevante_auftraege.keys())[-1]
    if relevante_auftraege[last_key] == {}:
        del relevante_auftraege[last_key]
    else:
        break
print('relevante aufträge:', relevante_auftraege)

# bestelllogik
# auf internet warten und einloggen, seite laden
if relevante_auftraege != {}:
    wait_for_internet() 
    login()
    essensseite_laden()

    logs_bestellungen = []

    for woche in relevante_auftraege:
        #aktuelle_wochenposition_auslesen()
        print('Woche:', aktuelle_wochenposition_auslesen())
        for auftrag in relevante_auftraege[woche]:
            auftragsdaten = relevante_auftraege[woche][auftrag]

            auftragsdatum = auftragsdaten['datum']
            gerichtnamen = auftragsdaten['gerichte']

            essens_ids_von_auftrag = finde_essensid_für_gerichte_an_datum(datum=auftragsdatum, gerichtnamen=gerichtnamen)

            sicher_bestellt = True

            for id in essens_ids_von_auftrag:
                try: 
                    if pruefe_ist_bestellt(datum=auftragsdatum, essens_id=id):
                        print(f"{auftrag} {id} am {auftragsdatum} bereits bestellt.")
                    else:
                        bestellung = essen_bestellen_abbestellen(datum=auftragsdatum, essens_id=id)
                        print(f"{auftrag} {id} am {auftragsdatum} bestellt: {bestellung}")

                        if pruefe_ist_bestellt(datum=auftragsdatum, essens_id=id): # quelle vom fehler, aber versteh ich nicht
                            print('bestellung erfolgreich')

                            with open('auftraege.json', 'r', encoding='utf-8') as file:
                                auftraege_dict = json.load(file)  # config daten laden

                            auftrag_typ = 'einzelauftraege' if auftragsdaten['einzelauftrag'] else 'dauerauftraege'
                            auftrag_name = auftrag.split('_._')[0]
                            
                            if auftrag_typ == 'einzelauftraege':
                                auftraege_dict[auftrag_typ][auftrag_name]['done'] = True
                            elif auftrag_typ == 'dauerauftraege':
                                auftraege_dict[auftrag_typ][auftrag_name]['done_dates'].append(auftragsdatum)

                            
                            with open('auftraege.json', 'w', encoding='utf-8') as f:
                                json.dump(auftraege_dict, f, ensure_ascii=False, indent=4)

                            print('aufträge.json aktualisiert c1')
                            
                            mail_log = [auftragsdatum, bestellung['essensname'], True]
                            logs_bestellungen.append(mail_log)


                        else: # essen konnte nicht bestellt werden
                            print('bestellung nicht erfolgreich')
                            sicher_bestellt = False # fallback aktivieren
                            mail_log = [auftragsdatum, bestellung['essensname'], False]
                            logs_bestellungen.append(mail_log)


                except Exception as e:
                    print('Fehler bei der Bestellung:', e)
                    if "Message:" in str(e):
                        print('FEhler, der leider immer kommt und ignoriert werden kann.')
                    else:
                        sicher_bestellt = False # fallback aktivieren
                        logs_bestellungen.append([auftragsdatum, f'Fehler (exeption: {e})', False])

            
            if not sicher_bestellt: # fallback # das gleiche nochmal mit fallback gerichten
                try:

                    essens_ids_von_fallback = finde_essensid_für_gerichte_an_datum(datum=auftragsdatum, gerichtnamen=auftragsdaten['fallback'])
                    for id in essens_ids_von_fallback:
                        if pruefe_ist_bestellt(datum=auftragsdatum, essens_id=id):
                            print(f"{auftrag} {id} am {auftragsdatum} bereits bestellt.")
                        else:
                            bestellung = essen_bestellen_abbestellen(datum=auftragsdatum, essens_id=id)
                            print(f"{auftrag} {id} am {auftragsdatum} bestellt: {bestellung}")

                            if pruefe_ist_bestellt(datum=auftragsdatum, essens_id=id):
                                print('bestellung erfolgreich')

                                with open('auftraege.json', 'r', encoding='utf-8') as file:
                                    auftraege_dict = json.load(file)  # config daten laden

                                auftrag_typ = 'einzelauftraege' if auftragsdaten['einzelauftrag'] else 'dauerauftraege'
                                auftrag_name = auftrag.split('_._')[0]
                                
                                if auftrag_typ == 'einzelauftraege':
                                    auftraege_dict[auftrag_typ][auftrag_name]['done'] = True
                                elif auftrag_typ == 'dauerauftraege':
                                    auftraege_dict[auftrag_typ][auftrag_name]['done_dates'].append(auftragsdatum)
                                

                                with open('auftraege.json', 'w', encoding='utf-8') as f:
                                    json.dump(auftraege_dict, f, ensure_ascii=False, indent=4)

                                print('aufträge.json aktualisiert c2')


                                mail_log = [auftragsdatum, bestellung['essensname'], True]
                                logs_bestellungen.append(mail_log)


                            else: # essen konnte nicht bestellt werden
                                print('bestellung nicht erfolgreich')
                                mail_log = [auftragsdatum, bestellung['essensname'], False]
                
            
                except Exception as e:
                    if "Message:" in str(e):
                        print('FEhler, der leider immer kommt und ignoriert werden kann.')
                    else:
                        print('Fehler bei der Fallback-Bestellung:', e)
                        mail_log = [auftragsdatum, f'Fallback (Exeption: {e})', False]
                        logs_bestellungen.append(mail_log)

                    time.sleep(5)  # kurze Pause 
        if woche != len(relevante_auftraege) - 1:
            woche_vor()

    # mail senden 

    #sent_mail(fromMail, passwort, smtp_server, smtp_port, toMail, subject, message, bcc):
    fromMail = configurations['fromMail']
    passwort = configurations['MailPasswort']
    smtp_server = configurations['smtp_server']
    smtp_port = configurations['smtp_port']
    toMail = configurations['toMail']

    now = datetime.now()
    formatted = now.strftime("%d.%m.%Y %H:%M:%S")

    subject = f'Bestellbereicht: Automatische Bestellung von {formatted}'
    bcc = False



    message = 'Bestellbericht:\n\n'

    for log in logs_bestellungen:
        print('log:', log)
        datum, essensname, status = log
        message += f'Essen "{essensname}" für {datum} - {"bestellt" if status else "fehlgeschlagen"}\n\n'

    try:
        sent_mail_threaded(fromMail, passwort, smtp_server, smtp_port, toMail, subject, message, bcc)
    except Exception as e:
        print('Fehler beim Senden der Mail:', e)
        print('Mailinhalt:', message)
        
                    

input('Beenden.')
driver.quit()
