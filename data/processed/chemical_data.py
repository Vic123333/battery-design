import pubchempy as pcp
import pandas as pd

class BatteryMaterial:
    def __init__(self, name):
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
        self._get_material_data()

    def _get_material_data(self):
        try:
            compound = pcp.get_compounds(self.name, namespace='name')[0]
            self.data = {prop: getattr(compound, prop, None) for prop in self.properties}
            self.data["name"] = self.name
        except IndexError:
            print(f"Material {self.name} nicht gefunden.")

    def get_data(self):
        return self.data


def get_battery_material_data(materials):
    material_objects = [BatteryMaterial(material) for material in materials]
    data = [material.get_data() for material in material_objects]
    return pd.DataFrame(data)

if __name__ == "__main__":
    materials = ["Lithium", "Cobalt", "Graphite", "Nickel", "Manganese", "Iron"]
    df = get_battery_material_data(materials)
    print(df)
