import pandas as pd
from utils import CombinedElementData
import re
import math

## TODO ES gibt mehrere Oxidationsstufen, dann muss über alle möglichen iteriert werden und die / dann Gui anpassen

class BatterySimulation:
    def __init__(self, reduction_element, oxidation_element, concentration_red=1, concentration_ox=1, temperature=298.15):
        self.reduction_element = reduction_element
        self.oxidation_element = oxidation_element
        self.concentration_red = concentration_red  
        self.concentration_ox = concentration_ox  
        self.temperature = temperature  
        self.combined = CombinedElementData(battery_materials_list=[self.reduction_element, self.oxidation_element])
        self.data = {
            "reduction": self.combined.get_data(self.reduction_element),
            "oxidation": self.combined.get_data(self.oxidation_element)
        }
    
    def getData(self):
        print(f"\nKombinierte Daten für '{self.reduction_element}' (Reduktion):")
        print(self.data["reduction"])
        print(f"\nKombinierte Daten für '{self.oxidation_element}' (Oxidation):")
        print(self.data["oxidation"])

    def getCellVoltage(self):
        reduction_E = self.clearValue(self.data["reduction"]["electrochemical_data"][0]["E° (V)"])
        oxidation_E = self.clearValue(self.data["oxidation"]["electrochemical_data"][0]["E° (V)"])
        
        n = self.getNumberOfElectrons()
        E_nernst = self.nernstEquation(reduction_E, oxidation_E, n)
        
        return E_nernst

    def clearValue(self, raw_value):
        cleaned_value = re.sub(r"[^\d,.-]", "", raw_value)
        cleaned_value = cleaned_value.replace(",", ".")
        e_potential = float(cleaned_value)
        
        return e_potential

    def getNumberOfElectrons(self):
        electrons_reduction = self.data["reduction"]["electrochemical_data"][0]["Pfeil"]
        electrons_oxidation = self.data["oxidation"]["electrochemical_data"][0]["Pfeil"]
        
        reduction_match = re.search(r'(\d+)\s*e−', electrons_reduction)
        oxidation_match = re.search(r'(\d+)\s*e−', electrons_oxidation)
        
        reduction_electrons = int(reduction_match.group(1)) if reduction_match else None
        oxidation_electrons = int(oxidation_match.group(1)) if oxidation_match else None

        lcm_value = math.lcm(reduction_electrons, oxidation_electrons)

        return lcm_value

    def nernstEquation(self, reduction_E, oxidation_E, n):
        R = 8.314  # J/mol·K
        F = 96485  # C/mol
        T = self.temperature  # Temperatur in Kelvin
        
        # Berechnung der Zellspannung unter Verwendung der Nernst-Gleichung
        E = reduction_E - (-oxidation_E - ((R * T) / (n * F)) * math.log(self.concentration_ox / self.concentration_red))
        return E


if __name__ == "__main__":
    # Beispielsimulation mit Konzentrationen und Temperatur
    simulation = BatterySimulation(reduction_element="Kupfer", oxidation_element="Zink", concentration_red=1, concentration_ox=1, temperature=298.15)
    print(simulation.getCellVoltage())
