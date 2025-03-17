import requests
from bs4 import BeautifulSoup
import pandas as pd

class ElektrochemischeSpannungsreiheScraper:
    def __init__(self, url="https://de.wikipedia.org/wiki/Elektrochemische_Spannungsreihe"):
        self.url = url
        self.html = ""
        self.potentiale = []
    
    def fetch_page(self):
        """Lädt den HTML-Inhalt der Seite herunter."""
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception(f"Fehler beim Laden der Seite: Statuscode {response.status_code}")
        self.html = response.text
    
    def parse_table(self):
        """Parst die Tabelle mit Standardpotentialen und speichert die Daten."""
        soup = BeautifulSoup(self.html, "html.parser")
        # Tabelle anhand der CSS-Klasse finden
        table = soup.find("table", {"class": "wikitable sortable"})
        if not table:
            raise Exception("Die Tabelle wurde nicht gefunden.")
        rows = table.find_all("tr")[1:]  # Überspringe den Header

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                element = cols[0].get_text(strip=True)
                oxidierte_form = cols[1].get_text(strip=True)
                pfeil = cols[2].get_text(strip=True)
                reduzierte_form = cols[3].get_text(strip=True)
                potential = cols[4].get_text(strip=True)
                self.potentiale.append({
                    "Element": element,
                    "oxidierte Form": oxidierte_form,
                    "Pfeil": pfeil,
                    "reduzierte Form": reduzierte_form,
                    "E° (V)": potential
                })
    
    def scrape(self):
        """Führt den gesamten Scraping-Prozess durch und gibt die Daten als Pandas DataFrame zurück."""
        self.fetch_page()
        self.parse_table()
        return pd.DataFrame(self.potentiale)

# Beispielhafte Nutzung
if __name__ == "__main__":
    scraper = ElektrochemischeSpannungsreiheScraper()
    df = scraper.scrape()
    print(df)
    # Optional: Speichern als CSV
    # df.to_csv("elektrochemische_spannungsreihe.csv", index=False)
