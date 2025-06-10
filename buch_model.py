# ----------------------------------------------------------
# buch_model.py
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



class Buch:
    """Repräsentiert ein einzelnes Buch mit Titel, Autor, Kategorie und Preis."""
    def __init__(self, titel: str, autor: str, kategorie: str, preis: float, verboten: bool = False, indiziert: bool = False):
        self.titel = titel
        self.autor = autor
        self.kategorie = kategorie
        self.preis = preis
        self.verboten = verboten
        self.indiziert = indiziert

    def __str__(self) -> str:
        """Gibt eine benutzerfreundliche Zeichenkette für das Buch zurück."""
        status = ""
        if self.verboten:
            status = " [VERBOTEN]"
        elif self.indiziert:
            status = " [INDIZIERT FSK18]"
        
        preis_str = "{:.2f}".format(self.preis).replace('.', ',')
        return f"'{self.titel}' von {self.autor} ({preis_str} €){status}"

    def __repr__(self) -> str:
        """Gibt eine eindeutige, technische Repräsentation des Objekts zurück."""
        return f"Buch(titel='{self.titel}', autor='{self.autor}', preis={self.preis}, verboten={self.verboten}, indiziert={self.indiziert})"

