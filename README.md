# Battery Simulation and Data Retrieval

This project provides a simulation of battery reactions using the electrochemical series and data on various battery materials. It retrieves relevant data from PubChem, scrapes electrochemical potential data, and uses SQLite for caching. A simple graphical user interface (GUI) built with Tkinter allows users to input reduction and oxidation elements to calculate the cell voltage of a battery.

## Features

- **Data Caching**: Uses SQLite to cache data with timestamps for improved performance.
- **Electrochemical Series Scraping**: Scrapes the electrochemical series from Wikipedia.
- **Battery Material Data**: Retrieves data for battery materials such as Lithium, Cobalt, Graphite, etc., using PubChem.
- **Battery Reaction Simulation**: Simulates the cell voltage for a battery using reduction and oxidation elements.
- **GUI**: A simple Tkinter-based GUI to input elements and calculate the cell voltage.

## Requirements

- Python 3.x
- `requests`
- `beautifulsoup4`
- `pubchempy`
- `pandas`
- `sqlite3`
- `tkinter`

To install the necessary dependencies, you can use the following command:

```bash
pip install requests beautifulsoup4 pubchempy pandas
