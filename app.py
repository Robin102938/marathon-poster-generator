import streamlit as st
import pandas as pd
import numpy as np
import gpxpy
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PIL import Image, ImageDraw, ImageFont
import io
from io import BytesIO
from datetime import datetime
import base64

st.set_page_config(page_title="Marathon Poster Generator", layout="wide")

# Funktion zum Laden und Parsen der GPX-Datei
def load_gpx_file(gpx_file):
    try:
        gpx_text = gpx_file.read().decode('utf-8')
        gpx = gpxpy.parse(gpx_text)
        
        points = []
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append({
                        'lat': point.latitude,
                        'lon': point.longitude,
                        'elevation': point.elevation,
                        'time': point.time
                    })
        
        df = pd.DataFrame(points)
        return df
    except Exception as e:
        st.error(f"Fehler beim Laden der GPX-Datei: {e}")
        return None

# Funktion zum Bereinigen der GPS-Daten
def clean_gps_data(df, smoothing_factor=5):
    if len(df) <= smoothing_factor:
        return df
    
    # Entfernen von Ausreißern mit einfachem gleitenden Durchschnitt
    df['lat_smooth'] = df['lat'].rolling(window=smoothing_factor, center=True).mean()
    df['lon_smooth'] = df['lon'].rolling(window=smoothing_factor, center=True).mean()
    
    # Auffüllen von NaN-Werten am Anfang und Ende
    df['lat_smooth'] = df['lat_smooth'].fillna(df['lat'])
    df['lon_smooth'] = df['lon_smooth'].fillna(df['lon'])
    
    return df

# Funktion zum Generieren einer simplen Route-Karte im Stil des Originalposters
def generate_map(df, map_color, route_color, start_color, end_color):
    # Definieren der Farbpalette
    color_palettes = {
        'Dunkelblau': '#1A2744',
        'Schwarz': '#000000',
        'Dunkelgrün': '#143D29',
        'Dunkelrot': '#4D1F1F',
        'Dunkelgrau': '#2E2E2E'
    }
    
    # Route-Farbpalette
    route_colors = {
        'Gold': '#FFD700',
        'Weiß': '#FFFFFF',
        'Rot': '#FF0000',
        'Blau': '#1E90FF',
        'Grün': '#32CD32'
    }
    
    # Marker-Farbpalette
    marker_colors = {
        'Gold': '#FFD700',
        'Weiß': '#FFFFFF',
        'Rot': '#FF0000',
        'Blau': '#1E90FF',
        'Grün': '#32CD32'
    }
    
    background_color = color_palettes.get(map_color, '#1A2744')
    line_color = route_colors.get(route_color, '#FFD700')
    start_marker_color = marker_colors.get(start_color, '#FFD700')
    end_marker_color = marker_colors.get(end_color, '#FFD700')
    
    # Figure erstellen - flacher, breiter Stil wie im Originaldesign
    fig = Figure(figsize=(10, 3), dpi=300, facecolor=background_color)
    ax = fig.add_subplot(111)
    
    # Route plotten
    if 'lat_smooth' in df.columns and 'lon_smooth' in df.columns:
        ax.plot(df['lon_smooth'], df['lat_smooth'], color=line_color, linewidth=2.5, zorder=2)
    else:
        ax.plot(df['lon'], df['lat'], color=line_color, linewidth=2.5, zorder=2)
    
    # Start- und Endpunkte
    start_point = df.iloc[0]
    end_point = df.iloc[-1]
    
    # Start- und Endmarker hinzufügen
    ax.scatter(start_point['lon'], start_point['lat'], color=start_marker_color, s=150, marker='o', zorder=3)
    ax.scatter(end_point['lon'], end_point['lat'], color=end_marker_color, s=150, marker='x', zorder=3)
    
    # Einstellungen für die Kartenansicht
    ax.set_aspect('auto')  # Ändern zu 'auto' für ein breiteres Design
    ax.axis('off')
    
    # Fügen Sie einen kleinen Puffer um die Route hinzu
    lon_buffer = (df['lon'].max() - df['lon'].min()) * 0.05
    lat_buffer = (df['lat'].max() - df['lat'].min()) * 0.05
    
    ax.set_xlim(df['lon'].min() - lon_buffer, df['lon'].max() + lon_buffer)
    ax.set_ylim(df['lat'].min() - lat_buffer, df['lat'].max() + lat_buffer)
    
    fig.tight_layout(pad=0)
    
    return fig

