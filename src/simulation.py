# simulation.py
import math
# Nimm an, dass utils.py im selben Ordner liegt oder im PYTHONPATH ist
from utils import ElectrochemicalSeries

R = 8.314  # universelle Gaskonstante in J/(mol·K)
F = 96485  # Faraday-Konstante in C/mol

class ElectrochemicalElement:
    """Adapter-Klasse für elektrochemische Elementdaten."""
    def __init__(self, element_data: dict) -> None:
        self.element = element_data.get("element", "N/A")
        self.reaction = element_data.get("reaction", "N/A")
        self.potential = element_data.get("E0", 0.0)  # Standard-Reduktionspotential in V
        self.electrons = element_data.get("n", 0)     # Anzahl der übertragenen Elektronen
        # Nutze die explizite Ionenformel aus den Daten
        self.ion_formula = element_data.get("ion_formula", "?") # Angepasste Variable

    def get_oxidation_reaction(self) -> str:
        """Gibt die umgekehrte Reaktion (Oxidation) als String zurück."""
        # Diese Methode könnte vereinfacht werden, wenn die Struktur immer gleich ist
        # oder man könnte eine robustere Parsing-Methode verwenden.
        # Annahme: Format ist "Ion + ne- -> Element" oder "Koeff*Ion + ne- -> Element/Molekül"
        parts = self.reaction.split('->')
        if len(parts) == 2:
            reactants_side = parts[0].strip()
            product_side = parts[1].strip()

            # Versuche, Elektronen zu entfernen (robuster als einfacher replace)
            electron_term = f"{self.electrons}e-"
            reactants_cleaned = reactants_side.replace(f" + {electron_term}", "").replace(f"{electron_term} + ", "").strip()

            # Die Oxidationsreaktion ist Produkt -> ursprüngliche Reaktanten (ohne e-) + e-
            return f"{product_side} -> {reactants_cleaned} + {self.electrons}e-"
        return "Umkehrung fehlgeschlagen"

    def __repr__(self) -> str:
        return (f"ElectrochemicalElement(element={self.element}, reaction='{self.reaction}', "
                f"potential={self.potential}, electrons={self.electrons}, ion_formula='{self.ion_formula}')") # Angepasst


