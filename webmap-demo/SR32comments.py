# -*- coding: utf-8 -*-
"""
Created on Fri Feb  7 22:49:19 2025

@author: saleh
"""

import geopandas as gpd
import folium
import pandas as pd
import numpy as np
import matplotlib.colors as mcolors
from branca.element import Element

# Load the Shapefile
gdf = gpd.read_file("df_map_export.shp")

# Rename columns
gdf = gdf.rename(columns={"liked": "like", "red_dots": "dislike"})

# Replace NaN values with 0 for 'like' and 'dislike' columns
gdf[["like", "dislike"]] = gdf[["like", "dislike"]].fillna(0)

# Ensure 'like' and 'dislike' columns are numeric
gdf["like"] = pd.to_numeric(gdf["like"], errors="coerce").fillna(0)
gdf["dislike"] = pd.to_numeric(gdf["dislike"], errors="coerce").fillna(0)

# Step 1: Forcefully set the correct CRS (EPSG:3857) without transforming
gdf = gdf.set_crs(epsg=3857, allow_override=True)  # Override the incorrect EPSG:4326

# Step 2: Convert it to Latitude/Longitude (EPSG:4326)
gdf = gdf.to_crs(epsg=4326)

# Print the transformed data
print(gdf.head())
print("Bounding Box:", gdf.total_bounds)

# ✅ Define colors based on the `categories` column
category_colors = {
    "alternative SR32 route": "#E5E4E2",  # Light gray
    "congestion problem": "#DC7633",  # Orange
    "finish the SR32 trail": "#145A32",  # Dark green
    "Improve Landscaping": "#1E8449",  # Green
    "improve pedestrian crossing": "#2ECC71",  # Light green
    "improve sidewalk/trails/biking facilities": "#1ABC9C",  # Cyan
    "improve walkable city centers": "#48C9B0",  # Teal
    "Limit the developments": "#800080",  # 🟣 Purple
    "more commercials/local commercials": "#00008B",  # 🔵 Very Dark Blue
    "preserve rural character/farm lands/corridor view/dark sky/wildlife": "#3498DB",  # Blue
    "proposing roundabout/bypass": "#654321",  # 🟤 Dark Brown
    "reduce parking": "#B7950B",  # Yellow-brown
    "safety issue": "#FFFF00",  # 🟡 Yellow
    "Speeding Issues": "#FF0000",  # 🔴 Red
    "other": "#808080"  # Gray (default color)
}

# ✅ Ensure `categories` column has valid values
gdf["categories"] = gdf["categories"].fillna("other").astype(str).str.strip()

# ✅ Get unique categories in the dataset
unique_categories = gdf["categories"].unique()

# ✅ Debugging: Print categories to verify mapping
print("Unique Categories in Dataset:", unique_categories)
print("Category Colors Mapping:", category_colors)

# Center the map on the dataset
map_center = [gdf.geometry.y.mean(), gdf.geometry.x.mean()]

# ✅ Set Light Gray Basemap (CartoDB Positron)
m = folium.Map(location=map_center, zoom_start=12, tiles="CartoDB Positron")

# Determine max value of "like" for scaling
max_likes = gdf["like"].max() if gdf["like"].max() > 0 else 1  # Avoid division by zero

# ✅ Assign colors to markers using `categories`
for _, row in gdf.iterrows():
    lat, lon = row.geometry.y, row.geometry.x
    category = row["categories"]  # ✅ Get category from the dataset
    likes = int(row["like"])
    dislikes = int(row["dislike"])
    row_id = int(row["id"])
    comments = row.get("comments", "N/A")  # Keep as string

    # ✅ Get color based on the category
    color = category_colors.get(category, "#808080")  # Default to gray if not found

    # ✅ Scale marker size (min 5, max 20)
    size = 5 + (likes / max_likes) * 15  # Scale between 5 and 20

    # ✅ Popup includes category
    popup_content = f"""
    <b>Category:</b> {category}<br>
    <b>ID:</b> {row_id}<br>
    <b>Comments:</b> {comments}<br>
    <b>Likes:</b> {likes}<br>
    <b>Dislikes:</b> {dislikes}
    """

    # ✅ Apply correct category color to the map
    folium.CircleMarker(
        location=[lat, lon],
        radius=size,
        color=color,  # ✅ Border color
        fill=True,
        fill_color=color,  # ✅ Fill color
        fill_opacity=0.7,
        popup=folium.Popup(popup_content, max_width=400)  # Increased width
    ).add_to(m)

# ✅ Move "other" to the bottom of the legend
sorted_categories = [cat for cat in category_colors.keys() if cat != "other"]
sorted_categories.append("other")  # Add "other" at the end

# ✅ Final legend with correct position & scrolling
legend_html = f"""
<div style="
    position: fixed; 
    top: 100px; left: 20px; /* Moves the legend down */
    width: 260px; 
    max-height: 400px; /* Allows more space before scrolling */
    background-color: rgba(255, 255, 255, 0.95); 
    z-index: 10000; font-size: 13px; /* Adjust font size slightly */
    border-radius: 8px; padding: 12px; 
    box-shadow: 3px 3px 6px rgba(0,0,0,0.5);
    font-family: Arial, sans-serif;
    line-height: 1.4;
    overflow-y: auto; /* Enables scrolling if needed */
">
    <b>Legend</b><br>
    <hr style="margin: 5px 0;">
    {''.join([
        f"""<div style="display: flex; align-items: center; margin: 7px 0;">
        <div style="width: 18px; height: 18px; background:{category_colors[category]}; 
        margin-right: 12px; border-radius: 4px; border: 1px solid black;"></div>{category}</div>"""
        for category in sorted_categories
    ])}
</div>
"""

# ✅ Add the legend using `Element`
legend = Element(legend_html)
m.get_root().html.add_child(legend)

# Save map to file
map_path = r"C:\Users\saleh\OneDrive\Desktop\Dorsa\Final\map.html"
m.save(map_path)

print(f"Map saved to: {map_path}")
