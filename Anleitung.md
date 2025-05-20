# Marathon Poster Generator - Anleitung

Diese Anleitung führt dich durch die Nutzung des Marathon Poster Generators Schritt für Schritt.

## Inhaltsverzeichnis
1. [Installation und Start](#installation-und-start)
2. [GPX-Datei vorbereiten](#gpx-datei-vorbereiten)
3. [Die Benutzeroberfläche](#die-benutzeroberfläche)
4. [Poster erstellen](#poster-erstellen)
5. [Problembehandlung](#problembehandlung)
6. [Tipps für optimale Ergebnisse](#tipps-für-optimale-ergebnisse)

## Installation und Start

### Methode 1: Lokale Installation

#### Unter Windows:
1. Stelle sicher, dass Python (Version 3.8 oder höher) installiert ist
2. Lade das Repository herunter und entpacke es
3. Doppelklick auf `setup.bat`
4. Nach Abschluss der Installation starte die App mit:
   ```
   streamlit run app.py
   ```

#### Unter Linux/Mac:
1. Stelle sicher, dass Python (Version 3.8 oder höher) installiert ist
2. Lade das Repository herunter und entpacke es
3. Öffne ein Terminal im Projektordner
4. Führe aus:
   ```
   chmod +x setup.sh
   ./setup.sh
   streamlit run app.py
   ```

### Methode 2: Docker
Wenn Docker installiert ist:
1. Im Projektordner ausführen:
   ```
   docker-compose up -d
   ```
2. Öffne im Browser: `http://localhost:8501`

### Methode 3: Streamlit Cloud
Die Anwendung ist auch online verfügbar unter:
[https://marathon-poster-generator.streamlit.app](https://marathon-poster-generator.streamlit.app)

## GPX-Datei vorbereiten

Du benötigst eine GPX-Datei deiner Marathon-Route. Diese kannst du auf verschiedene Weise erhalten:

### Eigene Aufzeichnung
- Mit GPS-Uhren (Garmin, Polar, Suunto, etc.)
- Mit Fitness-Apps auf dem Smartphone (Strava, Nike Run Club, etc.)

### Export aus Fitness-Plattformen
- **Strava**: Aktivität öffnen → "..." Button → "Export GPX"
- **Garmin Connect**: Aktivität öffnen → Zahnrad-Symbol → "Exportieren" → "GPX"

### Online erstellen
Wenn du keine eigene Route hast, kannst du eine mit diesen Tools erstellen:
- [GPX Studio](https://gpx.studio/)
- [OnTheGoMap](https://onthegomap.com/)
- [Strava Route Builder](https://www.strava.com/routes) (Strava-Konto erforderlich)

### Offizielle Marathon-Strecken
Viele Marathon-Veranstalter bieten GPX-Dateien ihrer offiziellen Strecken zum Download an.

## Die Benutzeroberfläche

Die Anwendung besteht aus zwei Hauptbereichen:

### Seitenleiste (links)
Hier gibst du alle Daten ein und passt das Poster an:
- GPX-Datei Upload
- Marathon-Details (Name, Datum)
- Athleten-Details (Name, Startnummer)
- Leistungsdaten (Distanz, Zeit, Pace)
- Kartenanpassung (Kartenstil, Routenfarbe, Start-/Zielfarbe)
- GPX-Bereinigung (Glättungsfaktor)
- Ausgabeoptionen (Dateiname)

### Hauptbereich (rechts)
Hier siehst du die Poster-Vorschau und Anleitungen.

## Poster erstellen

Folge diesen Schritten, um dein eigenes Marathon-Poster zu erstellen:

1. **GPX-Datei hochladen**
   - Klicke auf "Browse files" im Bereich "Upload GPX File"
   - Wähle deine GPX-Datei aus

2. **Marathon-Details eingeben**
   - Gib den Namen des Marathons ein (z.B. "VIENNA CITY MARATHON")
   - Wähle das Datum des Marathons aus

3. **Athleten-Details eingeben**
   - Gib deinen Namen ein
   - Gib deine Startnummer ein

4. **Leistungsdaten eingeben**
   - Gib die gelaufene Distanz in Kilometern ein
   - Gib deine Zeit im Format HH:MM:SS ein
   - Die Pace (min/km) wird automatisch berechnet, kann aber überschrieben werden

5. **Karte anpassen**
   - Wähle einen Kartenstil (Dark Blue, Light, Terrain, etc.)
   - Wähle Farben für die Route, Start- und Zielpunkt

6. **GPX-Bereinigung anpassen**
   - Stelle den Glättungsfaktor ein (höhere Werte = glattere Strecke)

7. **Ausgabeoptionen**
   - Gib einen Namen für die Ausgabedatei ein

8. **Poster generieren**
   - Klicke auf "Generate Poster"
   - Nach der Generierung erscheint ein Download-Button

9. **Poster herunterladen**
   - Klicke auf den Download-Button, um das hochauflösende Poster zu speichern

## Problembehandlung

### GPX-Datei kann nicht geladen werden
- Stelle sicher, dass die Datei im GPX-Format ist (Endung .gpx)
- Prüfe, ob die Datei korrekt formatiert ist
- Versuche eine andere GPX-Datei

### Karte wird nicht richtig angezeigt
- Prüfe, ob die GPX-Datei Koordinaten enthält
- Probiere einen höheren Glättungsfaktor
- Wähle einen anderen Kartenstil

### Anwendung startet nicht
- Prüfe, ob alle Abhängigkeiten installiert sind (erneut setup.bat/setup.sh ausführen)
- Prüfe deine Python-Version (3.8 oder höher erforderlich)
- Bei Docker: Prüfe, ob der Container läuft (`docker ps`)

## Tipps für optimale Ergebnisse

### Optimale GPX-Dateien
- Verwende möglichst saubere GPX-Aufzeichnungen ohne zu viele GPS-Sprünge
- Zeichne deine Route mit einer höheren Aufzeichnungsfrequenz auf (z.B. alle 1-2 Sekunden)
- Für bessere Ergebnisse: Bereinige die GPX-Datei vorab mit Tools wie [GPX Editor](https://gpx.studio)

### Gestaltungstipps
- Wähle kontrastierende Farben für bessere Sichtbarkeit
- Für Indoor-Poster eignen sich dunklere Karten besser
- Für den Druck empfehlen sich hellere Karten mit dunkler Route

### Drucktipps
- Das Poster hat A4-Proportionen und ist für den Druck in DIN A4 optimiert
- Die Ausgabe erfolgt in 300 DPI, geeignet für hochwertigen Druck
- Drucke auf hochwertigem Fotopapier für beste Ergebnisse
- Lokale Copy-Shops und Online-Druckdienste können das Poster in verschiedenen Größen drucken
