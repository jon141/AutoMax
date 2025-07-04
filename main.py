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

#wait_for_internet() # immer vor start ausführen, evtl. bevor essen bestellt wird um fehler zu vermeiden (erstmal optional)



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

#login()



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

#essensseite_laden()
#essensseite_debug()
# Beenden


def wochenansicht_auslesen():
    driver.switch_to.default_content() # gibt anscheinend mehrere Frames, im content Frame ist die Essensbestellung
    driver.switch_to.frame("contentFrame")

    print("🕵️ HTML der Wochenansicht wird geladen...")
    print(driver.page_source)  # gesammter code der seite wird ausgegeben - in <li> elementen findet man alle Gerichtnamen

    # das darunter funktioniert nicht so richtig, es wird nur Tomate Mozarella Rap ausgegeben
    tage = driver.find_elements(By.XPATH, "//td[contains(text(), 'Mo') or contains(text(), 'Di') or contains(text(), 'Mi') or contains(text(), 'Do') or contains(text(), 'Fr')]")
    for tag in tage:
        print("📅", tag.text)

    # vielleicht muss man gar nix klicken lassen, sondern direkt über js: (alles aus driver.page_source)
    # <td valign="top" title="Bestellen" alt="Bestellen" onclick="showBitteWarten();addMenu(this, 20250627,19010, '', '1');" colspan="3" style="cursor:pointer;"><ul>
    # mit der addMenu() Funktion
    # es gibt <td id="td20250627_19010" class="speiseplan-menue" style="height: 215px;"><table cellpadding="1" border="0" style="height:100%;width:100%;border-collapse:collapse;padding:0px;"> irgendwo
    # wobei die id id="td20250627_19010" das zusammengesetzt ist, was in addMenu(this, 20250627,19010, '', '1') angegeben wird
    # also müsste man nur die Zuordnung von Menü und Menünummmer für den Tag in der Woche finden und js ausführen
    # erster Teil der ID ist das Datum an dem Tag id="td20250627_19010"
    # villeicht ist der 2. teil der ID auch immer Gleich, das wäre am einfachsten
    # ist leider nicht so: aber Pittaschnitten vegetatisch in einer woche zählen so hoch: 19006 - 19010
    # also richtigen Tag mit id finden, richtiges menü müssen wir noch schauen

#wochenansicht_auslesen()

def aktuelle_wochenposition_auslesen():
    driver.switch_to.default_content()
    driver.switch_to.frame("contentFrame")  # sicherstellen, dass du im richtigen Frame bist

    span_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "lblWoche"))
    )
    woche_text = span_element.text
    print("ANgezeigete Woche:", woche_text)
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



def essen_bestellen_ne(): # funktionniert nicht
    driver.switch_to.default_content() # gibt anscheinend mehrere Frames, im content Frame ist die Essensbestellung
    driver.switch_to.frame("contentFrame")

    print('essen_bestellen( )')
    date = '20250710' 
    essens_id = '20017'
    js = f"addMenu(this, {date},{essens_id}, '', '1');"
    js = f"addMenu(null, {date},{essens_id}, '', '1');"

    driver.execute_script(js)
    print('js executed')

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

wait_for_internet()
login()
essensseite_laden()
aktuelle_wochenposition_auslesen()
woche_vor()
aktuelle_wochenposition_auslesen()
#woche_vor()
datum_ = '20250710'
gerichtnamen = ['Menü1', 'Menü2', 'Saiten, 1 Paar', 'Maultaschen']

essensids_für_daten = finde_essensid_für_gerichte_an_datum(datum=datum_, gerichtnamen=gerichtnamen)

datum = essensids_für_daten[0]
essens_ids = essensids_für_daten[1:]
print(datum)
print(essens_ids)

bestellungen = []
for id in essens_ids:
    bestellung = essen_bestellen_abbestellen(datum=datum, essens_id=id)
    bestellungen.append(bestellung)
    time.sleep(5)

print(bestellungen)




input('Beenden.')
driver.quit()







