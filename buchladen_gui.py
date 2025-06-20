# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk  # Only for messagebox/simpledialog
import os
from tkinter import messagebox, simpledialog
from buch_model import Buch
from PIL import Image, ImageTk
from buchladen_logik import Buchladen
import requests # For image downloading
import json # For handling JSONDecodeError
import urllib.parse # For URL encoding image search query
import time # For potential rate limiting (though less critical for single downloads)


# Globale Design-Konstanten (könnten auch in eine config.py)
FONT_FAMILY = "Constantia"
FONT_SIZE_DEFAULT = 12
FONT_SIZE_LISTBOX = 12
FONT_SIZE_BUTTON = 11
FONT_SIZE_TOTAL_LABEL = 14
FONT_SIZE_LABELFRAME_TITLE = 12

COLOR_BUTTON_BG = "#F5F5F5"
COLOR_BUTTON_FG = "#424242"
COLOR_BUTTON_HOVER_BG = "#E0E0E0"
COLOR_BUTTON_PRESSED_BG = "#BDBDBD"

COLOR_BUTTON_PRIMARY_BG = "#2196F3"
COLOR_BUTTON_PRIMARY_FG = "#FFFFFF"
COLOR_BUTTON_PRIMARY_HOVER_BG = "#1976D2"
COLOR_BUTTON_PRIMARY_PRESSED_BG = "#0D47A1"


