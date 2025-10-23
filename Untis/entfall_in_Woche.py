 
def get_entfall_in_week(datum):
    url_vertretungsplanwoche = "https://cissa.webuntis.com/timetable/class?date=" + str(datum)
# Daten aus dem Stundenplan für alle auslesen

    # Beispiel: Stundenplanseite öffnen (kann angepasst werden)
    driver.get(url_vertretungsplanwoche)
    time.sleep(3)

    # alle Elemente der klasse .lesson-card.cancelled abrufen -> hier sind die Entfälle enthalten
    all_faecher = []

    # Sichtbare abgesagte Stunden
    all_entfall = driver.find_elements(By.CSS_SELECTOR, ".lesson-card.cancelled")
    for lesson in all_entfall:
        try:
            #print('Lesson', lesson)
            #classes = lesson.get_attribute("class")
            #print(repr(classes))
            fach = lesson.find_element(By.CLASS_NAME, "lesson-card-subject").text
            all_faecher.append(fach)

            testid = lesson.get_attribute("data-testid")
            if "-" in testid and testid.count("-") == 3:  # lesson-card-23423-23423 für doppel
                print('doppelstundeeeeeeeee')
                all_faecher.append(fach)  # ein zweites mal hinzufügen, weil doppelstunde

            else:
                print('einzelstundeeeeeeeeeeeee')
        except:
            continue

    # Versteckte abgesagte Stunden (in "mehr"-Containern)
    invisible_containers = driver.find_elements(By.CSS_SELECTOR, ".timetable-summarised-entries--inner.highlighted")

    for container in invisible_containers:
        mehr_button = container.find_element(By.CSS_SELECTOR, ".timetable-summarised-entries--text")
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".timetable-summarised-entries--text")))
        mehr_button.click()

        scrollcontainer = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".scroll-container")))
        entfall = scrollcontainer.find_elements(By.CSS_SELECTOR, ".lesson-card.cancelled")

        for lesson in entfall:
            try:
                print('versteckte stundne')
                #print('Lesson', lesson.)

                #classes = lesson.get_attribute("class")
                #print(repr(classes))

                fach = lesson.find_element(By.CLASS_NAME, "lesson-card-subject").text
                all_faecher.append(fach)

                testid = lesson.get_attribute("data-testid")
                if "-" in testid and testid.count("-") == 3:  # lesson-card-23423-23423 für doppel
                    print('doppelstundeeeeeeeee')
                    all_faecher.append(fach)  # ein zweites mal hinzufügen, weil doppelstunde

                else:
                    print('einzelstundeeeeeeeeeeeee')

            except:
                continue

        close_button = driver.find_element(By.CSS_SELECTOR, 'button[data-testid="close-icon"]')
        time.sleep(0.1)
        driver.execute_script("arguments[0].click();", close_button)
    return (datum, all_faecher)