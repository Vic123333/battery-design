# Galvanic Cell Simulation

This project is a Python application that simulates a galvanic cell, allowing users to explore the electrochemical principles behind battery operation. It provides a graphical user interface (GUI) built with `tkinter` to visualize the cell, input parameters, and display calculation results.

![Screenshot 2025-04-03 000655](https://github.com/user-attachments/assets/ae39c777-f9dc-42fd-bbbe-4265d64f01aa)


## Features

-   **Interactive GUI:** User-friendly interface to select anode and cathode materials, input concentrations, and temperature.
-   **Electrochemical Series Data:** Utilizes data from an electrochemical series (loaded from `utils.py`) to calculate cell potentials.
-   **Nernst Equation Calculations:** Computes the cell potential under non-standard conditions using the Nernst equation.
-   **Gibbs Free Energy Calculation:** Calculates the standard Gibbs free energy change of the cell reaction.
-   **Visualization:** Schematic representation of the galvanic cell, including electrodes, electrolytes, salt bridge, and voltmeter.
-   **Dynamic Visualization:** Visualization of the Electrolyte level changes based on the concentration of the ion.
-   **Reaction Display:** Shows the anode (oxidation) and cathode (reduction) reactions.
-   **Stoichiometry and Reaction Quotient (Q) Calculation:** Shows the relevant formulas and values.
-   **Error Handling:** Robust error handling for invalid inputs and data loading issues.

## Dependencies

-   Python 3.x
-   `tkinter` (standard library)

## Project Structure

-   `gui.py`: Contains the main application logic and GUI implementation.
-   `utils.py`: Provides the `ElectrochemicalSeries` class to load and manage electrochemical data.
-   `simulation.py`: Contains the `BatterySimulation` and `ElectrochemicalElement` classes for electrochemical calculations.

## How to Run

1.  Ensure you have Python 3.x installed.
2.  Clone the repository or download the source files.
3.  Make sure `utils.py` and `simulation.py` are in the same directory as `gui.py`.
4.  Run `gui.py` using Python:

    ```bash
    python gui.py
    ```


## Usage

1.  Select the anode and cathode materials from the dropdown menus.
2.  Enter the concentrations of the anode and cathode ions (in mol/L).
3.  Enter the temperature (in Kelvin).
4.  Click the "Berechnen" (Calculate) button to perform the calculations.
5.  The results, including standard cell potential, Nernst potential, Gibbs free energy, and reaction quotient, will be displayed.
6.  The galvanic cell will be visualized in the "Zell-Schema" (Cell Scheme) frame.

## Code Explanation

-   `gui.py` uses `tkinter` to create the GUI, including labels, entry fields, dropdown menus, and a canvas for visualization.
-   The `BatteryApp` class handles the GUI logic, user input, and calculation results.
-   `utils.py` loads electrochemical data from a file or data source, providing element information like standard reduction potentials and reactions.
-   `simulation.py` performs the electrochemical calculations using the Nernst equation and Gibbs free energy formula.
-   The `redraw_canvas` method dynamically draws the galvanic cell based on the input parameters and calculation results.
-   Error handling is implemented to catch invalid inputs and data loading issues, displaying informative error messages to the user.

## Future Improvements

-   Add support for more complex cell configurations.
-   Implement a database or external data source for electrochemical series data.
-   Enhance the visualization with animations and more detailed representations.
-   Add the option to save and load simulation results.
-   Implement a more robust input validation.
-   Add more information to the visualisation, like Ionenflow in the salt bridge.

## Contributing

Contributions are welcome! If you find any bugs or have suggestions for improvements, please open an issue or submit a pull request.
