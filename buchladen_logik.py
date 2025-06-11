# -*- coding: utf-8 -*-
import json
from buch_model import Buch # Importiere die Buch-Klasse

class Buchladen:
    """Repräsentiert einen Online-Buchladen mit einem Inventar an Büchern."""
    def __init__(self, name: str):
        self.name = name
        self.inventar = []

    def buch_hinzufuegen(self, buch: Buch):
        if isinstance(buch, Buch):
            self.inventar.append(buch)
        else:
            print("Fehler: Es können nur Buch-Objekte hinzugefügt werden.")

    def lade_buecher_aus_json(self, dateipfad: str):
        """Lädt Bücher aus einer JSON-Datei in das Inventar."""
        try:
            with open(dateipfad, 'r', encoding='utf-8') as f:
                buecher_daten = json.load(f)
                for item in buecher_daten:
                    buch = Buch(
                        titel=item.get('titel', 'Unbekannter Titel'),
                        autor=item.get('autor', 'Unbekannter Autor'),
                        kategorie=item.get('kategorie', 'Unbekannte Kategorie'),
                        preis=float(item.get('preis', 0.0)),
                        verboten=bool(item.get('verboten', False)),
                        indiziert=bool(item.get('indiziert', False)),
                        image_path=item.get('image_path', None) # Bildpfad optional
                    )
                    self.buch_hinzufuegen(buch)
            print(f"{len(self.inventar)} Bücher erfolgreich aus '{dateipfad}' geladen.")
        except FileNotFoundError:
            print(f"Fehler: JSON-Datei '{dateipfad}' nicht gefunden.")
        except json.JSONDecodeError:
            print(f"Fehler: JSON-Datei '{dateipfad}' konnte nicht dekodiert werden.")
        except Exception as e:
            print(f"Ein unerwarteter Fehler ist beim Laden der Bücher aufgetreten: {e}")

    def berechne_gesamtpreis(self, buch_auswahl: list) -> float:
        """Berechnet den Gesamtpreis für eine Auswahl an Büchern, exklusive verbotener/indizierter."""
        return sum(buch.preis for buch in buch_auswahl if not buch.verboten)

    def suche_nach_kategorie(self, kategorie_suche: str) -> list:
        """Durchsucht das Inventar nach Büchern einer bestimmten Kategorie (case-insensitive)."""
        if not kategorie_suche or kategorie_suche.lower() == "alle anzeigen":
            return list(self.inventar) # Gibt eine Kopie des gesamten Inventars zurück
            
        gefundene_buecher = []
        for buch in self.inventar:
            if buch.kategorie.lower() == kategorie_suche.lower():
                gefundene_buecher.append(buch)
        return gefundene_buecher

    def get_gefilterte_buecher(self, filter_kriterium: str) -> list:
        """Gibt eine Liste von Büchern basierend auf dem Filterkriterium zurück."""
        if not filter_kriterium or filter_kriterium.lower() == "alle anzeigen":
            return list(self.inventar)
        elif filter_kriterium.lower() == "nur fsk18":
            return [buch for buch in self.inventar if buch.indiziert and not buch.verboten]
        elif filter_kriterium.lower() == "nur verbotene":
            return [buch for buch in self.inventar if buch.verboten]
        else: # Annahme: Es ist ein Kategoriename
            return self.suche_nach_kategorie(filter_kriterium)

    def get_alle_kategorien(self) -> list:
        """Gibt eine Liste aller einzigartigen Kategorien im Inventar zurück."""
        kategorien = set()
        for buch in self.inventar:
            kategorien.add(buch.kategorie)
        return sorted(list(kategorien))

    def speichere_inventar_in_json(self, dateipfad: str):
        """Speichert das aktuelle Inventar als JSON in die angegebene Datei."""
        buecher_daten_liste = []
        for buch in self.inventar:
            buch_dict = {
                "titel": buch.titel,
                "autor": buch.autor,
                "kategorie": buch.kategorie,
                "preis": buch.preis,
                "verboten": buch.verboten,
                "indiziert": buch.indiziert
            }
            if buch.image_path:
                buch_dict["image_path"] = buch.image_path
            buecher_daten_liste.append(buch_dict)
        try:
            with open(dateipfad, 'w', encoding='utf-8') as f:
                json.dump(buecher_daten_liste, f, indent=2, ensure_ascii=False)
            print(f"Inventar erfolgreich in '{dateipfad}' gespeichert.")
        except Exception as e:
            print(f"Fehler beim Speichern des Inventars in JSON: {e}")
