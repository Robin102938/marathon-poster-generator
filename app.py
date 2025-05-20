import streamlit as st
import pandas as pd
import numpy as np
import gpxpy
import folium
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from datetime import datetime
import os
import requests
from io import BytesIO
import contextily as ctx
from shapely.geometry import LineString
import geopandas as gpd
from shapely.ops import linemerge, unary_union
import mapclassify
from scipy.ndimage import gaussian_filter1d
from scipy.spatial import distance

# Set page title and icon
st.set_page_config(
    page_title="Marathon Poster Generator",
    page_icon="🏃",
    layout="wide"
)

# Add custom CSS for styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .footer {
        font-size: 0.8rem;
        text-align: center;
        margin-top: 2rem;
        color: #888;
    }
    .poster-preview {
        border: 2px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown("<h1 class='main-title'>Marathon Poster Generator</h1>", unsafe_allow_html=True)

# Load and parse GPX file
def load_gpx(uploaded_file):
    try:
        gpx_content = uploaded_file.read().decode('utf-8')
        gpx = gpxpy.parse(gpx_content)
        points = []
        
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    points.append({
                        'lat': point.latitude,
                        'lon': point.longitude,
                        'ele': point.elevation,
                        'time': point.time
                    })
        
        return pd.DataFrame(points)
    except Exception as e:
        st.error(f"Error parsing GPX file: {e}")
        return None

# Clean GPX data (remove noise, smooth track)
def clean_gpx_data(df, smoothing_factor=5):
    if len(df) < 3:
        return df  # Not enough points to smooth
    
    # Convert to numpy arrays for faster processing
    lats = np.array(df['lat'])
    lons = np.array(df['lon'])
    
    # Apply Gaussian smoothing
    lats_smooth = gaussian_filter1d(lats, sigma=smoothing_factor)
    lons_smooth = gaussian_filter1d(lons, sigma=smoothing_factor)
    
    # Create new dataframe with smoothed coordinates
    df_smooth = df.copy()
    df_smooth['lat'] = lats_smooth
    df_smooth['lon'] = lons_smooth
    
    # Remove duplicate points
    df_smooth = df_smooth.drop_duplicates(subset=['lat', 'lon'])
    
    # Remove outliers (points that are too far from their neighbors)
    points = np.column_stack((df_smooth['lon'], df_smooth['lat']))
    distances = []
    
    for i in range(1, len(points)):
        dist = distance.euclidean(points[i-1], points[i])
        distances.append(dist)
    
    distances = np.array([0] + distances)  # Add 0 for the first point
    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    
    # Filter out points that are more than 3 standard deviations away
    mask = distances <= (mean_dist + 3 * std_dist)
    df_clean = df_smooth[mask]
    
    return df_clean

# Generate map image
def create_map_image(df, map_color, route_color, start_color, end_color, width=800, height=800, dpi=100):
    # Create a GeoDataFrame from the route
    geometry = LineString(zip(df['lon'], df['lat']))
    gdf = gpd.GeoDataFrame(index=[0], crs='EPSG:4326', geometry=[geometry])
    
    # Transform to Web Mercator projection for mapping
    gdf = gdf.to_crs(epsg=3857)
    
    # Calculate buffer to add some padding around the route
    bounds = gdf.geometry.bounds
    x_min, y_min, x_max, y_max = bounds.iloc[0]
    
    # Add buffer (10% of width/height)
    buffer_x = (x_max - x_min) * 0.15
    buffer_y = (y_max - y_min) * 0.15
    
    # Create figure and axis with specified size and DPI
    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), dpi=dpi)
    
    # Plot the background map
    gdf.plot(ax=ax, color=route_color, linewidth=3)
    
    # Plot start and end points
    start_point = gdf.geometry.iloc[0].coords[0]
    end_point = gdf.geometry.iloc[0].coords[-1]
    
    # Convert points back to GeoDataFrame for plotting
    start_gdf = gpd.GeoDataFrame(geometry=[gpd.points_from_xy([start_point[0]], [start_point[1]])], crs='EPSG:3857')
    end_gdf = gpd.GeoDataFrame(geometry=[gpd.points_from_xy([end_point[0]], [end_point[1]])], crs='EPSG:3857')
    
    start_gdf.plot(ax=ax, color=start_color, marker='o', markersize=10, zorder=5)
    end_gdf.plot(ax=ax, color=end_color, marker='x', markersize=10, zorder=5)
    
    # Set extent with buffer
    ax.set_xlim(x_min - buffer_x, x_max + buffer_x)
    ax.set_ylim(y_min - buffer_y, y_max + buffer_y)
    
    # Remove axes
    ax.set_axis_off()
    
    # Add basemap
    try:
        basemap_style = {
            'Dark Blue': ctx.providers.CartoDB.DarkMatter,
            'Light': ctx.providers.CartoDB.Positron,
            'Terrain': ctx.providers.Stamen.Terrain,
            'Watercolor': ctx.providers.Stamen.Watercolor,
            'Toner': ctx.providers.Stamen.Toner
        }
        
        ctx.add_basemap(ax, source=basemap_style.get(map_color, ctx.providers.CartoDB.DarkMatter))
    except Exception as e:
        st.warning(f"Could not load basemap: {e}. Using plain background.")
        ax.set_facecolor(map_color)
    
    # Save to bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, dpi=dpi)
    plt.close(fig)
    buf.seek(0)
    
    return Image.open(buf)

