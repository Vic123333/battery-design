import pubchempy as pcp
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sqlite3
import json
import time
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# SQLite Cache Klasse mit Zeitstempel, Context Manager und Thread-Safety
class SQLiteCache:
    def __init__(self, db_path="cache.db"):
        self.db_path = db_path
        # Erlaube Multi-Threading in SQLite
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.lock = threading.Lock()
        self.create_tables()
    
    def create_tables(self):
        with self.lock:
            cursor = self.conn.cursor()
            # Tabelle für Batteriematerialien mit Zeitstempel
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS battery_materials (
                    name TEXT PRIMARY KEY,
                    data TEXT,
                    timestamp REAL
                )
            ''')
            # Tabelle für gescrapte Seiten mit Zeitstempel
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scraped_pages (
                    url TEXT PRIMARY KEY,
                    html TEXT,
                    timestamp REAL
                )
            ''')
            self.conn.commit()
    
    def get_battery_material(self, name, max_age=7200):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT data, timestamp FROM battery_materials WHERE name=?", (name,))
            row = cursor.fetchone()
        if row:
            data, timestamp = row
            # Prüfen, ob der Cache-Eintrag jünger als max_age (2 Stunden) ist
            if time.time() - timestamp < max_age:
                return json.loads(data)
        return None
    
    def set_battery_material(self, name, data):
        with self.lock:
            cursor = self.conn.cursor()
            current_time = time.time()
            cursor.execute(
                "INSERT OR REPLACE INTO battery_materials (name, data, timestamp) VALUES (?, ?, ?)", 
                (name, json.dumps(data), current_time)
            )
            self.conn.commit()
    
    def get_scraped_page(self, url, max_age=7200):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute("SELECT html, timestamp FROM scraped_pages WHERE url=?", (url,))
            row = cursor.fetchone()
        if row:
            html, timestamp = row
            if time.time() - timestamp < max_age:
                return html
        return None
    
    def set_scraped_page(self, url, html):
        with self.lock:
            cursor = self.conn.cursor()
            current_time = time.time()
            cursor.execute(
                "INSERT OR REPLACE INTO scraped_pages (url, html, timestamp) VALUES (?, ?, ?)", 
                (url, html, current_time)
            )
            self.conn.commit()
    
    def close(self):
        with self.lock:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

# Erstelle eine globale Cache-Instanz, die auch als Kontextmanager genutzt werden kann
global_cache = SQLiteCache()

class BatteryMaterial:
    def __init__(self, name, cache_instance=global_cache):
        self.name = name
        self.properties = [
            "molecular_formula", "molecular_weight", "canonical_smiles", "inchi", "iupac_name", 
            "xlogp", "exact_mass", "monoisotopic_mass", "tpsa", "complexity", "h_bond_donor_count", 
            "h_bond_acceptor_count", "rotatable_bond_count", "heavy_atom_count", "isotope_atom_count", 
            "atom_stereo_count", "defined_atom_stereo_count", "undefined_atom_stereo_count", 
            "bond_stereo_count", "defined_bond_stereo_count", "undefined_bond_stereo_count", 
            "covalent_unit_count"
        ]
        self.data = {}
        self.cache = cache_instance
        self._get_material_data()
    
    def _get_material_data(self):
        # Zuerst im Cache nachsehen (letzte 2 Stunden)
        cached_data = self.cache.get_battery_material(self.name)
        if cached_data:
            self.data = cached_data
            return
        
        try:
            compounds = pcp.get_compounds(self.name, namespace='name')
            if not compounds:
                print(f"Material {self.name} nicht gefunden.")
                return
            compound = compounds[0]
            self.data = {prop: getattr(compound, prop, None) for prop in self.properties}
            self.data["name"] = self.name
            # Ergebnis im Cache speichern
            self.cache.set_battery_material(self.name, self.data)
        except Exception as e:
            print(f"Fehler beim Abrufen von {self.name}: {e}")
    
    def get_data(self):
        return self.data

def get_battery_material_data(materials, cache_instance=global_cache):
    # Parallelisiere die Abfragen mit ThreadPoolExecutor
    material_objects = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(BatteryMaterial, material, cache_instance): material for material in materials}
        for future in as_completed(futures):
            try:
                material_obj = future.result()
                material_objects.append(material_obj)
            except Exception as exc:
                print(f"Material {futures[future]} generierte eine Exception: {exc}")
    data = [material.get_data() for material in material_objects]
    return pd.DataFrame(data)

