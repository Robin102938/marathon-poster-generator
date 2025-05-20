# Marathon Poster Generator

Eine Streamlit-Anwendung zur Erstellung von personalisierten Marathon-Postern aus GPX-Dateien.

![Beispiel Marathon Poster](https://raw.githubusercontent.com/username/marathon-poster-generator/main/example_poster.png)

## Funktionen

- **GPX-Datei Upload**: Lade deine Marathon-Route als GPX-Datei hoch
- **Anpassbare Details**: Marathon-Name, Datum, Name des Athleten, Startnummer, Distanz, Zeit und Pace
- **Kartenanpassung**: Verschiedene Kartenstile und anpassbare Farben für Strecke, Start- und Zielpunkt
- **Streckenbereinigung**: Automatische Glättung und Bereinigung von GPS-Daten für ein sauberes Ergebnis
- **Hochwertige Ausgabe**: 300 DPI Auflösung, geeignet für den Druck
- **Einfache Benutzeroberfläche**: Benutzerfreundliches Design mit Echtzeit-Vorschau

## Installation

### Lokale Installation

1. Repository klonen:
   ```bash
   git clone https://github.com/username/marathon-poster-generator.git
   cd marathon-poster-generator
   ```

2. Virtuelle Umgebung erstellen und aktivieren:
   ```bash
   python -m venv venv
   # Unter Windows:
   venv\Scripts\activate
   # Unter Linux/Mac:
   source venv/bin/activate
   ```

3. Abhängigkeiten installieren:
   ```bash
   pip install -r requirements.txt
   ```

4. Anwendung starten:
   ```bash
   streamlit run app.py
   ```

### Streamlit Cloud Deployment

Die Anwendung kann auch direkt auf Streamlit Cloud gehostet werden:

1. Forke das Repository auf GitHub
2. Melde dich bei [Streamlit Cloud](https://streamlit.io/cloud) an
3. Wähle "New app" und verbinde es mit deinem GitHub-Repository
4. Wähle die Datei "app.py" und klicke auf "Deploy"

## Verwendung

1. Lade eine GPX-Datei deiner Marathon-Strecke hoch
2. Fülle die Marathon-Details in der Seitenleiste aus
3. Passe die Karten- und Streckenfarben nach Wunsch an
4. Stelle den Glättungsfaktor ein, um die GPX-Daten zu bereinigen
5. Klicke auf "Generate Poster" um dein Poster zu erstellen
6. Lade das fertige Poster als hochauflösende PNG-Datei herunter

## GPX-Dateien erstellen oder finden

- Aufzeichnung mit GPS-Geräten oder Fitness-Apps (Garmin, Strava, etc.)
- Export aus Strava oder anderen Fitness-Plattformen
- Erstellung mit Online-Tools wie [GPX Editor](https://gpx.studio/)
- Download von Marathon-Strecken von offiziellen Veranstalterwebsites

## Anforderungen

- Python 3.8+
- Streamlit
- Pandas
- NumPy
- gpxpy
- Folium
- Pillow
- Matplotlib
- GeoPandas
- Contextily
- Shapely
- SciPy
- MapClassify
- Requests

## Beitragen

Beiträge sind willkommen! Bitte fühle dich frei, Issues zu eröffnen oder Pull Requests zu erstellen.

1. Forke das Repository
2. Erstelle einen Feature-Branch (`git checkout -b feature/amazing-feature`)
3. Committe deine Änderungen (`git commit -m 'Add some amazing feature'`)
4. Pushe zu deinem Branch (`git push origin feature/amazing-feature`)
5. Öffne einen Pull Request

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE) Datei für Details.

## Kontakt

Dein Name - [@dein_twitter](https://twitter.com/dein_twitter) - email@example.com

Projekt-Link: [https://github.com/username/marathon-poster-generator](https://github.com/username/marathon-poster-generator)
