# ----------------------------------------------------------
# main.py
#
# Copyright (c) 2025 Phillip Leupold
# Lizenz: MIT License
# (Mehr Details zur Lizenz in einer separaten LICENSE-Datei)
#
# Aufgabe_easy
# Thema: Buchladen mit GUI
#
# Beschreibung: Siehe ggf. # Ziel: weiter unten
#
# @autor: Phillip Leupold
# Version: 0.9.0
# Datum: 2025-06-10
# ----------------------------------------------------------



# -*- coding: utf-8 -*-
import tkinter as tk
import os
import sys # To check if running as a PyInstaller bundle
import shutil # For copying files
from tkinter import simpledialog, messagebox
from buchladen_logik import Buchladen
from buchladen_gui import BuchladenApp # AddBookWindow is imported within BuchladenApp
from buch_model import Buch

# --- Configuration ---
APP_NAME = "DasLeseparadies" # Used for creating the AppData folder
DEFAULT_JSON_FILENAME = "buecher.json"

# --- Helper function to get the correct path ---
def get_resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS # type: ignore[attr-defined]
    except AttributeError: # More specific: catch only if _MEIPASS is not found
        # Not running in a PyInstaller bundle, use script directory
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def get_app_data_dir(app_name: str) -> str:
    """Gets the application data directory, creating it if it doesn't exist."""
    path: str # Define type for path

    if sys.platform == "win32":
        appdata_env_val = os.getenv('APPDATA')
        if appdata_env_val: # Check if the environment variable exists and is not empty
            path = os.path.join(appdata_env_val, app_name)
        else:
            # Fallback if APPDATA is not set or empty on Windows
            print(f"Warning: APPDATA environment variable not set or empty. Using fallback directory in user's home for {app_name}.")
            path = os.path.join(os.path.expanduser('~'), '.' + app_name.lower().replace(" ", "_") + "_win_fallback")
    # The original code had commented-out elifs for other platforms.
    # The final 'else' was the fallback for non-Windows systems.
    else: # Fallback for non-Windows OS (e.g., Linux, macOS if not handled by specific elif)
        path = os.path.join(os.path.expanduser('~'), '.' + app_name.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)
    return path

# --- Determine paths ---
# SCRIPT_DIR is still useful for development or if not bundled
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Path for the user-specific, writable JSON file
USER_APP_DATA_DIR = get_app_data_dir(APP_NAME)
USER_JSON_DATEIPFAD = os.path.join(USER_APP_DATA_DIR, DEFAULT_JSON_FILENAME)

# Path to the (potentially) bundled default JSON file
# This will be used if the user-specific one doesn't exist yet.
BUNDLED_DEFAULT_JSON_PATH = get_resource_path(DEFAULT_JSON_FILENAME)


def run_backend_tests():
    """Führt die Backend-Tests aus, wie zuvor definiert."""
    print("--- Backend Test Start ---")
    buch1 = Buch("Python Crashkurs", "Eric Matthes", "Programmierung", 30.00)
    buch2 = Buch("Der Pragmatische Programmierer", "Andrew Hunt", "Programmierung", 25.50)
    buch3 = Buch("Faust I", "Johann Wolfgang von Goethe", "Klassiker", 7.99)
    buch4 = Buch("Die Verwandlung", "Franz Kafka", "Klassiker", 5.00, indiziert=True)

    test_laden = Buchladen("Test-Buchladen")
    test_laden.buch_hinzufuegen(buch1)
    test_laden.buch_hinzufuegen(buch2)
    test_laden.buch_hinzufuegen(buch3)
    test_laden.buch_hinzufuegen(buch4)

    print(f"\nInventar im '{test_laden.name}':")
    for buch_item in test_laden.inventar:
        print(f"- {buch_item}")
 
    print("\nSuche nach Kategorie 'Programmierung':")
    prog_buecher = test_laden.suche_nach_kategorie("Programmierung")
    for buch_item in prog_buecher:
        print(f"- {buch_item}")
    
    print("\nSuche nach 'Nur FSK18':")
    fsk_buecher = test_laden.get_gefilterte_buecher("Nur FSK18")
    for buch_item in fsk_buecher:
        print(f"- {buch_item}")

    auswahl = [buch1, buch3, buch4]
    gesamtpreis_test = test_laden.berechne_gesamtpreis(auswahl)
    print(f"\nGesamtpreis für Auswahl ({[str(b) for b in auswahl]}): {gesamtpreis_test:.2f} €")
    print("--- Backend Test Ende ---\n")


