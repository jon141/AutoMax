import smtplib
from email.message import EmailMessage
from datetime import datetime


import time
import socket

def wait_for_internet(host="8.8.8.8", port=53, timeout=3): 
    while True:
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            print("Internetverbindung verfügbar!")
            break
        except socket.error:
            print("Keine Internetverbindung. Neuer Versuch in 5 Sekunden...")
            time.sleep(5)

wait_for_internet()


def sent_mail(fromMail, passwort, smtp_server, smtp_port, toMail, subject, message, bcc):

    try:
                
        msg = EmailMessage() 

        msg['Subject'] = subject
        msg['From'] = fromMail
        msg['To'] = toMail
        msg.set_content(message)

        if bcc == True:
            recipients = [msg['To'], fromMail] 
        else:
            recipients = [msg['To']]

        try:

            if smtp_port == 465:  # SSL für Port 465
                with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                    smtp.login(fromMail, passwort)
                    smtp.send_message(msg, to_addrs=recipients)


            elif smtp_port == 587:  # STARTTLS für Port 587
                with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                    smtp.starttls()  # Verschlüsselung
                    smtp.login(fromMail, passwort)
                    smtp.send_message(msg, to_addrs=recipients)

            else:
                print(f"Unbekannter Port: {smtp_port}. Keine Verbindung hergestellt.")


        except Exception as e:
            print(f'Fehler: {e}')
    except Exception as e:
        print(e)
            
      