class BuchladenApp:
    def __init__(self, root_window, buchladen_instanz: Buchladen, json_dateipfad: str, get_resource_path_func, user_app_data_dir: str):
        self.root = root_window
        self.buchladen = buchladen_instanz
        self.json_dateipfad = json_dateipfad # JSON-Pfad speichern
        self.einkaufswagen = []
        self.aktuell_angezeigte_buecher = [] # Wichtig für korrekte Auswahl
        self.user_app_data_dir = user_app_data_dir # Store user's app data directory path
        self.get_resource_path = get_resource_path_func # Store the path resolving function

        self.buch_bild_label = None # Initialisiere das Bild-Label Attribut
        self.root.title("Das Leseparadies - GUI")
        self.root.geometry("1200x650") # Etwas mehr Höhe für das Dropdown
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("dark-blue")

        self.selected_inventar_index = None
        self.selected_wagen_index = None

        self._erstelle_widgets()
        self._update_inventar_anzeige() # Initiales Füllen mit allen Büchern
        self._erstelle_menuleiste() # Menüleiste erstellen

    def _erstelle_widgets(self):
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Filter Frame ---
        filter_frame = ctk.CTkFrame(main_frame)
        filter_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=(0,10), sticky="ew")
        
        ctk.CTkLabel(filter_frame, text="Kategorie filtern:", font=(FONT_FAMILY, FONT_SIZE_DEFAULT, "bold")).pack(side="left", padx=(0,5))
        
        self.kategorie_filter_var = tk.StringVar()
        filter_optionen = ["Alle Anzeigen"] + self.buchladen.get_alle_kategorien() + ["Nur FSK18", "Nur Verbotene"]
        self.kategorie_dropdown = ctk.CTkComboBox(filter_frame, 
                                                  variable=self.kategorie_filter_var, 
                                                  values=filter_optionen, 
                                                  width=200, 
                                                  state="readonly",
                                                  command=self._on_filter_change) # Use command
        self.kategorie_dropdown.pack(side="left", padx=5)
        self.kategorie_dropdown.set("Alle Anzeigen")

        # --- Linke Spalte: Inventar ---
        inventar_frame = ctk.CTkFrame(main_frame)
        inventar_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        inventar_frame.rowconfigure(0, weight=1)
        inventar_frame.columnconfigure(0, weight=1)

        # Stelle sicher, dass CTkScrollableFrame verwendet wird!
        self.inventar_scroll = ctk.CTkScrollableFrame(inventar_frame, width=400, height=400)
        self.inventar_scroll.grid(row=0, column=0, sticky="nswe", padx=(5,0), pady=(5,0))

        # --- Mittlere Spalte: Buttons ---
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=1, column=1, padx=10, pady=5, sticky="n")
        self.add_button = ctk.CTkButton(button_frame, text=">> In den Wagen", command=self._zum_wagen_hinzufuegen)
        self.add_button.configure(state="disabled")
        self.add_button.pack(pady=20, fill="x")
        self.remove_button = ctk.CTkButton(button_frame, text="<< Entfernen", command=self._aus_dem_wagen_entfernen)
        self.remove_button.pack(pady=5, fill="x")

        # --- Rechte Spalte: Einkaufswagen ---
        wagen_frame = ctk.CTkFrame(main_frame)
        wagen_frame.grid(row=1, column=2, padx=5, pady=5, sticky="nswe")
        wagen_frame.rowconfigure(0, weight=1)
        wagen_frame.columnconfigure(0, weight=1)

        self.wagen_scroll = ctk.CTkScrollableFrame(wagen_frame, width=400, height=400)
        self.wagen_scroll.grid(row=0, column=0, sticky="nswe", padx=(5,0), pady=(5,0))

        # --- Bildanzeige (Neue Spalte 3) ---
        image_frame = ctk.CTkFrame(main_frame)
        image_frame.grid(row=1, column=3, padx=5, pady=5, sticky="nsew")
        self.buch_bild_label = ctk.CTkLabel(image_frame, text="") # Label für das Bild
        self.buch_bild_label.pack()

        # --- Untere Zeile: Gesamtpreis und Kasse ---
        kasse_frame = ctk.CTkFrame(main_frame)
        kasse_frame.grid(row=2, column=0, columnspan=4, pady=(15, 10), sticky="ew") # Spaltenspan anpassen
        self.total_label_var = tk.StringVar(value="Gesamtpreis: 0,00 €")
        total_label = ctk.CTkLabel(kasse_frame, textvariable=self.total_label_var, font=(FONT_FAMILY, FONT_SIZE_TOTAL_LABEL, "bold"))
        total_label.pack(side="left", padx=10)
        self.kasse_button = ctk.CTkButton(kasse_frame, text="Zur Kasse", command=self._zur_kasse)
        self.kasse_button.pack(side="right", padx=10)

        main_frame.rowconfigure(1, weight=1) # Inventar/Wagen-Zeile soll skalieren
        main_frame.columnconfigure(0, weight=1) # Inventar-Spalte
        main_frame.columnconfigure(2, weight=1) # Wagen-Spalte
        main_frame.columnconfigure(3, weight=1) # Bild-Spalte (jetzt skalierend)
        main_frame.columnconfigure(1, weight=0) # Button-Spalte nicht

    def _erstelle_menuleiste(self):
        menubar = tk.Menu(self.root)
        datei_menu = tk.Menu(menubar, tearoff=0)
        datei_menu.add_command(label="Buch hinzufügen", command=self._buch_hinzufuegen_dialog)
        datei_menu.add_separator()
        datei_menu.add_command(label="Beenden", command=self.root.quit)
        menubar.add_cascade(label="Datei", menu=datei_menu)
        self.root.config(menu=menubar)

    def _buch_hinzufuegen_dialog(self):
        # AddBookWindow als modalen Dialog starten und auf sein Schließen warten
        add_window = AddBookWindow(self.root, self.buchladen, self.json_dateipfad, self.user_app_data_dir)
        self.root.wait_window(add_window) # Warten, bis das AddBookWindow geschlossen wird

        # Inventarliste und Filter-Dropdown in BuchladenApp aktualisieren
        self._aktualisiere_gui_nach_buch_hinzugefuegt()

    def _aktualisiere_gui_nach_buch_hinzugefuegt(self):
        """Aktualisiert die Inventaranzeige und die Filteroptionen."""
        self._update_inventar_anzeige(self.kategorie_filter_var.get()) # Aktuellen Filter beibehalten

        neue_filter_optionen = ["Alle Anzeigen"] + self.buchladen.get_alle_kategorien() + ["Nur FSK18", "Nur Verbotene"]
        self.kategorie_dropdown['values'] = neue_filter_optionen
        
        current_filter_value = self.kategorie_filter_var.get()
        if current_filter_value not in neue_filter_optionen: # Falls der alte Filter (eine gelöschte Kat.?) nicht mehr existiert
            self.kategorie_dropdown.set("Alle Anzeigen") # Auf "Alle Anzeigen" zurücksetzen
            self._on_filter_change() # Und die Anzeige entsprechend aktualisieren
            # Note: If _on_filter_change is called without args here, it needs to handle that.
            # The command callback provides an arg, but direct calls might not.
            # For simplicity, assuming this programmatic call will use the new value from .set()

    def _on_filter_change(self, filter_wert: str | None = None): # Modified signature
        """Wird aufgerufen, wenn eine Auswahl im Dropdown getroffen oder der Filter programmatisch geändert wird."""
        if filter_wert is None: # Handle programmatic calls that don't pass the value (e.g. from _aktualisiere_gui_nach_buch_hinzugefuegt)
            filter_wert = self.kategorie_filter_var.get()
        self._update_inventar_anzeige(filter_wert)

    def _update_inventar_anzeige(self, filter_kriterium=None):
        """Aktualisiert die Inventar-Listbox basierend auf dem Filter."""
        if filter_kriterium is None:
            filter_kriterium = "Alle Anzeigen"
        
        self.aktuell_angezeigte_buecher = self.buchladen.get_gefilterte_buecher(filter_kriterium)
        self._fuelle_inventar_liste_mit_buechern(self.aktuell_angezeigte_buecher)

    def _fuelle_inventar_liste_mit_buechern(self, buecher_liste: list):
        """Füllt die Listbox des Inventars mit den übergebenen Büchern."""
        print(f"DEBUG: _fuelle_inventar_liste_mit_buechern erhält {len(buecher_liste)} Bücher zum Anzeigen.") # DEBUG-Ausgabe
        # Clear previous widgets
        for widget in self.inventar_scroll.winfo_children():
            widget.destroy()
        self.selected_inventar_index = None
        self.add_button.configure(state="disabled")
        self._clear_buch_bild()
        self._inventar_buttons = []

        def on_select(idx):
            self.selected_inventar_index = idx
            self._zeige_buch_bild(self.aktuell_angezeigte_buecher[idx])
            self.add_button.configure(state="normal")
            for i, btn in enumerate(self._inventar_buttons):
                if i == idx:
                    btn.configure(state="disabled")
                else:
                    btn.configure(state="normal")

        for idx, buch in enumerate(buecher_liste):
            preis_str = "{:.2f} €".format(buch.preis).replace('.', ',')
            btn_text = f"{buch.titel}\n{buch.autor}   {preis_str}"
            btn = ctk.CTkButton(
                self.inventar_scroll,
                text=btn_text,
                anchor="w",
                width=380,
                height=48,
                command=lambda i=idx: on_select(i)
            )
            btn.pack(fill="x", pady=3, padx=5)  # Einheitliche Abstände
            self._inventar_buttons.append(btn)
        self.root.update()

    def _aktualisiere_wagen_anzeige(self):
        for widget in self.wagen_scroll.winfo_children():
            widget.destroy()
        self.selected_wagen_index = None
        self._wagen_buttons = []

        def on_select(idx):
            self.selected_wagen_index = idx
            # Visuelles Feedback für Auswahl (Button-Relief ändern, keine Farbe)
            for i, btn in enumerate(self._wagen_buttons):
                if i == idx:
                    btn.configure(state="disabled")
                else:
                    btn.configure(state="normal")

        for idx, buch in enumerate(self.einkaufswagen):
            preis_str = "{:.2f} €".format(buch.preis).replace('.', ',')
            btn_text = f"{buch.titel}\n{buch.autor}   {preis_str}"
            btn = ctk.CTkButton(
                self.wagen_scroll,
                text=btn_text,
                anchor="w",
                width=380,
                height=48,
                command=lambda i=idx: on_select(i)
            )
            btn.pack(fill="x", pady=3, padx=5)  # Einheitliche Abstände
            self._wagen_buttons.append(btn)

        gesamtpreis = self.buchladen.berechne_gesamtpreis(self.einkaufswagen)
        gesamtpreis_str = "{:.2f}".format(gesamtpreis).replace('.', ',')
        self.total_label_var.set(f"Gesamtpreis: {gesamtpreis_str} €")

    def _zum_wagen_hinzufuegen(self):
        try:
            idx = self.selected_inventar_index
            if idx is None:
                return
            buch_objekt = self.aktuell_angezeigte_buecher[idx]

            if buch_objekt.verboten:
                messagebox.showwarning("Nicht verfügbar", f"Das Buch '{buch_objekt.titel}' ist nicht verkäuflich.", parent=self.root)
                return
            if buch_objekt.indiziert:
                antwort = messagebox.askyesno(
                    "Altersüberprüfung", 
                    f"Das Buch '{buch_objekt.titel}' ist mit FSK18 gekennzeichnet.\n\nSind Sie mindestens 18 Jahre alt?",
                    parent=self.root
                )
                if not antwort: # Benutzer hat "Nein" geklickt oder Dialog geschlossen
                    messagebox.showinfo("Hinweis", "Das Buch wurde aufgrund der Altersbeschränkung nicht in den Warenkorb gelegt.", parent=self.root)
                    return
            
            # Wenn wir hier ankommen, ist das Buch nicht verboten, 
            # und falls es indiziert war, wurde das Alter bestätigt.
            self.einkaufswagen.append(buch_objekt)
            self._aktualisiere_wagen_anzeige()
        except IndexError:
            # Dieser Fehler sollte seltener auftreten, wenn aktuell_angezeigte_buecher korrekt ist
            messagebox.showerror("Fehler", "Auswahl konnte nicht verarbeitet werden. Bitte versuchen Sie es erneut.", parent=self.root)
            # Optionale Debug-Ausgabe für Entwickler:
            # selected_indices_debug = self.inventar_listbox.cureselection() # Erneut abrufen für den Fall, dass es sich geändert hat
            # print(f"DEBUG: IndexError in _zum_wagen_hinzufuegen. Selected indices: {selected_indices_debug}, len(aktuell_angezeigte_buecher): {len(self.aktuell_angezeigte_buecher)}")
        except Exception as e:
            messagebox.showerror("Unerwarteter Fehler", f"Ein Fehler ist aufgetreten: {e}", parent=self.root)
            
    def _aus_dem_wagen_entfernen(self):
        try:
            idx = self.selected_wagen_index
            if idx is None:
                return
            del self.einkaufswagen[idx]
            self._aktualisiere_wagen_anzeige()
        except IndexError:
            messagebox.showerror("Fehler", "Auswahl konnte nicht verarbeitet werden.", parent=self.root)

    def _zur_kasse(self):
        if not self.einkaufswagen:
            messagebox.showinfo("Information", "Ihr Einkaufswagen ist leer.", parent=self.root)
            return
        gesamtpreis = self.buchladen.berechne_gesamtpreis(self.einkaufswagen)
        gesamtpreis_str = "{:.2f}".format(gesamtpreis).replace('.', ',')
        message = f"Vielen Dank für Ihren Einkauf!\n\nGesamtsumme: {gesamtpreis_str} €"
        messagebox.showinfo("Kasse", message, parent=self.root)
        self.einkaufswagen.clear()
        self._aktualisiere_wagen_anzeige()

    def _zeige_buch_bild(self, buch_objekt):
        """Zeigt das Bild zum Buch an, falls vorhanden."""
        if not hasattr(self, "buch_bild_label") or self.buch_bild_label is None:
            print("[DEBUG] Kein Bild-Label vorhanden.")
            return  # Bild-Label existiert nicht

        image_path_from_json = getattr(buch_objekt, "image_path", None)
        print(f"[DEBUG] Buchbild-Pfad aus JSON: {image_path_from_json}")
        if not image_path_from_json:
            print("[DEBUG] Kein Bildpfad gesetzt.")
            self._clear_buch_bild()
            return

        # Prioritized image loading:
        # 1. Check user-specific assets folder (in AppData)
        # image_path_from_json is like "assets/image.jpg"
        user_specific_image_path = os.path.join(self.user_app_data_dir, image_path_from_json)
        
        path_to_load = None
        if os.path.exists(user_specific_image_path):
            path_to_load = user_specific_image_path
            print(f"[DEBUG] Bild gefunden in User AppData: {path_to_load}")
        else:
            # 2. Fallback to bundled/project assets
            bundled_image_path = self.get_resource_path(image_path_from_json)
            if os.path.exists(bundled_image_path):
                path_to_load = bundled_image_path
                print(f"[DEBUG] Bild gefunden in Bundled/Project Assets: {path_to_load}")

        if not path_to_load:
            print(f"[DEBUG] Bilddatei nicht gefunden. Geprüft: {user_specific_image_path} und (falls anders) {self.get_resource_path(image_path_from_json)}")
            self._clear_buch_bild()
            return

        try:
            # Pillow >=9.1.0: Image.Resampling.LANCZOS
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.Resampling.LANCZOS
            img = Image.open(path_to_load)
            img = img.resize((180, 260), resample)
            photo = ImageTk.PhotoImage(img)
            self.buch_bild_label.configure(image=photo)
            self.buch_bild_label.image = photo  # type: ignore[attr-defined]
            print("[DEBUG] Bild erfolgreich geladen und angezeigt.")
        except Exception as e:
            print(f"Fehler beim Laden des Bildes: {e}")
            self._clear_buch_bild()

    def _clear_buch_bild(self):
        if hasattr(self, "buch_bild_label") and self.buch_bild_label is not None:
            self.buch_bild_label.configure(image="")
            self.buch_bild_label.image = None  # type: ignore[attr-defined]