def main():
    # Ensure the user-specific JSON exists, copy from bundle if not
    if not os.path.exists(USER_JSON_DATEIPFAD):
        if os.path.exists(BUNDLED_DEFAULT_JSON_PATH):
            try:
                shutil.copy2(BUNDLED_DEFAULT_JSON_PATH, USER_JSON_DATEIPFAD)
                print(f"Copied default data file to {USER_JSON_DATEIPFAD}")
            except Exception as e:
                messagebox.showerror("Fehler beim Initialisieren",
                                     f"Konnte die Standard-Datendatei nicht nach {USER_JSON_DATEIPFAD} kopieren.\nFehler: {e}")
                return # Critical error, cannot proceed
        else:
            # This case should ideally not happen if PyInstaller is configured correctly
            # or if running in dev mode with buecher.json present.
            # We can create an empty JSON array as a last resort.
            print(f"Warnung: Weder Benutzer-JSON noch Standard-JSON ({BUNDLED_DEFAULT_JSON_PATH}) gefunden. Erstelle leere Datei in {USER_JSON_DATEIPFAD}.")
            try:
                with open(USER_JSON_DATEIPFAD, 'w', encoding='utf-8') as f:
                    f.write("[]") # Create an empty JSON list
            except Exception as e:
                messagebox.showerror("Fehler beim Initialisieren",
                                     f"Konnte keine leere Datendatei in {USER_JSON_DATEIPFAD} erstellen.\nFehler: {e}")
                return # Critical error

    # Erstelle das Hauptfenster für die Buchladen-Anwendung
    root = tk.Tk()
    # For consistency with BuchladenApp, let's use ctk.CTk() if it's the main window.
    # However, BuchladenApp takes `root_window` which can be tk.Tk or ctk.CTk.
    # If BuchladenApp internally sets appearance mode, tk.Tk() is fine here.

    # Erstelle die Buchladen-Logik-Instanz und lade die Daten
    # Now always use the USER_JSON_DATEIPFAD
    mein_buchladen = Buchladen("Das Leseparadies Online")
    mein_buchladen.lade_buecher_aus_json(USER_JSON_DATEIPFAD)

    # Prüfe, ob Bücher geladen wurden (oder ob die Datei leer ist nach Initialisierung)
    if not mein_buchladen.inventar:
        # Only show warning if the file existed and was empty, or failed to load for other reasons
        # The copy mechanism above should handle the "file not found" for the first run.
        if os.path.exists(USER_JSON_DATEIPFAD): # Check if it's not a loading error of an existing file
             messagebox.showwarning("Inventar Leer",
                                   f"Das Inventar ist leer. Sie können Bücher über 'Datei -> Buch hinzufügen' hinzufügen.\nDatendatei: {USER_JSON_DATEIPFAD}",
                                   parent=root)
        # No need to exit, user can add books.

    # Erstelle die GUI-Anwendungs-Instanz, passing the user-specific JSON path
    app = BuchladenApp(
        root_window=root,
        buchladen_instanz=mein_buchladen,
        json_dateipfad=USER_JSON_DATEIPFAD,
        get_resource_path_func=get_resource_path,
        user_app_data_dir=USER_APP_DATA_DIR)
    root.mainloop()

if __name__ == "__main__":
    # run_backend_tests() # Führe zuerst die Backend-Tests aus
    main()