class ElektrochemischeSpannungsreiheScraper:
    def __init__(self, url="https://de.wikipedia.org/wiki/Elektrochemische_Spannungsreihe", cache_instance=global_cache):
        self.url = url
        self.html = ""
        self.potentiale = []
        self.cache = cache_instance
    
    def fetch_page(self):
        """Lädt den HTML-Inhalt der Seite herunter oder nutzt den Cache (gültig für 2 Stunden)."""
        cached_html = self.cache.get_scraped_page(self.url)
        if cached_html:
            self.html = cached_html
            return
        response = requests.get(self.url)
        if response.status_code != 200:
            raise Exception(f"Fehler beim Laden der Seite: Statuscode {response.status_code}")
        self.html = response.text
        self.cache.set_scraped_page(self.url, self.html)
    
    def parse_table(self):
        """Parst die Tabelle mit Standardpotentialen und speichert die Daten.
           Dabei wird der Elementname per Regex bereinigt (z.B. "Fluor(F)" -> "Fluor")."""
        soup = BeautifulSoup(self.html, "html.parser")
        table = soup.find("table", {"class": "wikitable sortable"})
        if not table:
            raise Exception("Die Tabelle wurde nicht gefunden.")
        rows = table.find_all("tr")[1:]  # Header überspringen

        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 5:
                raw_element = cols[0].get_text(strip=True)
                element = re.sub(r'\(.*?\)', '', raw_element).strip()
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

class CombinedElementData:
    """
    Kombiniert Daten der elektrochemischen Spannungsreihe und der Batteriematerialien
    für ein bestimmtes Element. Der Elementname wird dabei per Regex bereinigt,
    sodass der Vergleich (z.B. "Fluor") eindeutig möglich ist.
    """
    def __init__(self, cache_instance=global_cache, scraper_url="https://de.wikipedia.org/wiki/Elektrochemische_Spannungsreihe", battery_materials_list=None):
        self.cache = cache_instance
        # Scraping der elektrochemischen Spannungsreihe
        self.scraper = ElektrochemischeSpannungsreiheScraper(url=scraper_url, cache_instance=self.cache)
        self.electro_df = self.scraper.scrape()
        
        # Verwende einen Default-Wert, falls keine Liste übergeben wird
        if battery_materials_list is None:
            battery_materials_list = ["Lithium", "Cobalt", "Graphite", "Nickel", "Manganese", "Iron"]
        self.battery_materials = {}
        for mat in battery_materials_list:
            bm = BatteryMaterial(mat, cache_instance=self.cache)
            self.battery_materials[mat.strip().lower()] = bm.get_data()
    
    def get_data(self, element_name):
        """
        Gibt ein Dictionary zurück mit den Schlüsseln "electrochemical_data" und
        "battery_material_data" für das angefragte Element (z.B. "Fluor").
        """
        element_name_clean = element_name.strip().lower()
        electro_data = []
        for _, row in self.electro_df.iterrows():
            if row["Element"].strip().lower() == element_name_clean:
                electro_data.append(row.to_dict())
        battery_data = self.battery_materials.get(element_name_clean)
        return {
            "electrochemical_data": electro_data,
            "battery_material_data": battery_data
        }

# Beispielhafte Nutzung
if __name__ == "__main__":
    # Verwende den Cache als Kontextmanager
    with SQLiteCache() as cache_instance:
        # Elektrochemische Spannungsreihe abrufen
        scraper = ElektrochemischeSpannungsreiheScraper(cache_instance=cache_instance)
        df_potenziale = scraper.scrape()
        print("Elektrochemische Spannungsreihe:")
        print(df_potenziale)
        
        # Batteriematerialien (parallelisiert) abrufen
        materials = ["Lithium", "Cobalt", "Graphite", "Nickel", "Manganese", "Iron"]
        df_materials = get_battery_material_data(materials, cache_instance=cache_instance)
        print("\nBatteriematerialien:")
        print(df_materials)
        
        # Kombinierte Daten für ein bestimmtes Element (z.B. "Fluor") abrufen
        combined = CombinedElementData(cache_instance=cache_instance,
                                       battery_materials_list=["Fluor", "Lithium", "Cobalt", "Graphite", "Nickel", "Manganese", "Iron"])
        data = combined.get_data("Fluor")
        print("\nKombinierte Daten für 'Fluor':")
        print(data)
