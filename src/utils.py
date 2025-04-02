
import json

class ElectrochemicalSeries:
    def __init__(self):
        # Farben hinzugefügt (Standardnamen oder Hex-Codes)
        self.series = [
             # Element, Reaktion, E0, n, Ionenformel, Farbe
             { "element": "Li", "reaction": "Li+ + e- -> Li", "E0": -3.04, "n": 1, "ion_formula": "Li+", "color": "#C0C0C0" }, # Silver
             { "element": "K", "reaction": "K+ + e- -> K", "E0": -2.93, "n": 1, "ion_formula": "K+", "color": "#C0C0C0" },  # Silver
             { "element": "Ca", "reaction": "Ca2+ + 2e- -> Ca", "E0": -2.87, "n": 2, "ion_formula": "Ca²⁺", "color": "#C0C0C0" },# Silver
             { "element": "Na", "reaction": "Na+ + e- -> Na", "E0": -2.71, "n": 1, "ion_formula": "Na+", "color": "#C0C0C0" }, # Silver
             { "element": "Mg", "reaction": "Mg2+ + 2e- -> Mg", "E0": -2.37, "n": 2, "ion_formula": "Mg²⁺", "color": "#C0C0C0" },# Silver
             { "element": "Al", "reaction": "Al3+ + 3e- -> Al", "E0": -1.66, "n": 3, "ion_formula": "Al³⁺", "color": "#C0C0C0" },# Silver
             { "element": "Zn", "reaction": "Zn2+ + 2e- -> Zn", "E0": -0.76, "n": 2, "ion_formula": "Zn²⁺", "color": "#A9A9A9" }, # DarkGray (typisch Zink)
             { "element": "Fe", "reaction": "Fe2+ + 2e- -> Fe", "E0": -0.44, "n": 2, "ion_formula": "Fe²⁺", "color": "#808080" }, # Gray
             { "element": "Ni", "reaction": "Ni2+ + 2e- -> Ni", "E0": -0.25, "n": 2, "ion_formula": "Ni²⁺", "color": "#C0C0C0" },# Silver
             { "element": "Sn", "reaction": "Sn2+ + 2e- -> Sn", "E0": -0.14, "n": 2, "ion_formula": "Sn²⁺", "color": "#C0C0C0" },# Silver
             { "element": "Pb", "reaction": "Pb2+ + 2e- -> Pb", "E0": -0.13, "n": 2, "ion_formula": "Pb²⁺", "color": "#696969" }, # DimGray (typisch Blei)
             # H bekommt Pt-Farbe, da oft Pt-Elektrode verwendet wird
             { "element": "H", "reaction": "2H+ + 2e- -> H2", "E0": 0.00, "n": 2, "ion_formula": "H+", "color": "#E5E4E2" }, # Platinum color
             { "element": "Cu", "reaction": "Cu2+ + 2e- -> Cu", "E0": 0.34, "n": 2, "ion_formula": "Cu²⁺", "color": "#B87333" }, # Copper
             { "element": "Ag", "reaction": "Ag+ + e- -> Ag", "E0": 0.80, "n": 1, "ion_formula": "Ag+", "color": "silver" },   # Silver (Name)
             { "element": "Pt", "reaction": "Pt2+ + 2e- -> Pt", "E0": 1.20, "n": 2, "ion_formula": "Pt²⁺", "color": "#E5E4E2" }, # Platinum
             { "element": "Au", "reaction": "Au3+ + 3e- -> Au", "E0": 1.50, "n": 3, "ion_formula": "Au³⁺", "color": "gold" }     # Gold (Name)
        ]

    def get_element_names(self):
        """Gibt eine Liste der verfügbaren Elementnamen zurück."""
        # Sortiere nach dem Standardpotential (E0) aufsteigend
        return sorted([elem['element'] for elem in self.series], key=lambda name: self.get_element_data(name)['E0'])

    def get_element_data(self, element_name: str) -> dict:
        """Sucht die elektrochemischen Daten eines Elements."""
        for elem in self.series:
            if elem["element"] == element_name:
                return elem
        raise ValueError(f"Element '{element_name}' nicht in der Spannungsreihe gefunden!")