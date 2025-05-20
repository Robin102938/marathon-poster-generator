# Marathon Poster Generator

Diese Streamlit-Anwendung erstellt personalisierte Marathon-Poster basierend auf GPX-Daten. Die App ermöglicht es Nutzern, ihre Laufstrecke als GPX-Datei hochzuladen und individuelle Details wie Marathon-Name, Datum, Athletenname, Startnummer, Distanz, Zeit und Pace anzugeben.

## Funktionen

- Upload von GPX-Dateien zur Visualisierung der Laufstrecke
- Anpassbare Details: Marathon-Name, Datum, Athlet, Startnummer, Distanz, Zeit und Pace
- Auswahl verschiedener Farben für Karte, Strecke, Start- und Zielpunkt
- Bereinigung und Glättung der GPS-Daten für eine saubere Darstellung
- Hohe Ausgabequalität für den Druck
- Download des fertigen Posters als PNG-Datei

## Verwendung

1. Besuche die [Marathon Poster Generator App](https://marathon-poster-generator.streamlit.app/)
2. Fülle die persönlichen Details aus (Marathon-Name, Datum, Athlet, etc.)
3. Lade deine GPX-Datei hoch
4. Wähle die gewünschten Farben für dein Poster
5. Passe den Glättungsfaktor der Strecke an
6. Lade dein personalisiertes Poster herunter

## Beispiel

Wenn du keine eigene GPX-Datei hast, kannst du die Beispielfunktion nutzen, um ein Muster-Poster zu erstellen.

## Lokale Installation

Falls du die Anwendung lokal ausführen möchtest:

```bash
git clone https://github.com/dein-username/marathon-poster-generator.git
cd marathon-poster-generator
pip install -r requirements.txt
streamlit run app.py
```

## Technologien

- Python
- Streamlit
- Pandas
- NumPy
- gpxpy
- Matplotlib
- Pillow

## Bereitstellung

Diese Anwendung ist auf Streamlit Cloud bereitgestellt und über GitHub verbunden.