class BatterySimulation:
    """
    Simuliert eine elektrochemische Zelle und berechnet relevante Größen.
    Berücksichtigt Stöchiometrie für die Q-Berechnung.
    """
    def __init__(self, cathode_element_data: dict, anode_element_data: dict) -> None:
        self.cathode = ElectrochemicalElement(cathode_element_data) # Reduktion (+)
        self.anode = ElectrochemicalElement(anode_element_data)     # Oxidation (-)

        # Stelle sicher, dass die Anode das geringere Potential hat (Standardfall für galvanische Zelle)
        # Wenn nicht, könnte man die Rollen tauschen oder eine Warnung ausgeben.
        # Hier gehen wir davon aus, dass die Auswahl in der GUI korrekt ist (Anode = unedler).
        if self.anode.potential > self.cathode.potential:
             print(f"Warnung: Das gewählte Anodenmaterial ({self.anode.element}) ist edler als das Kathodenmaterial ({self.cathode.element}). Die berechnete Spannung wird negativ sein (elektrolytische Zelle).")


        if not self.cathode.electrons or not self.anode.electrons or self.cathode.electrons <= 0 or self.anode.electrons <= 0:
              raise ValueError("Elektronenanzahl für Anode oder Kathode ungültig (<= 0 oder nicht definiert).")

        # Bestimme die Anzahl der Elektronen für die ausgeglichene Reaktion (kleinstes gemeinsames Vielfaches)
        try:
            self.n_overall = math.lcm(self.cathode.electrons, self.anode.electrons)
        except TypeError: # Fallback für ältere Python-Versionen ohne math.lcm
             # Einfache Implementierung von kgV
             def gcd(a, b):
                 while b:
                     a, b = b, a % b
                 return a
             def lcm(a, b):
                  return (a * b) // gcd(a, b) if a != 0 and b != 0 else 0
             self.n_overall = lcm(self.cathode.electrons, self.anode.electrons)


        # Berechne die Faktoren, mit denen die Halbreaktionen multipliziert werden müssen
        self.factor_cathode = self.n_overall // self.cathode.electrons
        self.factor_anode = self.n_overall // self.anode.electrons

        # Überprüfe, ob Potentiale gültig sind
        if self.cathode.potential is None or self.anode.potential is None:
            raise ValueError("Potentiale für Kathode oder Anode nicht verfügbar.")

    def get_stoichiometric_factors(self) -> tuple[int, int]:
        """
        Gibt die stöchiometrischen Faktoren für die Ionen in der Q-Berechnung zurück.
        ACHTUNG: Dies geht davon aus, dass der Koeffizient des Ions in der Halbreaktion 1 ist.
        Für Reaktionen wie 2H+ + 2e- -> H2 muss dies angepasst werden, falls H+ als Anode/Kathode genutzt wird.
        Die aktuelle `ElectrochemicalSeries` hat einfache Ionen, daher passt es hier.

        :return: Tuple (factor_anode_ion, factor_cathode_ion)
                 factor_anode_ion: Stöchiometrischer Koeffizient des Ions, das an der Anode *entsteht*.
                 factor_cathode_ion: Stöchiometrischer Koeffizient des Ions, das an der Kathode *verbraucht* wird.
        """
        # Hier nehmen wir an, dass pro Halbreaktion (wie in utils.py definiert)
        # genau ein Ion mit dem Koeffizienten 1 beteiligt ist.
        # Wenn komplexere Reaktionen (z.B. 2Ag+ + ...) hinzukämen, müsste man die Koeffizienten parsen.
        anode_ion_stoich_factor = self.factor_anode # Multiplikator für die gesamte Halbreaktion
        cathode_ion_stoich_factor = self.factor_cathode # Multiplikator für die gesamte Halbreaktion
        return anode_ion_stoich_factor, cathode_ion_stoich_factor

    def get_standard_cell_voltage(self) -> float:
        """Berechnet die Standardzellspannung E⁰_cell = E⁰(Kathode) - E⁰(Anode)."""
        return self.cathode.potential - self.anode.potential

    def get_nernst_voltage(self, reaction_quotient: float, temperature: float = 298.15) -> float:
        """Berechnet die Zellspannung mittels Nernst-Gleichung: E = E⁰ - (RT / nF) * ln(Q)."""
        if self.n_overall <= 0: # F ist positiv
             raise ValueError("Gesamt-Elektronenanzahl (n) muss positiv sein.")
        if reaction_quotient <= 0:
             # In der Realität kann Q sehr klein, aber > 0 sein.
             # Ein Logarithmus von 0 oder negativ ist mathematisch undefiniert.
             raise ValueError("Reaktionsquotient (Q) muss positiv sein.")
        if temperature <= 0:
             raise ValueError("Temperatur muss positiv sein (in Kelvin).")

        E0_cell = self.get_standard_cell_voltage()
        try:
             # Verwende n_overall (kgV der Elektronen)
             nernst_term = (R * temperature / (self.n_overall * F)) * math.log(reaction_quotient)
        except (OverflowError, ValueError) as e:
             # ValueError kann bei math.log(sehr kleiner Zahl) auftreten oder math.log(großer Zahl) -> Overflow
             raise ValueError(f"Fehler bei Logarithmus-Berechnung für Q={reaction_quotient}: {e}")

        return E0_cell - nernst_term

    def get_delta_G0(self) -> float:
        """Berechnet die Standard-Gibbs-Energie ΔG⁰ = -n * F * E⁰_cell."""
        if self.n_overall <= 0:
             raise ValueError("Gesamt-Elektronenanzahl (n) muss positiv sein.")
        E0_cell = self.get_standard_cell_voltage()
        # Verwende n_overall (kgV der Elektronen)
        return -self.n_overall * F * E0_cell

    def get_cathode_reaction(self) -> str:
        """Gibt die (ggf. multiplizierte) Reaktionsgleichung der Kathode (Reduktion) zurück."""
        # return f"{self.factor_cathode} * ({self.cathode.reaction})" # Optionale Anzeige mit Faktor
        return self.cathode.reaction # Einfache Anzeige

    def get_anode_reaction(self) -> str:
        """Gibt die (ggf. multiplizierte) Reaktionsgleichung der Anode (Oxidation) zurück."""
        # return f"{self.factor_anode} * ({self.anode.get_oxidation_reaction()})" # Optionale Anzeige mit Faktor
        return self.anode.get_oxidation_reaction() # Einfache Anzeige