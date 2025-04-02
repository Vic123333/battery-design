import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

try:
    from utils import ElectrochemicalSeries
    from simulation import BatterySimulation, ElectrochemicalElement, R, F
except ImportError as e:
     messagebox.showerror("Import Fehler", f"Konnte Module nicht laden: {e}\nStellen Sie sicher, dass utils.py und simulation.py im selben Ordner wie gui.py sind.")
     import sys
     sys.exit(1)
import math 

class BatteryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Galvanische Zelle Simulation")
        self.root.minsize(800, 550)

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except tk.TclError:
            print("Hinweis: TTK Theme 'clam' nicht verfügbar, verwende Standard.")
            pass

        style.configure("TButton", padding=6, relief="flat", background="#E1E1E1")
        style.configure("TLabelFrame", padding=5, font=('Calibri', 10))
        style.configure("TLabel", padding=2, font=('Calibri', 10))
        style.configure("TEntry", padding=3, font=('Calibri', 10))
        style.configure("TCombobox", padding=3, font=('Calibri', 10))


        try:
             self.series_data = ElectrochemicalSeries()
             self.element_names = self.series_data.get_element_names()
        except NameError:
             messagebox.showerror("Fehler", "Klasse 'ElectrochemicalSeries' nicht in utils.py gefunden.")
             sys.exit(1)
        except Exception as e:
             messagebox.showerror("Fehler", f"Fehler beim Laden der Daten aus utils.py: {e}")
             sys.exit(1)


        self.current_simulation: BatterySimulation | None = None

        self.anode_var = tk.StringVar()
        self.cathode_var = tk.StringVar()
        self.conc_anode_var = tk.StringVar(value="1.0")
        self.conc_cathode_var = tk.StringVar(value="1.0")
        self.temp_var = tk.StringVar(value="298.15")
        self.current_conc_anode: float = 1.0 # Für Visualisierung
        self.current_conc_cathode: float = 1.0 # Für Visualisierung
        self.anode_conc_label_var = tk.StringVar(value="[Anoden-Ion] (mol/L):")
        self.cathode_conc_label_var = tk.StringVar(value="[Kathoden-Ion] (mol/L):")
        self.voltage_var = tk.StringVar(value="E⁰: --- V")
        self.delta_g_var = tk.StringVar(value="ΔG⁰: --- kJ/mol")
        self.nernst_var = tk.StringVar(value="E_Nernst: --- V")
        self.q_display_var = tk.StringVar(value="Q: ---")
        self.anode_reaction_var = tk.StringVar(value="Anodenreaktion (Oxidation)")
        self.cathode_reaction_var = tk.StringVar(value="Kathodenreaktion (Reduktion)")
        self.anode_ion_label_var = tk.StringVar(value="Anoden-Ion")
        self.cathode_ion_label_var = tk.StringVar(value="Kathoden-Ion")

        self.create_input_frame()
        main_area_frame = ttk.Frame(self.root)
        main_area_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.root.grid_rowconfigure(1, weight=1)
        main_area_frame.grid_columnconfigure(0, weight=3) # Visualisierung mehr Platz
        main_area_frame.grid_columnconfigure(1, weight=1) # Formeln weniger

        self.create_visualization_frame(main_area_frame)
        self.create_formula_frame(main_area_frame)
        self.create_output_frame()

        if "Zn" in self.element_names and "Cu" in self.element_names:
            self.anode_var.set("Zn")
            self.cathode_var.set("Cu")
            self.update_concentration_labels()
            self.calculate_and_update()
        else:
             if self.element_names:
                  self.anode_var.set(self.element_names[0])
                  if len(self.element_names) > 1:
                       self.cathode_var.set(self.element_names[1])
                  self.update_concentration_labels()
                  self.calculate_and_update()


    def create_input_frame(self):
        """Erstellt den Frame für die Eingabeelemente."""
        input_frame = ttk.LabelFrame(self.root, text="Eingabe", padding=10)
        input_frame.grid(row=0, column=0, padx=10, pady=(10,5), sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1, minsize=100)
        input_frame.grid_columnconfigure(3, weight=1, minsize=100)
        input_frame.grid_columnconfigure(4, weight=0)

        ttk.Label(input_frame, text="Anode (- Pol, Oxidation):").grid(row=0, column=0, padx=(0,5), pady=2, sticky="w")
        anode_combo = ttk.Combobox(input_frame, textvariable=self.anode_var, values=self.element_names, width=10, state="readonly")
        anode_combo.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        anode_combo.bind("<<ComboboxSelected>>", self.handle_selection_change)

        ttk.Label(input_frame, text="Kathode (+ Pol, Reduktion):").grid(row=0, column=2, padx=(15,5), pady=2, sticky="w")
        cathode_combo = ttk.Combobox(input_frame, textvariable=self.cathode_var, values=self.element_names, width=10, state="readonly")
        cathode_combo.grid(row=0, column=3, padx=5, pady=2, sticky="ew")
        cathode_combo.bind("<<ComboboxSelected>>", self.handle_selection_change)

        ttk.Label(input_frame, textvariable=self.anode_conc_label_var).grid(row=1, column=0, padx=(0,5), pady=5, sticky="w")
        conc_anode_entry = ttk.Entry(input_frame, textvariable=self.conc_anode_var, width=12)
        conc_anode_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        conc_anode_entry.bind("<FocusOut>", self.calculate_and_update)
        conc_anode_entry.bind("<Return>", self.calculate_and_update)

        ttk.Label(input_frame, textvariable=self.cathode_conc_label_var).grid(row=1, column=2, padx=(15,5), pady=5, sticky="w")
        conc_cathode_entry = ttk.Entry(input_frame, textvariable=self.conc_cathode_var, width=12)
        conc_cathode_entry.grid(row=1, column=3, padx=5, pady=5, sticky="ew")
        conc_cathode_entry.bind("<FocusOut>", self.calculate_and_update)
        conc_cathode_entry.bind("<Return>", self.calculate_and_update)

        ttk.Label(input_frame, text="Temperatur (K):").grid(row=2, column=0, padx=(0,5), pady=5, sticky="w")
        temp_entry = ttk.Entry(input_frame, textvariable=self.temp_var, width=12)
        temp_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        temp_entry.bind("<FocusOut>", self.calculate_and_update)
        temp_entry.bind("<Return>", self.calculate_and_update)

        calc_button = ttk.Button(input_frame, text="Berechnen", command=self.calculate_and_update)
        calc_button.grid(row=2, column=3, padx=5, pady=5, sticky="e")

    def create_visualization_frame(self, parent_frame):
        """Erstellt den Frame für die schematische Darstellung."""
        vis_frame = ttk.LabelFrame(parent_frame, text="Zell-Schema", padding=10)
        vis_frame.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="nsew")
        vis_frame.grid_rowconfigure(0, weight=1)
        vis_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(vis_frame, bg="white", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", pady=5, padx=5)
        self.canvas.bind("<Configure>", self.redraw_canvas)

    def calculate_dynamic_fill_y(self, concentration: float, reference_y: float, min_y: float, max_y: float) -> float:
        """Berechnet die Y-Koordinate des Füllstands basierend auf der Konzentration."""
        min_conc_visual = 0.1
        max_conc_visual = 5.0
        reference_conc = 1.0
        clamped_conc = max(min_conc_visual, min(concentration, max_conc_visual))

        total_visual_height = max_y - min_y
        height_above_ref = reference_y - min_y
        height_below_ref = max_y - reference_y

        if total_visual_height <= 0 or height_above_ref < 0 or height_below_ref < 0:
            return reference_y

        if clamped_conc >= reference_conc: # Konzentration >= 1 -> Pegel steigt (Y sinkt)
            if max_conc_visual - reference_conc == 0: frac = 0.0
            else: frac = (clamped_conc - reference_conc) / (max_conc_visual - reference_conc)
            fill_y = reference_y - frac * height_above_ref
        else: # Konzentration < 1 -> Pegel sinkt (Y steigt)
            if reference_conc - min_conc_visual == 0: frac = 0.0
            else: frac = (reference_conc - clamped_conc) / (reference_conc - min_conc_visual)
            fill_y = reference_y + frac * height_below_ref

        return max(min_y, min(fill_y, max_y))

    def redraw_canvas(self, event=None):
         """Zeichnet den Inhalt der Canvas neu, passt sich an die Größe an."""
         self.canvas.delete("all")
         width = self.canvas.winfo_width()
         height = self.canvas.winfo_height()

         if width < 150 or height < 150:
             self.canvas.create_text(width/2, height/2, text="Fenster vergrößern...", font=("Calibri", 10))
             return

         electrode_width = max(30, width * 0.07)
         electrode_height = max(60, height * 0.35)
         beaker_width = max(100, width * 0.28)
         beaker_height = electrode_height + max(35, height*0.18)
         beaker_bottom_margin = max(18, height * 0.06)
         spacing = max(50, width * 0.1)
         top_margin = max(45, height * 0.16)
         bottom_margin = max(55, height*0.22)

         total_cell_width = 2 * beaker_width + spacing
         anode_beaker_x = (width - total_cell_width) / 2
         if anode_beaker_x < 10: anode_beaker_x = 10
         cathode_beaker_x = anode_beaker_x + beaker_width + spacing
         anode_x = anode_beaker_x + (beaker_width - electrode_width) / 2
         cathode_x = cathode_beaker_x + (beaker_width - electrode_width) / 2
         voltmeter_y = top_margin * 0.4
         wire_y_level = top_margin * 0.8
         beaker_y_top = wire_y_level + 5
         electrode_y_top = beaker_y_top + 12
         electrode_y_bottom = electrode_y_top + electrode_height
         beaker_y_bottom = beaker_y_top + beaker_height

         reference_fill_y = beaker_y_bottom - beaker_bottom_margin
         min_fill_y_allowed = beaker_y_bottom - 8
         max_fill_y_allowed = electrode_y_top + 8
         anode_fill_y_actual = self.calculate_dynamic_fill_y(
             self.current_conc_anode, reference_fill_y, max_fill_y_allowed, min_fill_y_allowed
         )
         cathode_fill_y_actual = self.calculate_dynamic_fill_y(
             self.current_conc_cathode, reference_fill_y, max_fill_y_allowed, min_fill_y_allowed
         )
         vm_width = max(40, width * 0.08)
         vm_height = max(28, height * 0.07)
         voltmeter_x = anode_beaker_x + beaker_width + spacing / 2

         anode_name = self.anode_var.get()
         cathode_name = self.cathode_var.get()
         anode_color = "#A9A9A9"  # Default Anodenfarbe (Zink-Grau)
         cathode_color = "#808080" # Default Kathodenfarbe (Grau)
         try:
             if anode_name:
                 anode_data = self.series_data.get_element_data(anode_name)
                 anode_color = anode_data.get("color", anode_color)
             if cathode_name:
                 cathode_data = self.series_data.get_element_data(cathode_name)
                 cathode_color = cathode_data.get("color", cathode_color)
         except ValueError:
             print(f"Warnung: Elementdaten für Farbfindung nicht gefunden ({anode_name}/{cathode_name})")
         except AttributeError:
              print(f"Warnung: Problem beim Zugriff auf Elementdaten für Farbe.")
         except Exception as e: # Fange andere mögliche Fehler ab
             print(f"Unerwarteter Fehler beim Holen der Farbe: {e}")


         # --- Zeichnen ---
         # 1. Bechergläser
         self.canvas.create_rectangle(anode_beaker_x, beaker_y_top, anode_beaker_x + beaker_width, beaker_y_bottom, outline="grey", width=1)
         self.canvas.create_rectangle(cathode_beaker_x, beaker_y_top, cathode_beaker_x + beaker_width, beaker_y_bottom, outline="grey", width=1)

         # 2. Elektroden (mit Farben aus Daten)
         self.canvas.create_rectangle(anode_x, electrode_y_top, anode_x + electrode_width, electrode_y_bottom, fill=anode_color, outline="black", width=1.5, tags="anode_electrode")
         self.canvas.create_rectangle(cathode_x, electrode_y_top, cathode_x + electrode_width, electrode_y_bottom, fill=cathode_color, outline="black", width=1.5, tags="cathode_electrode")

         # 3. Elektrolyt (Dynamisch)
         if anode_fill_y_actual < beaker_y_bottom -1:
            self.canvas.create_rectangle(anode_beaker_x + 1, anode_fill_y_actual, anode_beaker_x + beaker_width - 1, beaker_y_bottom -1 , fill="#ADD8E6", outline="", tags="anode_electrolyte")
         if cathode_fill_y_actual < beaker_y_bottom - 1:
             self.canvas.create_rectangle(cathode_beaker_x + 1, cathode_fill_y_actual, cathode_beaker_x + beaker_width -1, beaker_y_bottom -1 , fill="#ADD8E6", outline="", tags="cathode_electrolyte")

         # 4. Voltmeter (Symbol und externe Textanzeige)
         self.canvas.create_rectangle(voltmeter_x - vm_width/2, voltmeter_y - vm_height/2, voltmeter_x + vm_width/2, voltmeter_y + vm_height/2, outline="black", fill="white", width=1.5)
         self.canvas.create_text(voltmeter_x, voltmeter_y, text="V", font=("Calibri", 11, "bold")) # Nur 'V'
         # Spannungswert rechts vom Symbol
         vm_text = self.nernst_var.get().replace("E_Nernst: ", "").strip()
         if vm_text == "---": vm_text = "? V"
         self.canvas.create_text(voltmeter_x + vm_width/2 + 5, voltmeter_y, text=vm_text, font=("Calibri", 10, "bold"), anchor="w")

         # 5. Drähte und Elektronenfluss (Pfeil bleibt, Text entfernt)
         anode_wire_x = anode_x + electrode_width / 2
         cathode_wire_x = cathode_x + electrode_width / 2
         wire_y_electrode = electrode_y_top - 5
         self.canvas.create_line(anode_wire_x, wire_y_electrode, anode_wire_x, wire_y_level, width=1.5)
         self.canvas.create_line(anode_wire_x, wire_y_level, voltmeter_x - vm_width/2, wire_y_level, width=1.5)
         self.canvas.create_line(voltmeter_x - vm_width/2, wire_y_level, voltmeter_x - vm_width/2, voltmeter_y + vm_height/2, width=1.5)
         self.canvas.create_line(voltmeter_x + vm_width/2, voltmeter_y + vm_height/2, voltmeter_x + vm_width/2, wire_y_level, width=1.5)
         self.canvas.create_line(voltmeter_x + vm_width/2, wire_y_level, cathode_wire_x, wire_y_level, width=1.5, arrow=tk.LAST, arrowshape=(8,10,3), fill="blue") # Pfeil bleibt
         self.canvas.create_line(cathode_wire_x, wire_y_level, cathode_wire_x, wire_y_electrode, width=1.5)
         # Label "e- Fluss ->" wurde entfernt

         # 6. Salzbrücke (ohne Ionenfluss-Beschriftung/Pfeile)
         sb_width = 18
         sb_y1 = beaker_y_top + max(12, height * 0.04)
         sb_center_y = sb_y1
         sb_x1_center = anode_beaker_x + beaker_width * 0.8
         sb_x2_center = cathode_beaker_x + beaker_width * 0.2
         sb_anode_end_y = max(sb_y1 + 5, anode_fill_y_actual + 5)
         sb_cathode_end_y = max(sb_y1 + 5, cathode_fill_y_actual + 5)
         self.canvas.create_line(sb_x1_center, sb_center_y, sb_x2_center, sb_center_y, width=sb_width, fill="lightgrey", capstyle=tk.ROUND)
         self.canvas.create_line(sb_x1_center, sb_center_y, sb_x1_center, sb_anode_end_y, width=sb_width, fill="lightgrey")
         self.canvas.create_line(sb_x2_center, sb_center_y, sb_x2_center, sb_cathode_end_y, width=sb_width, fill="lightgrey")
         self.canvas.create_text((sb_x1_center + sb_x2_center) / 2, sb_center_y - sb_width/2 - 5, text="Salzbrücke", font=("Calibri", 9))
         # Pfeile und Labels für Kationen/Anionen wurden entfernt

         # 7. Beschriftungen (ohne Ionenanzeige im Becher)
         base_y_labels = beaker_y_bottom + 12
         line_height = 16
         # Anode Info
         self.canvas.create_text(anode_beaker_x + beaker_width / 2, base_y_labels, text="Anode (-)", font=("Calibri", 11, "bold"), anchor="n")
         self.canvas.create_text(anode_beaker_x + beaker_width / 2, base_y_labels + line_height, text=self.anode_var.get(), font=("Calibri", 10), anchor="n")
         self.canvas.create_text(anode_beaker_x + beaker_width / 2, base_y_labels + 2.5*line_height, text="Oxidation:", font=("Calibri", 10, "bold"), anchor="n")
         self.canvas.create_text(anode_beaker_x + beaker_width / 2, base_y_labels + 3.5*line_height, text=self.anode_reaction_var.get(), font=("Calibri", 9), width=beaker_width*1.1, anchor="n")
         # Kathode Info
         self.canvas.create_text(cathode_beaker_x + beaker_width / 2, base_y_labels, text="Kathode (+)", font=("Calibri", 11, "bold"), anchor="n")
         self.canvas.create_text(cathode_beaker_x + beaker_width / 2, base_y_labels + line_height, text=self.cathode_var.get(), font=("Calibri", 10), anchor="n")
         self.canvas.create_text(cathode_beaker_x + beaker_width / 2, base_y_labels + 2.5*line_height, text="Reduktion:", font=("Calibri", 10, "bold"), anchor="n")
         self.canvas.create_text(cathode_beaker_x + beaker_width / 2, base_y_labels + 3.5*line_height, text=self.cathode_reaction_var.get(), font=("Calibri", 9), width=beaker_width*1.1, anchor="n")
         # Ionenanzeigen neben Elektroden wurden entfernt

    def create_formula_frame(self, parent_frame):
          """Erstellt den Frame zur Anzeige der relevanten Formeln."""
          formula_frame = ttk.LabelFrame(parent_frame, text="Relevante Formeln", padding=10)
          formula_frame.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="nsew")

          self.q_formula_label = ttk.Label(formula_frame, text=" Q = [Prod.] / [Reakt.]", font=("Courier New", 10)) # Angepasster Default

          formulas = [
              "Standard-Zellspannung:",
              " E⁰_cell = E⁰(Kathode) - E⁰(Anode)",
              "", "Reaktionsquotient:",
              self.q_formula_label, # Widget einfügen
              "", "Nernst-Gleichung (bei T):",
              f" E_cell = E⁰_cell - (RT / nF) ln(Q)",
              f"  R = {R:.3f} J/(mol·K)",
              f"  F = {F} C/mol",
              "  n = übertragene e⁻ (Gesamt)",
              "  T = Temperatur in Kelvin",
              "", "Gibbs-Energie (Standard):",
              " ΔG⁰ = -n F E⁰_cell"
          ]

          row_counter = 0
          for item in formulas:
              pady_val = 2
              font_val = ('Calibri', 10)
              anchor_val = "w"
              sticky_val = "w"

              if isinstance(item, tk.Widget):
                  item.grid(row=row_counter, column=0, sticky="ew", padx=5, pady=pady_val)
              elif isinstance(item, str):
                  if not item: lbl_text = ""; pady_val = 4
                  elif item.startswith(" "): lbl_text = item; font_val = ('Courier New', 10)
                  elif item.endswith(":"): lbl_text = item; font_val = ('Calibri', 10, 'bold'); pady_val = (6,2)
                  else: lbl_text = item

                  lbl = ttk.Label(formula_frame, text=lbl_text, font=font_val, anchor=anchor_val)
                  lbl.grid(row=row_counter, column=0, sticky=sticky_val, padx=5, pady=pady_val)
              row_counter += 1

    def create_output_frame(self):
        """Erstellt den Frame für die numerischen Ergebnisse."""
        output_frame = ttk.LabelFrame(self.root, text="Ergebnisse", padding=10)
        output_frame.grid(row=2, column=0, padx=10, pady=(5,10), sticky="ew")
        output_frame.grid_columnconfigure(1, weight=1)
        output_frame.grid_columnconfigure(3, weight=1)

        fnt_bold = ('Calibri', 11, 'bold')
        fnt_normal = ('Calibri', 11)

        ttk.Label(output_frame, text="Standard-Spannung (E⁰):", font=fnt_bold).grid(row=0, column=0, padx=5, pady=4, sticky="w")
        ttk.Label(output_frame, textvariable=self.voltage_var, font=fnt_normal).grid(row=0, column=1, padx=5, pady=4, sticky="w")

        ttk.Label(output_frame, text="Nernst-Spannung (E_cell):", font=fnt_bold).grid(row=1, column=0, padx=5, pady=4, sticky="w")
        ttk.Label(output_frame, textvariable=self.nernst_var, font=fnt_normal).grid(row=1, column=1, padx=5, pady=4, sticky="w")

        ttk.Label(output_frame, text="Reaktionsquotient (Q):", font=fnt_bold).grid(row=0, column=2, padx=15, pady=4, sticky="w")
        ttk.Label(output_frame, textvariable=self.q_display_var, font=fnt_normal).grid(row=0, column=3, padx=5, pady=4, sticky="w")

        ttk.Label(output_frame, text="Standard-Gibbs-Energie (ΔG⁰):", font=fnt_bold).grid(row=1, column=2, padx=15, pady=4, sticky="w")
        ttk.Label(output_frame, textvariable=self.delta_g_var, font=fnt_normal).grid(row=1, column=3, padx=5, pady=4, sticky="w")

    def update_concentration_labels(self):
        """Aktualisiert die Labels für die Konzentrationseingabe."""
        # Stellt sicher, dass series_data initialisiert wurde
        if not hasattr(self, 'series_data'):
             print("Fehler: series_data nicht initialisiert in update_concentration_labels.")
             return

        ano_name = self.anode_var.get()
        cat_name = self.cathode_var.get()
        ano_ion = "[?]"
        cat_ion = "[?]"
        try:
            # Hole Ionenformel nur, wenn ein Name ausgewählt ist
            if ano_name:
                # --- HINWEIS: Prüfe 'ion_formula' und 'color' in utils.py! ---
                ano_ion = self.series_data.get_element_data(ano_name).get("ion_formula", "[?]")
            if cat_name:
                cat_ion = self.series_data.get_element_data(cat_name).get("ion_formula", "[?]")
        except ValueError:
            # Wird ausgelöst, wenn get_element_data das Element nicht findet
            print(f"Warnung: Element nicht gefunden bei Label-Update ({ano_name} / {cat_name})")
        except AttributeError:
             # Wird ausgelöst, wenn series_data nicht die erwartete Struktur hat
             messagebox.showwarning("Datenfehler", "Konnte Elementdaten nicht korrekt laden (AttributeError). Prüfen Sie utils.py.")
             ano_ion = "[?]"; cat_ion = "[?]"
        except Exception as e:
             print(f"Unerwarteter Fehler in update_concentration_labels: {e}")
             ano_ion = "[?]"; cat_ion = "[?]"


        self.anode_conc_label_var.set(f"c({ano_ion}) Anode [mol/L]:")
        self.cathode_conc_label_var.set(f"c({cat_ion}) Kathode [mol/L]:")
        # Diese Variablen werden nicht mehr direkt im Canvas angezeigt
        self.anode_ion_label_var.set(ano_ion)
        self.cathode_ion_label_var.set(cat_ion)

    def handle_selection_change(self, event=None):
        """Wird aufgerufen, wenn Anode oder Kathode geändert wird."""
        self.update_concentration_labels()
        self.calculate_and_update()

    def calculate_and_update(self, event=None):
        """Holt Eingaben, führt Simulation durch und aktualisiert die GUI."""
        # Stellt sicher, dass series_data initialisiert wurde
        if not hasattr(self, 'series_data'):
             messagebox.showerror("Fehler", "series_data nicht initialisiert. Start fehlgeschlagen.")
             return

        anode_name = self.anode_var.get()
        cathode_name = self.cathode_var.get()

        # Prüfe, ob Elemente ausgewählt wurden
        if not anode_name or not cathode_name:
            self.reset_outputs(clear_selection=False)
            try: self.redraw_canvas()
            except Exception: pass
            return


        try:
            # Eingaben validieren
            conc_anode_val = float(self.conc_anode_var.get().replace(',', '.'))
            conc_cathode_val = float(self.conc_cathode_var.get().replace(',', '.'))
            temp_val = float(self.temp_var.get().replace(',', '.'))

            if conc_anode_val <= 0 or conc_cathode_val <= 0: raise ValueError("Konzentrationen müssen > 0 sein.")
            if temp_val <= 0: raise ValueError("Temperatur muss > 0 K sein.")

            # Valide Konzentrationen für Visualisierung speichern
            self.current_conc_anode = conc_anode_val
            self.current_conc_cathode = conc_cathode_val

            # Elementdaten holen
            anode_data = self.series_data.get_element_data(anode_name)
            cathode_data = self.series_data.get_element_data(cathode_name)

            # Simulation initialisieren
            try:
                 # Stellt sicher, dass BatterySimulation in simulation.py vorhanden ist
                 self.current_simulation = BatterySimulation(cathode_element_data=cathode_data, anode_element_data=anode_data)
            except NameError:
                  messagebox.showerror("Fehler", "Klasse 'BatterySimulation' nicht in simulation.py gefunden.")
                  self.reset_outputs(clear_selection=False); self.redraw_canvas(); return
            except ValueError as sim_error: # Fehler innerhalb der Simulation (z.B. ungültiges n)
                 messagebox.showerror("Simulationsfehler", f"Fehler beim Initialisieren:\n{sim_error}")
                 self.reset_outputs(clear_selection=False); self.redraw_canvas(); return
            except AttributeError as data_error: # Fehler, wenn Datenstruktur unerwartet (z.B. 'potential' fehlt)
                 messagebox.showerror("Datenfehler", f"Fehler beim Zugriff auf Elementdaten:\n{data_error}\nPrüfen Sie utils.py.")
                 self.reset_outputs(clear_selection=False); self.redraw_canvas(); return
            except Exception as e: # Andere Fehler bei Initialisierung
                 messagebox.showerror("Simulationsfehler", f"Unerwarteter Fehler bei Simulationsstart:\n{e}")
                 self.reset_outputs(clear_selection=False); self.redraw_canvas(); return

            sim = self.current_simulation
            # Optional: Warnung bei Elektrolyse-Setup
            if sim.anode.potential > sim.cathode.potential: pass

            # Stöchiometrie und Q berechnen
            factor_anode_ion, factor_cathode_ion = sim.get_stoichiometric_factors()
            try:
                 term_anode = conc_anode_val ** factor_anode_ion
                 term_cathode = conc_cathode_val ** factor_cathode_ion
                 if term_cathode == 0: raise ZeroDivisionError("c(Kathode) ist 0.")
                 q_calculated = term_anode / term_cathode
                 if q_calculated <= 0: raise ValueError("Q <= 0.")
            except ZeroDivisionError as e: raise ValueError(f"Q-Berechnungsfehler: {e}") from e
            except OverflowError: raise ValueError("Overflow bei Q-Berechnung.") from None
            except ValueError as e: raise ValueError(f"Q-Berechnungsfehler: {e}") from e
            except Exception as e: raise ValueError(f"Allg. Fehler bei Q-Berechnung: {e}") from e

            # Elektrochemische Werte berechnen
            E0_cell = sim.get_standard_cell_voltage()
            delta_G0 = sim.get_delta_G0()
            E_nernst = sim.get_nernst_voltage(reaction_quotient=q_calculated, temperature=temp_val)

            # GUI-Variablen aktualisieren
            self.voltage_var.set(f"{E0_cell:.3f} V")
            self.delta_g_var.set(f"{delta_G0 / 1000:.2f} kJ/mol")
            self.nernst_var.set(f"{E_nernst:.3f} V") # Spannung mit Einheit für redraw_canvas
            self.q_display_var.set(f"{q_calculated:.3e}")
            self.anode_reaction_var.set(sim.get_anode_reaction())
            self.cathode_reaction_var.set(sim.get_cathode_reaction())

            # Q-Formel aktualisieren (mit Fallback)
            # --- HINWEIS: Prüfe 'ion_formula' in utils.py für korrekte Anzeige! ---
            ano_ion_f = sim.anode.ion_formula if hasattr(sim.anode, 'ion_formula') else "?"
            cat_ion_f = sim.cathode.ion_formula if hasattr(sim.cathode, 'ion_formula') else "?"
            fac_a = factor_anode_ion if isinstance(factor_anode_ion, int) else "?"
            fac_c = factor_cathode_ion if isinstance(factor_cathode_ion, int) else "?"
            if ano_ion_f != "?" and cat_ion_f != "?":
                 q_formel_str = f" Q = [{ano_ion_f}]^{fac_a} / [{cat_ion_f}]^{fac_c}"
            else:
                 q_formel_str = f" Q = [Prod.]^{fac_a} / [Reakt.]^{fac_c}" # Fallback
            # Stelle sicher, dass das Label existiert, bevor config aufgerufen wird
            if hasattr(self, 'q_formula_label') and self.q_formula_label:
                self.q_formula_label.config(text=q_formel_str)
            else:
                print("Warnung: q_formula_label nicht gefunden zum Konfigurieren.")


            # Canvas neu zeichnen
            self.redraw_canvas()

        except ValueError as e: # Fängt Validierungs- und Berechnungsfehler
            messagebox.showerror("Eingabe-/Berechnungsfehler", f"Fehler: {e}")
            self.reset_outputs(clear_selection=False); self.redraw_canvas()
        except Exception as e: # Fängt alle anderen Fehler ab
            import traceback
            print("------ UNERWARTETER FEHLER ------"); traceback.print_exc(); print("-------------------------------")
            messagebox.showerror("Allgemeiner Fehler", f"Unerwarteter Fehler:\n{type(e).__name__}: {e}\nDetails siehe Konsole.")
            self.reset_outputs(clear_selection=False); self.redraw_canvas()


    def reset_outputs(self, clear_selection=True):
         """Setzt die Ausgabefelder und Schema-Infos zurück."""
         # Reset Visualisierungs-Konzentrationen
         self.current_conc_anode = 1.0
         self.current_conc_cathode = 1.0

         # Reset Ausgabe-Variablen
         self.voltage_var.set("E⁰: --- V")
         self.delta_g_var.set("ΔG⁰: --- kJ/mol")
         self.nernst_var.set("E_Nernst: --- V") # Setzt auch Text für redraw zurück
         self.q_display_var.set("Q: ---")
         self.anode_reaction_var.set("Anodenreaktion (Oxidation)")
         self.cathode_reaction_var.set("Kathodenreaktion (Reduktion)")
         self.anode_ion_label_var.set("Anoden-Ion")
         self.cathode_ion_label_var.set("Kathoden-Ion")

         # Reset Q-Formel-Label (falls vorhanden)
         if hasattr(self, 'q_formula_label') and self.q_formula_label:
             self.q_formula_label.config(text=" Q = [Prod.] / [Reakt.]")

         # Reset Simulationsobjekt
         self.current_simulation = None

         # Optional: Auswahl zurücksetzen
         if clear_selection:
              self.anode_var.set("")
              self.cathode_var.set("")
              self.update_concentration_labels() # Aktualisiert c(...) Labels


# --- Hauptprogramm ---
if __name__ == "__main__":
    root = tk.Tk()
    app = BatteryApp(root)
    # Stelle sicher, dass das Fenster initial gezeichnet wird
    root.update_idletasks() # Verarbeitet anstehende Aufgaben wie Geometrie
    try:
        app.redraw_canvas() # Zeichne initial (könnte leer sein, wenn keine Defaults)
    except tk.TclError as e:
         if "invalid command name" in str(e):
               print("Warnung: Initiales Zeichnen fehlgeschlagen (Fenster ggf. noch nicht bereit).")
         else:
               raise e # Anderer TclError
    except Exception as e:
        print(f"Fehler beim initialen Zeichnen: {e}")

    root.mainloop()