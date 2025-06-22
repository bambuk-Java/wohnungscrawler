import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import time
from datetime import datetime
import os

# Deine Einstellungen
MIN_ROOMS = 4
CHECK_INTERVAL = 600  # alle 10 Minuten
YOUR_EMAIL = os.getenv("YOUR_EMAIL")
YOUR_PASSWORD = os.getenv("YOUR_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

# Speichert gefundene Wohnungen, damit du nicht doppelt Mails bekommst
found_apartments = set()

def check_apartments():
    url = "https://www.vermietungen.stadt-zuerich.ch/publication/apartment/"
    try:
        response = requests.get(url)
    except requests.exceptions.HTTPError as errh:
        print("HTTP Error")
        print(errh.args[0])
    soup = BeautifulSoup(response.text, 'html.parser')

    # Alle Listenelemente finden (muss evtl. angepasst werden!)
    listings = soup.find_all('tr')

    new_matches = []

    for listing in listings:
        columns = listing.find_all('td')
        if len(columns) >= 4:
            try:
                rooms = float(columns[2].get_text(strip=True).replace(',', '.'))
                rent = float(columns[5].get_text(strip=True).replace(',', '.'))
                area = columns[4].get_text(strip=True)
                street = columns[1].get_text(strip=True)
                kreis = columns[6].get_text(strip=True)
                link = columns[0].find('a')['href']
                full_link = "https://www.vermietungen.stadt-zuerich.ch" + link
                if rooms >= MIN_ROOMS and full_link not in found_apartments:
                    new_matches.append([full_link, rooms, area, rent, street, kreis ])
                    found_apartments.add(full_link)
            except:
                continue
    return new_matches

def send_email(matches):
    lines = []
    for match in matches:
        full_link, rooms, area, rent, street, kreis = match
        lines.append(
            f"""
Wohnung gefunden:
  Link: {full_link}
  Zimmer: {rooms}
  Fläche: {area}
  Miete: {rent} CHF
  Strasse: {street}
  Kreis: {kreis}
"""
        )

    message_body = "\n\n".join(lines)

    msg = MIMEText(message_body)
    msg['Subject'] = f"Neue Wohnungen gefunden ({len(matches)})"
    msg['From'] = YOUR_EMAIL
    msg['To'] = TO_EMAIL  # als String für den Header OK

    # 🗝️ WICHTIG: Liste für sendmail
    recipients = [email.strip() for email in TO_EMAIL.split(",")]

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(YOUR_EMAIL, YOUR_PASSWORD)
        server.sendmail(YOUR_EMAIL, recipients, msg.as_string())

if __name__ == "__main__":
    while True:
        print("Prüfe Wohnungen...")
        matches = check_apartments()
        if matches:
            for match in matches:
                full_link, rooms, area, rent, street, kreis = match
                print(
                    f"""
                    Wohnung gefunden:
                    Link: {full_link}
                    Zimmer: {rooms}
                    Fläche: {area}
                    Miete: {rent} CHF
                    Strasse: {street}
                    Kreis: {kreis}
                    """
                )
            send_email(matches)
        else:
            current_time = datetime.now()
            print(current_time, ": Keine neuen passenden Wohnungen.")
        time.sleep(CHECK_INTERVAL)
