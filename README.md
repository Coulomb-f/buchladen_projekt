# Buchladen - Ein POC, dass tkinter gar nicht so hässlich sein muss.

Willkommen beim Buchladen-Projekt! Diese Desktop-Anwendung dient als Proof-of-Concept (POC) und demonstriert, wie man mit Python, Tkinter und der CustomTkinter-Bibliothek ansprechende und moderne grafische Benutzeroberflächen erstellen kann. Die Anwendung simuliert einen einfachen Online-Buchladen mit Inventarverwaltung und Einkaufswagenfunktion.

## Features

*   **Buchinventar anzeigen**: Durchsuchen Sie eine Liste verfügbarer Bücher.
*   **Filterfunktionen**:
    *   Filtern Sie Bücher nach Kategorie.
    *   Zeigen Sie nur Bücher mit FSK18-Kennzeichnung an.
    *   Zeigen Sie nur verbotene (nicht verkäufliche) Bücher an.
*   **Einkaufswagen**: Legen Sie Bücher in den Einkaufswagen und sehen Sie den Gesamtpreis.
*   **Kasse**: Simulieren Sie den Kaufvorgang.
*   **Buchcover-Anzeige**: Sehen Sie das Cover des ausgewählten Buches.
*   **Buch hinzufügen**:
    *   Fügen Sie neue Bücher zum Inventar hinzu.
    *   Automatische Suche und Download von Buchcovern über die Google Books API.
*   **Persistente Datenspeicherung**:
    *   Das Buchinventar wird in einer `buecher.json`-Datei gespeichert.
    *   Benutzerspezifische Daten (hinzugefügte Bücher, heruntergeladene Cover) werden im Anwendungsdatenverzeichnis des Benutzers gespeichert (z.B. `%APPDATA%\DasLeseparadies` unter Windows).
*   **Moderne GUI**: Dank CustomTkinter eine optisch ansprechendere Oberfläche als mit Standard-Tkinter.

## Technologien

*   **Python 3**: Programmiersprache
*   **Tkinter**: Standard-GUI-Bibliothek von Python (verwendet für Hauptfensterstruktur und Standarddialoge).
*   **CustomTkinter**: Erweiterung für Tkinter, um moderne und anpassbare Widgets zu erstellen.
*   **Pillow (PIL Fork)**: Bibliothek zur Bildverarbeitung (Anzeigen von Buchcovern).
*   **Requests**: Bibliothek für HTTP-Anfragen (Download von Buchcovern).

## Ausführen der Anwendung

### Über Releases (Empfohlen für Benutzer)

Fertig kompilierte Versionen der Anwendung (als `.exe`-Datei für Windows) finden Sie im Releases-Bereich dieses GitHub-Repositories. Laden Sie einfach die neueste Version herunter und führen Sie die Datei aus.

**Wichtiger Hinweis zur Datenspeicherung:**
Die Anwendung erstellt ein Verzeichnis im Anwendungsdatenordner Ihres Betriebssystems, um benutzerspezifische Daten zu speichern. Unter Windows ist dies typischerweise:
`C:\Users\<IhrBenutzername>\AppData\Roaming\DasLeseparadies`

Dort werden die `buecher.json` (Ihre persönliche Kopie des Inventars) und ein `assets`-Ordner für heruntergeladene Buchcover abgelegt. Beim ersten Start wird eine Standard-`buecher.json` aus dem Programmpaket in diesen Ordner kopiert, falls noch keine vorhanden ist.

### Aus dem Quellcode (Für Entwickler)

1.  **Voraussetzungen**:
    *   Python 3.8 oder neuer.
    *   Git (optional, um das Repository zu klonen).

2.  **Repository klonen (optional):**
    ```bash
    git clone https://github.com/Coulomb-f/buchladen_projekt.git
    cd buchladen_projekt
    ```

3.  **Abhängigkeiten installieren**:
    Navigieren Sie in das Projektverzeichnis und installieren Sie die benötigten Pakete:
    ```bash
    pip install customtkinter Pillow requests
    ```

4.  **Anwendung starten**:
    ```bash
    python main.py
    ```

## Datenstruktur

Das Kerninventar der Bücher wird in einer JSON-Datei (`buecher.json`) verwaltet. Jedes Buchobjekt enthält Informationen wie Titel, Autor, Kategorie, Preis, Status (verboten/indiziert) und optional einen Pfad zum Buchcover.

*   Eine **Standardversion** der `buecher.json` und zugehörige Bilder im `assets`-Ordner sind im Quellcode und in der kompilierten Anwendung enthalten.
*   Beim **ersten Start** der Anwendung wird diese Standard-`buecher.json` in das benutzerspezifische Anwendungsdatenverzeichnis kopiert (siehe "Ausführen der Anwendung"). Alle weiteren Änderungen, wie das Hinzufügen neuer Bücher oder das Herunterladen neuer Cover, erfolgen in diesem benutzerspezifischen Verzeichnis.

## Kompilieren (mit PyInstaller)

Um die Anwendung für Windows zu kompilieren, verwenden Sie PyInstaller.

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.

---
Viel Spaß beim Ausprobieren und Weiterentwickeln!

## Zukünftige Erweiterungen (To-Do)

*   **Platzhalter-Cover**: Implementierung eines Standard-Platzhalterbildes für Bücher, für die über die API kein Cover gefunden werden konnte.
*   **Manuelle Cover-Auswahl**: Verbesserung der "Buch hinzufügen"-Funktion, um Benutzern die Auswahl lokaler Bilddateien als Buchcover zu ermöglichen.
*   **Kategorie-Management**: Überprüfung und Fertigstellung der Funktionalität zum Hinzufügen neuer Kategorien im "Buch hinzufügen"-Dialog.
*   **Weitere GUI-Verbesserungen**: Optimierung des Layouts und der Benutzerinteraktion.
*   **Tests erweitern**: Ausbau der Unit-Tests für Backend-Logik und GUI-Interaktionen.