# Calculate total distance in kilometers
def calculate_distance(df):
    if len(df) < 2:
        return 0
    
    total_distance = 0
    for i in range(1, len(df)):
        lat1, lon1 = df.iloc[i-1]['lat'], df.iloc[i-1]['lon']
        lat2, lon2 = df.iloc[i]['lat'], df.iloc[i]['lon']
        
        # Haversine formula
        R = 6371  # Earth radius in kilometers
        dlat = np.radians(lat2 - lat1)
        dlon = np.radians(lon2 - lon1)
        a = np.sin(dlat/2)**2 + np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlon/2)**2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1-a))
        distance = R * c
        
        total_distance += distance
    
    return total_distance

# Generate the final poster
def create_poster(map_image, marathon_name, date, athlete_name, bib_number, 
                 distance, duration, pace, logo_path=None):
    # Create a new white image with proper dimensions for printing (A4 proportions)
    width, height = 2480, 3508  # A4 at 300dpi
    poster = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(poster)
    
    # Load fonts
    try:
        title_font = ImageFont.truetype("Arial Bold.ttf", 150)
        date_font = ImageFont.truetype("Arial.ttf", 80)
        details_font = ImageFont.truetype("Arial Bold.ttf", 100)
        label_font = ImageFont.truetype("Arial.ttf", 60)
    except IOError:
        # Use default font if Arial is not available
        title_font = ImageFont.load_default()
        date_font = ImageFont.load_default()
        details_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
    
    # Resize map image to fit the poster
    map_width = int(width * 0.9)
    map_height = int(height * 0.6)
    map_resized = map_image.resize((map_width, map_height), Image.LANCZOS)
    
    # Calculate positions
    margin = 100
    map_position = ((width - map_width) // 2, 300)
    
    # Add title
    title_width = draw.textlength(marathon_name.upper(), font=title_font)
    title_position = ((width - title_width) // 2, 100)
    draw.text(title_position, marathon_name.upper(), fill='black', font=title_font)
    
    # Add date
    date_width = draw.textlength(date, font=date_font)
    date_position = ((width - date_width) // 2, 250)
    draw.text(date_position, date, fill='black', font=date_font)
    
    # Paste map image
    poster.paste(map_resized, map_position)
    
    # Create info section
    info_y = map_position[1] + map_height + 100
    
    # Load Vienna City Marathon logo or use default icon
    logo = None
    logo_size = 200
    
    try:
        if logo_path:
            logo = Image.open(logo_path).resize((logo_size, logo_size), Image.LANCZOS)
        else:
            # Create a simple runner icon
            logo = Image.new('RGBA', (logo_size, logo_size), (0, 0, 0, 0))
            draw_logo = ImageDraw.Draw(logo)
            
            # Draw a simple logo (wreath and runner)
            # Outer wreath (dark blue)
            draw_logo.ellipse((10, 10, logo_size-10, logo_size-10), outline=(33, 37, 99), width=5)
            
            # Draw some laurel leaves (simplified)
            for i in range(0, 360, 45):
                angle_rad = np.radians(i)
                x1 = logo_size//2 + int(logo_size//3 * np.cos(angle_rad))
                y1 = logo_size//2 + int(logo_size//3 * np.sin(angle_rad))
                x2 = logo_size//2 + int(logo_size//2.5 * np.cos(angle_rad))
                y2 = logo_size//2 + int(logo_size//2.5 * np.sin(angle_rad))
                draw_logo.line((x1, y1, x2, y2), fill=(33, 37, 99), width=5)
            
            # Draw runner (stick figure)
            center_x, center_y = logo_size//2, logo_size//2
            # Head
            draw_logo.ellipse((center_x-15, center_y-25, center_x+15, center_y+5), fill=(33, 37, 99))
            # Body
            draw_logo.line((center_x, center_y+5, center_x, center_y+50), fill=(33, 37, 99), width=5)
            # Arms
            draw_logo.line((center_x-30, center_y+20, center_x+30, center_y+20), fill=(33, 37, 99), width=5)
            # Legs
            draw_logo.line((center_x, center_y+50, center_x-25, center_y+80), fill=(33, 37, 99), width=5)
            draw_logo.line((center_x, center_y+50, center_x+25, center_y+80), fill=(33, 37, 99), width=5)

    except Exception as e:
        st.warning(f"Could not load or create logo: {e}")
        logo = Image.new('RGB', (logo_size, logo_size), 'white')
    
    # Paste logo
    if logo:
        logo_position = (margin, info_y)
        poster.paste(logo, logo_position, logo if logo.mode == 'RGBA' else None)
    
    # Add athlete info
    info_x = margin + logo_size + 100
    
    # Horizontal line under athlete name
    line_y = info_y + 150
    draw.line((info_x, line_y, width - margin, line_y), fill='black', width=3)
    
    # Athlete name and bib number
    athlete_text = f"{athlete_name}"
    bib_text = f"#{bib_number}"
    
    draw.text((info_x, info_y + 50), athlete_text, fill='black', font=details_font)
    
    # Calculate position for bib number to be right-aligned
    bib_width = draw.textlength(bib_text, font=details_font)
    draw.text((width - margin - bib_width, info_y + 50), bib_text, fill='black', font=details_font)
    
    # Add distance, time and pace
    stat_y = info_y + 200
    stat_width = (width - 2*margin - logo_size - 100) // 3
    
    # Distance
    distance_text = f"{distance}"
    draw.text((info_x, stat_y), distance_text, fill='black', font=details_font)
    draw.text((info_x, stat_y + 100), "KM", fill='black', font=label_font)
    
    # Time
    time_text = f"{duration}"
    time_x = info_x + stat_width
    draw.text((time_x, stat_y), time_text, fill='black', font=details_font)
    draw.text((time_x, stat_y + 100), "TIME", fill='black', font=label_font)
    
    # Pace
    pace_text = f"{pace}"
    pace_x = info_x + 2 * stat_width
    draw.text((pace_x, stat_y), pace_text, fill='black', font=details_font)
    draw.text((pace_x, stat_y + 100), "/KM", fill='black', font=label_font)
    
    return poster

# Function to convert time strings to seconds
def time_to_seconds(time_str):
    # Parse formats like HH:MM:SS or MM:SS
    parts = time_str.split(':')
    if len(parts) == 3:  # HH:MM:SS
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:  # MM:SS
        return int(parts[0]) * 60 + int(parts[1])
    else:
        return 0

# Function to convert seconds to formatted time strings
def seconds_to_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

# Function to calculate pace from distance and duration
def calculate_pace(distance, duration):
    if distance <= 0:
        return "00:00"
    
    # Convert duration to seconds
    duration_seconds = time_to_seconds(duration)
    
    # Calculate seconds per kilometer
    pace_seconds = duration_seconds / distance
    
    # Convert back to MM:SS format
    minutes = int(pace_seconds // 60)
    seconds = int(pace_seconds % 60)
    
    return f"{minutes:02d}:{seconds:02d}"

# Save image to file with high quality
def save_image(image, filename, quality=95):
    image.save(filename, quality=quality, dpi=(300, 300))
    return filename

# Main application layout
def main():
    # Sidebar for inputs
    with st.sidebar:
        st.markdown("### Upload GPX File")
        uploaded_file = st.file_uploader("Choose a GPX file", type="gpx")
        
        st.markdown("### Marathon Details")
        marathon_name = st.text_input("Marathon Name", "VIENNA CITY MARATHON")
        marathon_date = st.date_input("Date", datetime(2025, 4, 6))
        
        # Format date as DD MONTH YYYY
        formatted_date = marathon_date.strftime("%-d %B %Y").upper()
        
        st.markdown("### Athlete Details")
        athlete_name = st.text_input("Athlete Name", "ATHLETE NAME")
        bib_number = st.text_input("Bib Number", "1234")
        
        st.markdown("### Performance")
        manual_distance = st.text_input("Distance (km)", "42.195")
        duration = st.text_input("Duration (HH:MM:SS)", "00:00:00")
        
        # Calculated pace (user can override)
        try:
            distance_val = float(manual_distance)
            calculated_pace = calculate_pace(distance_val, duration) if duration != "00:00:00" else "00:00"
        except:
            calculated_pace = "00:00"
            
        pace = st.text_input("Pace (MM:SS/km)", calculated_pace)
        
        st.markdown("### Map Customization")
        map_color = st.selectbox(
            "Map Style",
            ["Dark Blue", "Light", "Terrain", "Watercolor", "Toner"]
        )
        
        route_color = st.color_picker("Route Color", "#FFA500")  # Orange by default
        start_color = st.color_picker("Start Point Color", "#FFD700")  # Gold by default
        end_color = st.color_picker("End Point Color", "#FFFFFF")  # White by default
        
        st.markdown("### GPX Cleaning")
        smoothing_factor = st.slider("Smoothing Factor", 1, 10, 5, 
                                   help="Higher values create smoother tracks but might lose details")
        
        st.markdown("### Output")
        output_filename = st.text_input("Output Filename", "marathon_poster.png")
        
        generate_button = st.button("Generate Poster")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("<h2 class='section-header'>Poster Preview</h2>", unsafe_allow_html=True)
        
        preview_placeholder = st.empty()
        
        if uploaded_file is not None:
            # Process GPX file
            df = load_gpx(uploaded_file)
            
            if df is not None and not df.empty:
                # Clean GPX data
                df_clean = clean_gpx_data(df, smoothing_factor)
                
                # Generate map image
                map_image = create_map_image(df_clean, map_color, route_color, start_color, end_color)
                
                # Create poster
                poster = create_poster(
                    map_image, 
                    marathon_name, 
                    formatted_date, 
                    athlete_name, 
                    bib_number, 
                    manual_distance, 
                    duration, 
                    pace
                )
                
                # Display preview
                preview_placeholder.image(poster, caption="Poster Preview", use_column_width=True)
                
                # Generate download link if button pressed
                if generate_button:
                    # Save image to BytesIO
                    buf = io.BytesIO()
                    poster.save(buf, format="PNG", quality=95, dpi=(300, 300))
                    buf.seek(0)
                    
                    # Create download link
                    st.download_button(
                        label="Download Poster",
                        data=buf,
                        file_name=output_filename,
                        mime="image/png"
                    )
                    
                    st.success(f"Poster generated successfully! Click the button above to download.")
            else:
                st.error("Could not process GPX file. Please check the format and try again.")
        else:
            # Display sample image
            st.markdown("""
            ### Welcome to the Marathon Poster Generator!
            
            Upload a GPX file of your marathon route to get started. 
            You'll be able to customize the poster with your marathon details and map styling.
            
            The poster will be generated with high resolution suitable for printing.
            """)
    
    with col2:
        st.markdown("<h2 class='section-header'>Instructions</h2>", unsafe_allow_html=True)
        st.markdown("""
        1. **Upload your GPX file** - This should be the track of your marathon route
        2. **Fill in your marathon details** - Name, date, your name, bib number, etc.
        3. **Customize the map** - Choose colors for the map, route, start and end points
        4. **Adjust GPX cleaning** - Use the smoothing slider if your track has GPS noise
        5. **Set output options** - Choose a filename for your poster
        6. **Generate and download** - Click the Generate button and download your poster
        
        The final poster will be created at high resolution (300 DPI) suitable for printing.
        """)
        
        st.markdown("<h2 class='section-header'>Tips for Best Results</h2>", unsafe_allow_html=True)
        st.markdown("""
        - For best results, use a clean GPX track without too many GPS errors
        - If your track is noisy, increase the smoothing factor
        - Choose contrasting colors for better visibility
        - The final poster is in A4 proportions, ideal for printing
        - For printing, we recommend using at least 300 DPI
        """)
    
    # Footer
    st.markdown("<div class='footer'>Marathon Poster Generator © 2025</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
