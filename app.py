import streamlit as st
import pandas as pd
import numpy as np
import gpxpy
import folium
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from matplotlib.figure import Figure
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from io import BytesIO
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from matplotlib.patches import Circle

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

# Funktion zum Generieren einer Karte aus GPS-Daten
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
    
    # Figure erstellen
    fig = Figure(figsize=(8, 8), dpi=300, facecolor=background_color)
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
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Fügen Sie einen kleinen Puffer um die Route hinzu
    lon_buffer = (df['lon'].max() - df['lon'].min()) * 0.1
    lat_buffer = (df['lat'].max() - df['lat'].min()) * 0.1
    
    ax.set_xlim(df['lon'].min() - lon_buffer, df['lon'].max() + lon_buffer)
    ax.set_ylim(df['lat'].min() - lat_buffer, df['lat'].max() + lat_buffer)
    
    fig.tight_layout()
    
    return fig

# Funktion zum Erstellen des finalen Posters
def create_poster(map_fig, marathon_name, event_date, athlete_name, bib_number, distance, time, pace):
    # Poster erstellen mit weißem Hintergrund
    fig = Figure(figsize=(8.5, 12), dpi=300, facecolor='white')
    
    # Layout festlegen
    grid = fig.add_gridspec(5, 1, height_ratios=[0.8, 3.5, 0.2, 0.3, 0.2])
    
    # Header: Marathon-Name und Datum
    ax_header = fig.add_subplot(grid[0])
    ax_header.axis('off')
    ax_header.text(0.5, 0.7, marathon_name, fontsize=24, fontweight='bold', ha='center', va='center')
    
    # Formatieren des Datums
    try:
        if isinstance(event_date, str):
            # Verschiedene Datumsformate probieren
            date_formats = ['%d.%m.%Y', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']
            parsed_date = None
            
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(event_date, fmt)
                    break
                except ValueError:
                    continue
            
            if parsed_date:
                formatted_date = parsed_date.strftime('%d %B %Y').upper()
            else:
                formatted_date = event_date
        else:
            formatted_date = event_date.strftime('%d %B %Y').upper()
    except:
        formatted_date = event_date
    
    ax_header.text(0.5, 0.3, formatted_date, fontsize=14, ha='center', va='center')
    
    # Karte in der Mitte
    ax_map = fig.add_subplot(grid[1])
    ax_map.axis('off')
    
    # Konvertieren der Matplotlib-Figur in ein Image
    map_buf = BytesIO()
    map_fig.savefig(map_buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0)
    map_buf.seek(0)
    map_img = Image.open(map_buf)
    
    # Bild auf ax_map anzeigen
    ax_map.imshow(map_img)
    
    # Logo hinzufügen (hier ein einfaches Beispiel-Marathon-Logo)
    ax_logo = fig.add_subplot(grid[2])
    ax_logo.axis('off')
    
    # Erstellen eines einfachen Marathon-Logos
    logo_fig = Figure(figsize=(2, 2), dpi=100)
    logo_ax = logo_fig.add_subplot(111)
    logo_ax.axis('off')
    
    # Zeichne einen Kreis als Logo-Hintergrund
    circle = plt.Circle((0.5, 0.5), 0.4, color='navy')
    logo_ax.add_patch(circle)
    
    # Füge Text zum Logo hinzu
    logo_text = logo_ax.text(0.5, 0.5, f"{marathon_name.split()[0][0]}CM", color='white', 
                            fontsize=20, fontweight='bold', ha='center', va='center')
    logo_text.set_path_effects([path_effects.withStroke(linewidth=2, foreground='navy')])
    
    # Füge einen Lorbeerkranz hinzu
    theta = np.linspace(0, 2*np.pi, 100)
    r = 0.45
    x = r * np.cos(theta) + 0.5
    y = r * np.sin(theta) + 0.5
    logo_ax.plot(x, y, 'navy', alpha=0)  # Unsichtbarer Kreis als Platzhalter
    
    # Zeichne ein paar Lorbeerzweige
    leaf_color = 'navy'
    for i in range(8):
        angle = i * np.pi/4
        x_leaf = 0.5 + 0.47 * np.cos(angle)
        y_leaf = 0.5 + 0.47 * np.sin(angle)
        dx = 0.1 * np.cos(angle + np.pi/2)
        dy = 0.1 * np.sin(angle + np.pi/2)
        logo_ax.plot([x_leaf, x_leaf+dx], [y_leaf, y_leaf+dy], color=leaf_color, linewidth=2)
        logo_ax.plot([x_leaf, x_leaf-dx], [y_leaf, y_leaf-dy], color=leaf_color, linewidth=2)
    
    # Konvertieren des Logo in ein Image
    logo_buf = BytesIO()
    logo_fig.savefig(logo_buf, format='png', dpi=100, transparent=True)
    logo_buf.seek(0)
    logo_img = Image.open(logo_buf)
    
    # Logo im Poster anzeigen
    logo_extent = [0.2, 0.4, 0.2, 0.8]  # [links, rechts, unten, oben]
    ax_logo.imshow(logo_img, extent=logo_extent)
    
    # Füge den Text "42ND" neben dem Logo hinzu
    ax_logo.text(0.45, 0.5, "42ND", fontsize=14, fontweight='bold', ha='left', va='center')
    
    # Details: Athlet, Distanz, Zeit, Pace
    ax_details = fig.add_subplot(grid[3])
    ax_details.axis('off')
    
    # Zeile für Athletennamen und Startnummer
    ax_details.text(0.25, 0.7, f"{athlete_name}", fontsize=18, fontweight='bold', ha='center', va='center')
    ax_details.text(0.75, 0.7, f"#{bib_number}", fontsize=16, ha='center', va='center')
    
    # Zeile für Distanz, Zeit und Pace
    ax_details.text(0.25, 0.3, f"{distance}\nKM", fontsize=14, ha='center', va='center')
    ax_details.text(0.5, 0.3, f"{time}\nTIME", fontsize=14, ha='center', va='center')
    ax_details.text(0.75, 0.3, f"{pace}\n/KM", fontsize=14, ha='center', va='center')
    
    # Footer: Platz für QR-Code oder zusätzliche Informationen
    ax_footer = fig.add_subplot(grid[4])
    ax_footer.axis('off')
    
    fig.tight_layout()
    
    # Konvertieren der Figur in ein Bild
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    return buf

# Streamlit UI
st.title("Marathon Poster Generator")

st.markdown("""
Diese Anwendung erstellt personalisierte Marathon-Poster basierend auf deiner GPX-Datei und eingegebenen Details.
""")

# Eingabefelder in Spalten anordnen
col1, col2 = st.columns(2)

with col1:
    marathon_name = st.text_input("Marathon Name", "VIENNA CITY MARATHON")
    event_date = st.text_input("Datum (TT.MM.JJJJ)", "06.04.2025")
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

if gpx_file is not None:
    df = load_gpx_file(gpx_file)
    
    if df is not None and not df.empty:
        st.success("GPX-Datei erfolgreich geladen!")
        
        # Daten bereinigen
        df_clean = clean_gps_data(df, smoothing_factor)
        
        # Karte generieren
        map_fig = generate_map(df_clean, map_color, route_color, start_color, end_color)
        
        # Poster erstellen
        poster_buffer = create_poster(map_fig, marathon_name, event_date, athlete_name, 
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

if st.button("Beispiel-GPX laden"):
    # Einfache Beispiel-GPX-Daten erstellen (ein Kreis um das Zentrum von Wien)
    center_lat, center_lon = 48.2082, 16.3719  # Wien Zentrum
    radius = 0.02  # ungefähr 2km
    num_points = 200
    
    angle = np.linspace(0, 2*np.pi, num_points)
    lats = center_lat + radius * np.cos(angle) * 0.7  # Ellipse statt Kreis
    lons = center_lon + radius * np.sin(angle)
    
    # Füge etwas Variation hinzu, um es realistischer zu machen
    np.random.seed(42)  # Für reproduzierbare Ergebnisse
    lats += np.random.normal(0, 0.0005, num_points)
    lons += np.random.normal(0, 0.0005, num_points)
    
    # Erstelle DataFrame
    example_df = pd.DataFrame({
        'lat': lats,
        'lon': lons,
        'elevation': np.zeros(num_points),
        'time': [datetime.now()] * num_points
    })
    
    # Bereinigen
    example_df_clean = clean_gps_data(example_df, smoothing_factor)
    
    # Karte generieren
    example_map_fig = generate_map(example_df_clean, map_color, route_color, start_color, end_color)
    
    # Poster erstellen
    example_poster_buffer = create_poster(example_map_fig, marathon_name, event_date, athlete_name, 
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

Diese Anwendung kann auf GitHub gehostet und über Streamlit Cloud bereitgestellt werden:

1. Erstelle ein GitHub-Repository
2. Füge diese `app.py` Datei hinzu
3. Erstelle eine `requirements.txt` Datei
4. Stelle die App auf Streamlit Cloud bereit

Für detaillierte Anweisungen, siehe die Erklärung unten.
""")