class AddBookWindow(ctk.CTkToplevel):
    def __init__(self, parent, buchladen_instanz: Buchladen, json_dateipfad: str, user_app_data_dir: str):
        super().__init__(parent)
        self.buchladen = buchladen_instanz
        self.json_dateipfad = json_dateipfad
        self.user_app_data_dir = user_app_data_dir # Store for saving downloaded images

        self.title("Neues Buch hinzufügen")
        self.geometry("450x350") # Angepasste Größe
        self.transient(parent) # Bleibt über dem Hauptfenster
        self.grab_set() # Modal machen (blockiert Interaktion mit Parent)

        # Variablen für Eingabefelder
        self.titel_var = tk.StringVar()
        self.autor_var = tk.StringVar()
        self.kategorie_var = tk.StringVar()
        self.preis_var = tk.StringVar()
        self.image_path_var = tk.StringVar() # Variable für Bildpfad
        self.verboten_var = tk.BooleanVar()
        self.indiziert_var = tk.BooleanVar()

        self._erstelle_widgets()

    def _sanitize_filename(self, name: str) -> str:
        """Sanitizes a string to be a valid filename."""
        return "".join(c for c in name if c.isalnum() or c in "._- ").rstrip()

    def _download_cover_image(self, title: str, author: str, target_save_path: str):
        """Attempts to download a cover image and save it to target_save_path."""
        if os.path.exists(target_save_path):
            print(f"[*] Bild existiert bereits unter {target_save_path}. Überspringe Download.")
            return True # Indicate success as file exists

        query = urllib.parse.quote_plus(f"{title} {author}")
        api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        headers = {"User-Agent": "Mozilla/5.0 (BuchladenApp/1.0)"}

        print(f"[*] Suche Cover für '{title}' via Google Books API...")
        try:
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if "items" in data and len(data["items"]) > 0:
                volume_info = data["items"][0].get("volumeInfo", {})
                image_links = volume_info.get("imageLinks", {})
                img_url = (image_links.get("large") or
                           image_links.get("medium") or
                           image_links.get("thumbnail") or
                           image_links.get("smallThumbnail"))

                if not img_url or not isinstance(img_url, str):
                    print(f"[-] Kein passender Bildlink für '{title}' in API-Antwort gefunden.")
                    return False
                
                if img_url.startswith("//"): # Handle protocol-relative URLs
                    img_url = "https:" + img_url

                print(f"[*] Lade Cover für '{title}' von {img_url}...")
                img_response = requests.get(img_url, headers=headers, timeout=15)
                img_response.raise_for_status()

                os.makedirs(os.path.dirname(target_save_path), exist_ok=True)
                with open(target_save_path, 'wb') as f:
                    f.write(img_response.content)
                print(f"[+] Cover gespeichert: {target_save_path}")
                time.sleep(0.5) # Small delay
                return True
            else:
                print(f"[-] Keine Treffer für '{title}' in Google Books API gefunden.")
                return False
        except requests.exceptions.RequestException as e:
            print(f"[!] Fehler bei der Cover-Suche/Download für '{title}': {e}")
        except (json.JSONDecodeError, IOError) as e:
            print(f"[!] Fehler bei der Verarbeitung der API-Antwort oder beim Speichern für '{title}': {e}")
        return False

    def _erstelle_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(main_frame, text="Titel:").grid(row=0, column=0, sticky="w", pady=5)
        self.titel_entry = ctk.CTkEntry(main_frame, textvariable=self.titel_var, width=250)
        self.titel_entry.grid(row=0, column=1, sticky="ew", pady=5)

        ctk.CTkLabel(main_frame, text="Autor:").grid(row=1, column=0, sticky="w", pady=5)
        ctk.CTkEntry(main_frame, textvariable=self.autor_var, width=250).grid(row=1, column=1, sticky="ew", pady=5)

        ctk.CTkLabel(main_frame, text="Kategorie:").grid(row=2, column=0, sticky="w", pady=5)
        kategorien = self.buchladen.get_alle_kategorien()
        self.kategorie_combobox = ctk.CTkComboBox(main_frame, variable=self.kategorie_var, values=kategorien + ["Neue Kategorie..."], width=250, state="readonly")
        self.kategorie_combobox.grid(row=2, column=1, sticky="ew", pady=5)
        self.kategorie_combobox.bind("<<ComboboxSelected>>", self._on_kategorie_selected)

        ctk.CTkLabel(main_frame, text="Bildpfad:").grid(row=3, column=0, sticky="w", pady=5)
        ctk.CTkEntry(main_frame, textvariable=self.image_path_var, width=250).grid(row=3, column=1, sticky="ew", pady=5)

        ctk.CTkLabel(main_frame, text="Preis (€):").grid(row=4, column=0, sticky="w", pady=5)
        ctk.CTkEntry(main_frame, textvariable=self.preis_var, width=100).grid(row=4, column=1, sticky="w", pady=5)

        check_frame = ctk.CTkFrame(main_frame)
        check_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky="w")
        ctk.CTkCheckBox(check_frame, text="Verboten", variable=self.verboten_var).pack(side="left", padx=5)
        ctk.CTkCheckBox(check_frame, text="Indiziert (FSK18)", variable=self.indiziert_var).pack(side="left", padx=5)

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=20)
        ctk.CTkButton(button_frame, text="Speichern", command=self._speichern).pack(side="left", padx=10)
        ctk.CTkButton(button_frame, text="Abbrechen", command=self.destroy).pack(side="left", padx=10)

        main_frame.columnconfigure(1, weight=1) # Damit Eingabefelder skalieren

    def _speichern(self):
        titel = self.titel_var.get().strip()
        autor = self.autor_var.get().strip()
        kategorie = self.kategorie_var.get().strip()
        preis_str = self.preis_var.get().strip().replace(',', '.') # Komma zu Punkt für float
        image_path_input = self.image_path_var.get().strip() # Rohe Eingabe des Bildpfads lesen
        verboten = self.verboten_var.get()
        indiziert = self.indiziert_var.get()

        # Validierung
        if not titel:
            messagebox.showerror("Fehler", "Titel darf nicht leer sein.", parent=self)
            return
        if not autor:
            messagebox.showerror("Fehler", "Autor darf nicht leer sein.", parent=self)
            return
        if not kategorie:
            messagebox.showerror("Fehler", "Kategorie darf nicht leer sein.", parent=self)
            return
        
        try:
            preis = float(preis_str)
            if preis < 0:
                raise ValueError("Preis darf nicht negativ sein.")
        except ValueError:
            messagebox.showerror("Fehler", "Ungültiger Preis. Bitte eine Zahl eingeben (z.B. 19.99).", parent=self)
            return

        # Bildpfad verarbeiten, um "assets/" automatisch hinzuzufügen, falls nicht vorhanden
        final_image_path = None
        if image_path_input: # User provided an explicit path
            # Entferne führendes "assets/" oder "assets\" (Groß-/Kleinschreibung ignorieren)
            # und normalisiere interne Pfadtrenner für die Dateinamensverarbeitung.
            filename_part = image_path_input
            if filename_part.lower().startswith("assets/"):
                filename_part = filename_part[len("assets/"):]
            elif filename_part.lower().startswith("assets\\"):
                filename_part = filename_part[len("assets\\"):]
            
            # Stelle sicher, dass der Dateiname eine Erweiterung hat, standardmäßig .jpg
            if filename_part and not os.path.splitext(filename_part)[1]: # Prüft, ob eine Erweiterung fehlt
                filename_part += ".jpg"
            
            if filename_part: # Ensure filename_part is not empty after stripping/processing
                # Baue den Pfad mit "assets" und dem (ggf. korrigierten) Dateinamen zusammen
                constructed_path = os.path.join("assets", filename_part)
                # Für die Speicherung im JSON wollen wir immer Forward-Slashes
                final_image_path = constructed_path.replace("\\", "/")
        else: # image_path_input is empty, try to generate from title
            if titel: # Ensure title is not empty
                sanitized_title = self._sanitize_filename(titel)
                if sanitized_title: # Ensure sanitized_title is not empty after sanitization
                    filename_part = sanitized_title + ".jpg" # Default to .jpg
                    constructed_path = os.path.join("assets", filename_part)
                    final_image_path = constructed_path.replace("\\", "/")

        # Neues Buch-Objekt erstellen
        neues_buch = Buch(titel, autor, kategorie, preis, verboten, indiziert, final_image_path)

        # Zum Inventar hinzufügen und speichern
        self.buchladen.buch_hinzufuegen(neues_buch)
        self.buchladen.speichere_inventar_in_json(self.json_dateipfad)
        messagebox.showinfo("Erfolg", f"Buch '{titel}' erfolgreich hinzugefügt und gespeichert.", parent=self)

        # Versuche, das Cover herunterzuladen, wenn ein Bildpfad generiert wurde
        if final_image_path:
            # final_image_path ist z.B. "assets/My Book.jpg"
            # Wir wollen es in self.user_app_data_dir/assets/My Book.jpg speichern
            target_image_save_path = os.path.join(self.user_app_data_dir, final_image_path)
            
            download_success = self._download_cover_image(titel, autor, target_image_save_path)
            if download_success:
                messagebox.showinfo("Bild-Download", f"Cover für '{titel}' erfolgreich heruntergeladen.", parent=self)
            else:
                messagebox.showwarning("Bild-Download", f"Cover für '{titel}' konnte nicht automatisch heruntergeladen werden. Bitte manuell im Ordner '{os.path.dirname(target_image_save_path)}' als '{os.path.basename(target_image_save_path)}' ablegen.", parent=self)

        # Optional: Eingabefelder leeren für nächste Eingabe
        self.titel_var.set("")
        self.autor_var.set("")
        self.kategorie_var.set("")
        self.image_path_var.set("") # Bildpfad-Feld leeren
        self.preis_var.set("")
        self.verboten_var.set(False)
        self.indiziert_var.set(False)
        self.titel_entry.focus_set() # Fokus zurück auf Titelfeld (benötigt self.titel_entry)
        # Um den Fokus zu setzen, müssen wir das Entry-Widget speichern:
        # In _erstelle_widgets:
        # self.titel_entry = ctk.CTkEntry(main_frame, textvariable=self.titel_var, width=250)
        # self.titel_entry.grid(...)

        # Wenn das Fenster nach dem Speichern geschlossen werden soll:
        # self.destroy()

    def _on_kategorie_selected(self, event=None):
        if self.kategorie_var.get() == "Neue Kategorie...":
            neue_kategorie = simpledialog.askstring("Neue Kategorie", "Bitte geben Sie die neue Kategorie ein:", parent=self)
            if neue_kategorie:
                neue_kategorie = neue_kategorie.strip()
                if not neue_kategorie: # Leere Eingabe nach strip
                    self.kategorie_var.set("") # Oder erste Kategorie, falls vorhanden
                    return
                self.kategorie_var.set(neue_kategorie)
                aktuelle_werte = list(self.kategorie_combobox['values'])
                if neue_kategorie not in aktuelle_werte: # Duplikate vermeiden
                    idx_neue_kat_option = aktuelle_werte.index("Neue Kategorie...")
                    aktuelle_werte.insert(idx_neue_kat_option, neue_kategorie)
                    self.kategorie_combobox['values'] = aktuelle_werte
            else:
                self.kategorie_var.set("") # Benutzer hat Abbrechen geklickt