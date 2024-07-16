# %%
import geopandas as gp
import pandas as pd

# %%
shapefile = gp.read_file('C:\\Users\\raaki\\Downloads\\bgd_adm_bbs_20201113_shp\\bgd_admbnda_adm2_bbs_20201113.shp')

# %%
shapefile.to_csv('shapefileBD_data.csv', index=False)


# %%
excel = pd.read_csv('C:\\Users\\raaki\\Downloads\\shapefileBD_data.csv')

# %%
merged_shapefile = shapefile.merge(excel, on='ADM2_EN', how='left')

# %%
merged_shapefile.to_file('merged_shapefile.shp', index=False)

# %%
merged_shapefile.to_file('merged.geojson', driver='GeoJSON')

# %%
import folium
from folium.features import GeoJsonTooltip

# %%
bangladeshMap = folium.Map(location=[23.6850, 90.3563], zoom_start=7, 
               tiles='CartoDB positron',
    attr='Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL.')

# %%
folium.Choropleth(
    geo_data='merged.geojson',
    name='choropleth',
    data=merged_shapefile,               # The GeoDataFrame with the data
    columns=['ADM2_EN', 'ANNUAL AVERAGE '],  # Column with area names and the data column
    key_on='feature.properties.ADM2_EN',  # Key in the GeoJSON features to match with the data
    fill_color='YlGn',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Annual Rainfall Average (mm)'
).add_to(bangladeshMap)

# %%
folium.LayerControl().add_to(bangladeshMap)

# %%
from shapely.geometry import Polygon, MultiPolygon

# %%
def get_centroid(geometry):
    if isinstance(geometry, Polygon):
        return [geometry.centroid.y, geometry.centroid.x]
    elif isinstance(geometry, MultiPolygon):
        return [geometry.centroid.y, geometry.centroid.x]
    else:
        raise TypeError("The geometry must be a Polygon or MultiPolygon.")

# %%
for idx, row in merged_shapefile.iterrows():
    try:
        centroid = get_centroid(row['geometry'])
        tooltip = f"District: {row['ADM2_EN']}<br>Annual Rainfall: {row['ANNUAL AVERAGE ']} mm"
        folium.Marker(location=centroid, tooltip=tooltip).add_to(bangladeshMap)
    except Exception as e:
        print(f"Error processing row {idx}: {e}")

# %%
dengueMap = folium.Map(location=[23.6850, 90.3563], zoom_start=7, 
               tiles='CartoDB positron',
    attr='Map tiles by CartoDB, under CC BY 3.0. Data by OpenStreetMap, under ODbL.')

# %%
import numpy as np

# %%
bins = list(merged_shapefile['CASES AVERAGE'].quantile([0, 0.25, 0.5, 0.75, 1]))

# %%
choropleth = folium.Choropleth(
    geo_data='merged.geojson',
    name='choropleth',
    data=merged_shapefile,
    columns=['ADM2_EN', 'CASES AVERAGE'],
    key_on='feature.properties.ADM2_EN',
    fill_color='OrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Dengue Fever Cases per Capita',
    bins=bins,  # Use the custom bins
).add_to(dengueMap)

# %%
for idx, row in merged_shapefile.iterrows():
    try:
        centroid = get_centroid(row['geometry'])
        tooltip = f"District: {row['ADM2_EN']}<br>Average Dengue Fever Cases per Capita: {row['CASES AVERAGE']}"
        folium.Marker(location=centroid, tooltip=tooltip).add_to(dengueMap)
    except Exception as e:
        print(f"Error processing row {idx}: {e}")

# %%
dengueMap.save('dengueMap.html')

# %%
bangladeshMap.save('rainMap.html')

# %%
map1_html = bangladeshMap.get_root().render()

# %%
map2_html = dengueMap.get_root().render()

# %%
combined_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Combined Maps</title>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        #map1, #map2 {{
            width: 100%;
            height: 50vh;
        }}
    </style>
</head>
<body>
    <h2>Annual Rainfall Average</h2>
    <div id="map1">{map1_html}</div>
    <h2>Dengue Fever Cases per Capita</h2>
    <div id="map2">{map2_html}</div>
</body>
</html>
"""

# %%
with open('combined_bangladesh_map.html', 'w') as file:
    file.write(combined_html)