# Funktion zum Erstellen einer einfachen Beispielroute
def create_example_route():
    num_points = 100
    
    # Startpunkt
    start_lon, start_lat = 16.35, 48.20
    
    # Ein paar zufällige Wegpunkte für eine realistischere Route
    points = [(start_lon, start_lat)]
    
    # Erstelle eine simple Route
    np.random.seed(42)  # Für reproduzierbare Ergebnisse
    
    # Erster Teil - nach links
    for i in range(20):
        last_lon, last_lat = points[-1]
        points.append((last_lon - 0.005 + np.random.normal(0, 0.001), 
                      last_lat + np.random.normal(0, 0.002)))
    
    # Abwärts
    for i in range(15):
        last_lon, last_lat = points[-1]
        points.append((last_lon + np.random.normal(0, 0.001), 
                      last_lat - 0.005 + np.random.normal(0, 0.001)))
    
    # Nach rechts
    for i in range(35):
        last_lon, last_lat = points[-1]
        points.append((last_lon + 0.005 + np.random.normal(0, 0.001), 
                      last_lat + np.random.normal(0, 0.001)))
    
    # Nach oben und rechts (Ende)
    for i in range(10):
        last_lon, last_lat = points[-1]
        points.append((last_lon + 0.005 + np.random.normal(0, 0.001), 
                      last_lat + 0.005 + np.random.normal(0, 0.001)))
    
    # Erstelle DataFrame
    lons, lats = zip(*points)
    df = pd.DataFrame({
        'lat': lats,
        'lon': lons,
        'elevation': np.zeros(len(points)),
        'time': [datetime.now()] * len(points)
    })
    
    return df

