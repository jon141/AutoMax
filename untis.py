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
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

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
    service = Service(executable_path=r'chromedriver-win64/chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)


wait = WebDriverWait(driver, 10) # wartefunktion, die bis zu 10 s warten kann, ob eine aktion ausführbar ist
untispasswort = configurations['untispasswort']
untisbenutzername = configurations['untisbenutzername']#

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

wait_for_internet() # immer vor start ausführen, evtl. bevor essen bestellt wird um fehler zu vermeiden (erstmal optional)

def loginjoin():
    # logt sich in Join ein, aber kein Plan wie es funktioniert
    driver.get('https://cissa.webuntis.com/WebUntis/?school=JKG+Weil+der+Stadt#/basic/login')


    benutzerfeld = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((
            By.XPATH, "//input[@aria-describedby='login-form-errors' and @type='text']"
        ))
    )   
    benutzerfeld.clear()
    benutzerfeld.send_keys(untisbenutzername)  


    passwortfeld = WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((
        By.XPATH, "//input[@type='password' and @aria-describedby='login-form-errors']"
        ))
    )
    passwortfeld.clear()
    passwortfeld.send_keys(untispasswort)  
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_button.click() 
    print('login')
    time.sleep(2)
    stundenplan_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@class='item-name' and text()='Mein Stundenplan']"))
    )
    stundenplan_button.click()
loginjoin() 



def existierende_stunden_zu_uhrzeit(uhrzeit):
    print("gestartet")
    time.sleep(3)  # Warte auf das Laden der Seite

    # 1. Top-Koordinate des Zeitelements uhrzeit finden
    zeit_top = None
    elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'timetable-grid-slot-time')]")
    for el in elements:
        try:
            span = el.find_element(By.XPATH, ".//span[contains(@class, 'timetable-grid-slot-time--time-value')]")
            if span.text.strip() == uhrzeit:
                style = el.get_attribute("style")
                if "top:" in style:
                    zeit_top = float(style.split("top:")[1].split("px")[0].strip())
                    print(f"Top-Koordinate für {uhrzeit}: {zeit_top}")
                    break
        except:
            continue

    if zeit_top is None:
        print(f"Zeitfeld {uhrzeit} nicht gefunden.")
        return

    # 2. Alle Karten prüfen, ob sie die Zeit-Koordinate abdecken
    idx = 0
    count = 0
    while True:
        karten = driver.find_elements(By.XPATH, "//div[contains(@class, 'timetable-grid-card')]")
        if idx >= len(karten):
            break
        karte = karten[idx]
        style = karte.get_attribute("style")
        try:
            top = float(style.split("top:")[1].split("px")[0].strip())
            height = float(style.split("height:")[1].split("px")[0].strip())
            if top <= zeit_top <= top + height:
                count += 1
                lesson_card = karte.find_element(By.CLASS_NAME, "lesson-card")
                lesson_classes = lesson_card.get_attribute("class")

                if "cancelled" in lesson_classes:
                    print('entfall')
                    print(karte.text)
                    #print(karte.get_attribute("innerHTML"))
                    lesson_card.click()
                    kartenurl = driver.current_url
                    #print(kartenurl)
                    url_segmente = kartenurl.split('/')
                    #print(url_segmente)
                    print(url_segmente[9]) # gibt das Datum der stunde an
                    driver.back()
                    time.sleep(1)  
                    # Nach dem Zurückgehen: Karten neu suchen und an der richtigen Stelle weitermachen
                    idx += 1
                    continue
        except Exception:
            pass
        idx += 1
    print(f"Karten auf Höhe {uhrzeit}: {count}")
zeiten = ["07:40", "08:25", "09:10", "09:30", "10:15", "10:20", "11:05", "11:15", "12:00", "12:05", "12:50", "13:45", "14:30", "14:35", "15:20", "15:30", "16:15", "16:20", "17:05"]
# man braucht wahrscheinlihc nicht alle zeiten, aber mal zum testen

#for e in zeiten:
#    print(f'-------------------------{e}--------------------------')
#    existierende_stunden_zu_uhrzeit(e)

existierende_stunden_zu_uhrzeit('14:35')

# 8:25 und 9:10 und 9:30 -> 1.2. STunde
# 10:15 und 10:20 und 11:05 -> 3.4
#"12:00", "12:05", "12:50", "13:45" -> 5.6
# "14:30", "14:35", "15:20", "15:30" -> 7.8.
#"16:15", "16:20", "17:05" -> 9.10



input('Beenden.')
driver.quit() 
