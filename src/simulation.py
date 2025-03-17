import pandas as pd
from utils import CombinedElementData
import re

class BatterySimulation:
    def __init__(self, reduction_element, oxidation_element):
        self.reduction_element = reduction_element
        self.oxidation_element = oxidation_element
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

        return reduction_E - (-oxidation_E)  
    
    def clearValue(self, raw_value):
        cleaned_value = re.sub(r"[^\d,.-]", "", raw_value)
        cleaned_value = cleaned_value.replace(",", ".")
        e_potential = float(cleaned_value)
        
        return e_potential
        



if __name__ == "__main__":
    simulation = BatterySimulation(reduction_element="Fluor", oxidation_element="Lithium")
    print(simulation.getCellVoltage())