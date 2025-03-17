import tkinter as tk
from tkinter import messagebox
from simulation import BatterySimulation

def calculate_reaction():
    reduction_element = reduction_entry.get()
    oxidation_element = oxidation_entry.get()
    
    try:
        simulation = BatterySimulation(reduction_element, oxidation_element)
        voltage = simulation.getCellVoltage()
        result_label.config(text=f"Zellspannung: {voltage:.2f} V")
        
        if voltage > 0:
            messagebox.showinfo("Ergebnis", "Die Reaktion ist freiwillig (spontan).")
        else:
            messagebox.showwarning("Ergebnis", "Die Reaktion ist nicht freiwillig (nicht spontan).")
    except Exception as e:
        messagebox.showerror("Fehler", f"Fehler bei der Berechnung: {str(e)}")

# GUI erstellen
root = tk.Tk()
root.title("Batterie Simulation")

# Labels und Eingabefelder
tk.Label(root, text="Reduktionsmittel:").grid(row=0, column=0)
reduction_entry = tk.Entry(root)
reduction_entry.grid(row=0, column=1)

tk.Label(root, text="Oxidationsmittel:").grid(row=1, column=0)
oxidation_entry = tk.Entry(root)
oxidation_entry.grid(row=1, column=1)

# Berechnen-Button
calculate_button = tk.Button(root, text="Berechnen", command=calculate_reaction)
calculate_button.grid(row=2, columnspan=2)

# Ergebnis-Label
result_label = tk.Label(root, text="")
result_label.grid(row=3, columnspan=2)

# Hauptloop starten
root.mainloop()
