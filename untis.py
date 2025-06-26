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



def mittagschule_finden():
    print("gestartet")
    time.sleep(3)  # Warte auf das Laden der Seite

    # 1. Top-Koordinate des Zeitelements "12:00" finden
    zeit_top = None
    elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'timetable-grid-slot-time')]")
    for el in elements:
        try:
            span = el.find_element(By.XPATH, ".//span[contains(@class, 'timetable-grid-slot-time--time-value')]")
            if span.text.strip() == "12:00":
                style = el.get_attribute("style")
                if "top:" in style:
                    zeit_top = float(style.split("top:")[1].split("px")[0].strip())
                    print(f"Top-Koordinate für 12:00: {zeit_top}")
                    break
        except:
            continue

    if zeit_top is None:
        print("Zeitfeld 12:00 nicht gefunden.")
        return

    # 2. Alle Karten prüfen, ob sie die Zeit-Koordinate abdecken
    karten = driver.find_elements(By.XPATH, "//div[contains(@class, 'timetable-grid-card')]")
    count = 0
    for karte in karten:
        style = karte.get_attribute("style")
        try:
            top = float(style.split("top:")[1].split("px")[0].strip())
            height = float(style.split("height:")[1].split("px")[0].strip())
            if top <= zeit_top <= top + height:
                count += 1
        except Exception:
            continue
    print(f"Karten auf Höhe 12:00: {count}")

mittagschule_finden()



input('Beenden.')
driver.quit()
