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
# Version: 1.0.0
# Datum: 2025-06-10
# ----------------------------------------------------------



# -*- coding: utf-8 -*-
import tkinter as tk
import os # Importiere das os-Modul
from tkinter import simpledialog, messagebox
from buchladen_logik import Buchladen
from buchladen_gui import BuchladenApp, AddBookWindow # AddBookWindow importieren
from buch_model import Buch # Für den Testblock

# Bestimme den Pfad zum aktuellen Skriptverzeichnis
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Erstelle den absoluten Pfad zur JSON-Datei
JSON_DATEIPFAD = os.path.join(SCRIPT_DIR, "buecher.json")


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
    # Erstelle das Hauptfenster für die Buchladen-Anwendung (Kaufen-Modus)
    root = tk.Tk()

    # Erstelle die Buchladen-Logik-Instanz und lade die Daten
    mein_buchladen = Buchladen("Das Leseparadies Online")
    mein_buchladen.lade_buecher_aus_json(JSON_DATEIPFAD)

    # Prüfe, ob Bücher geladen wurden
    if not mein_buchladen.inventar:
        messagebox.showwarning("Keine Bücher", "Das Inventar ist leer. Bitte prüfen Sie die 'buecher.json'.", parent=root)
        # Optional: App schließen, wenn keine Bücher da sind
        # root.destroy()
        # return

    # Erstelle die GUI-Anwendungs-Instanz
    app = BuchladenApp(root, mein_buchladen, JSON_DATEIPFAD)
    root.mainloop()

if __name__ == "__main__":
    run_backend_tests() # Führe zuerst die Backend-Tests aus
    main()