# Funktion zum Erstellen des finalen Posters
def create_poster(map_fig, marathon_name, event_date, athlete_name, bib_number, distance, time, pace):
    # Poster erstellen mit weißem Hintergrund im Minimalstil
    fig = Figure(figsize=(8.5, 12), dpi=300, facecolor='white')
    
    # Layout festlegen - wie im Originalposter
    grid = fig.add_gridspec(14, 1, height_ratios=[1, 0.5, 4, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 1, 0.1, 0.5])
    
    # Header: Marathon-Name
    ax_header = fig.add_subplot(grid[0])
    ax_header.axis('off')
    ax_header.text(0.5, 0.5, marathon_name, fontsize=24, fontweight='bold', ha='center', va='center')
    
    # Datum
    ax_date = fig.add_subplot(grid[1])
    ax_date.axis('off')
    ax_date.text(0.5, 0.5, event_date, fontsize=14, ha='center', va='center')
    
    # Karte in der Mitte
    ax_map = fig.add_subplot(grid[2])
    ax_map.axis('off')
    
    # Konvertieren der Matplotlib-Figur in ein Image
    map_buf = BytesIO()
    map_fig.savefig(map_buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
    map_buf.seek(0)
    map_img = Image.open(map_buf)
    
    # Bild auf ax_map anzeigen
    ax_map.imshow(map_img)
    
    # Leere Zeilen zwischen Karte und Details für Abstände
    # (werden durch height_ratios gesteuert)
    
    # Logo - sehr minimal, nur "42ND"
    ax_logo = fig.add_subplot(grid[11])
    ax_logo.axis('off')
    ax_logo.text(0.5, 0.5, "42ND", fontsize=14, fontweight='bold', color='navy', ha='center', va='center')
    
    # Details: Athlet, Distanz, Zeit, Pace
    ax_details = fig.add_subplot(grid[12:])
    ax_details.axis('off')
    
    # Zeile für Athletennamen und Startnummer mit mehr Abstand - wie im Original
    ax_details.text(0.15, 0.6, f"{athlete_name}", fontsize=18, fontweight='bold', ha='left', va='center')
    ax_details.text(0.85, 0.6, f"#{bib_number}", fontsize=16, ha='right', va='center')
    
    # Zeile für Distanz, Zeit und Pace - wie im Original
    ax_details.text(0.15, 0.2, f"{distance}\nKM", fontsize=14, ha='left', va='center')
    ax_details.text(0.5, 0.2, f"{time}\nTIME", fontsize=14, ha='center', va='center')
    ax_details.text(0.85, 0.2, f"{pace}\n/KM", fontsize=14, ha='right', va='center')
    
    fig.tight_layout()
    
    # Konvertieren der Figur in ein Bild
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    return buf

# Formatieren des Datums in ein einheitliches Format
def format_date(date_str):
    try:
        # Verschiedene Datumsformate probieren
        date_formats = ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
        parsed_date = None
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                continue
        
        if parsed_date:
            return parsed_date.strftime('%d %B %Y').upper()
        else:
            return date_str.upper()
    except:
        return date_str.upper()

# Streamlit UI
st.title("Marathon Poster Generator")

st.markdown("""
Diese Anwendung erstellt personalisierte Marathon-Poster basierend auf deiner GPX-Datei und eingegebenen Details.
""")

# Eingabefelder in Spalten anordnen
col1, col2 = st.columns(2)

with col1:
    marathon_name = st.text_input("Marathon Name", "VIENNA CITY MARATHON")
    event_date = st.text_input("Datum", "6 APRIL 2025")
    athlete_name = st.text_input("Athlet Name", "ATHLETE NAME")
    bib_number = st.text_input("Startnummer", "1234")

with col2:
    distance = st.text_input("Distanz (km)", "42.195")
    time = st.text_input("Zeit (hh:mm:ss)", "00:00:00")
    pace = st.text_input("Pace (min/km)", "00:00")
    
    # GPX-Datei Upload
    gpx_file = st.file_uploader("GPX-Datei hochladen", type=['gpx'])

# Farbauswahl
st.subheader("Farbeinstellungen")
col1, col2, col3, col4 = st.columns(4)

with col1:
    map_color = st.selectbox("Kartenfarbe", 
                             ['Dunkelblau', 'Schwarz', 'Dunkelgrün', 'Dunkelrot', 'Dunkelgrau'])

with col2:
    route_color = st.selectbox("Streckenfarbe", 
                               ['Gold', 'Weiß', 'Rot', 'Blau', 'Grün'])

with col3:
    start_color = st.selectbox("Startpunkt-Farbe", 
                              ['Gold', 'Weiß', 'Rot', 'Blau', 'Grün'])

with col4:
    end_color = st.selectbox("Zielpunkt-Farbe", 
                            ['Gold', 'Weiß', 'Rot', 'Blau', 'Grün'])

# Glättungsfaktor
smoothing_factor = st.slider("Glättungsfaktor der Strecke", 1, 20, 5, 
                            help="Höhere Werte sorgen für eine glattere Strecke")

# Formatiere das Datum
formatted_date = format_date(event_date)

if gpx_file is not None:
    df = load_gpx_file(gpx_file)
    
    if df is not None and not df.empty:
        st.success("GPX-Datei erfolgreich geladen!")
        
        # Daten bereinigen
        df_clean = clean_gps_data(df, smoothing_factor)
        
        # Karte generieren
        map_fig = generate_map(df_clean, map_color, route_color, start_color, end_color)
        
        # Poster erstellen
        poster_buffer = create_poster(map_fig, marathon_name, formatted_date, athlete_name, 
                                      bib_number, distance, time, pace)
        
        # Vorschau und Download-Button anzeigen
        st.subheader("Poster Vorschau")
        st.image(poster_buffer, use_column_width=True)
        
        # Download-Button
        st.download_button(
            label="Poster herunterladen (PNG)",
            data=poster_buffer,
            file_name=f"{marathon_name.replace(' ', '_')}_poster.png",
            mime="image/png"
        )
        
        # Hochauflösende PDF-Version für den Druck
        st.markdown("""
        **Hinweis:** Die heruntergeladene PNG-Datei ist für die Bildschirmanzeige optimiert. 
        Für einen hochwertigen Druck empfehlen wir die Verwendung der heruntergeladenen Datei 
        mit einem Bildbearbeitungsprogramm, um weitere Anpassungen vorzunehmen.
        """)
else:
    st.info("Bitte lade eine GPX-Datei hoch, um dein Marathon-Poster zu erstellen.")

# Füge eine Beispiel-GPX-Datei hinzu
st.markdown("### Keine GPX-Datei? Probiere ein Beispiel!")

if st.button("Beispiel-Route laden"):
    # Beispielroute erstellen
    example_df = create_example_route()
    
    # Bereinigen
    example_df_clean = clean_gps_data(example_df, smoothing_factor)
    
    # Karte generieren
    example_map_fig = generate_map(example_df_clean, map_color, route_color, start_color, end_color)
    
    # Poster erstellen
    example_poster_buffer = create_poster(example_map_fig, marathon_name, formatted_date, athlete_name, 
                                        bib_number, distance, time, pace)
    
    # Vorschau anzeigen
    st.subheader("Beispiel-Poster Vorschau")
    st.image(example_poster_buffer, use_column_width=True)
    
    # Download-Button
    st.download_button(
        label="Beispiel-Poster herunterladen (PNG)",
        data=example_poster_buffer,
        file_name="Beispiel_Marathon_Poster.png",
        mime="image/png"
    )

# Füge Informationen zur Github-Bereitstellung hinzu
st.markdown("""
## GitHub und Streamlit Bereitstellung

Diese Anwendung kann auf GitHub gehostet und über Streamlit Cloud bereitgestellt werden.
""")
