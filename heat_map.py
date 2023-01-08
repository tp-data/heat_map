import json
import country_converter as coco
from datetime import datetime, timedelta
import requests
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib as mpl
import sys

csv = sys.argv[1]

df = pd.read_csv(csv)

df = df.groupby(['code']).agg({'value':'sum'}).reset_index()

SHAPEFILE = 'ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp'

geo_df = gpd.read_file(SHAPEFILE)[['ADMIN', 'ADM0_A3', 'geometry']] # Read shapefile using Geopandas
geo_df.columns = ['country', 'country_code', 'geometry'] # Rename columns
geo_df = geo_df.drop(geo_df.loc[geo_df['country'] == 'Antarctica'].index)
geo_df.plot(figsize=(20, 20), edgecolor='white', linewidth=1, color='lightblue') # Print the map

iso3_codes = geo_df['country'].to_list() # Next, we need to ensure that our data matches with the country codes. 
iso2_codes_list = coco.convert(names=iso3_codes, to='ISO2', not_found='NULL') # Convert to iso3_codes

geo_df['iso2_code'] = iso2_codes_list # Add the list with iso2 codes to the dataframe
# There are some countries for which the converter could not find a country code. 
geo_df = geo_df.drop(geo_df.loc[geo_df['iso2_code'] == 'NULL'].index) # We will drop these countries.

merged_df = pd.merge(left=geo_df, right=df, how='left', left_on='iso2_code', right_on='code') # Merge the two dataframes
df_merged = merged_df.drop(['code'], axis=1) # Delete some columns that we won't use
df_merged['value'].fillna(0, inplace=True) #Create the indicator values

# Set up map
title = 'World Heat Map'
col = 'value' # Set the range for the choropleth
source = '' # Add text 
vmin = df_merged[col].min()
vmax = df_merged[col].max()
cmap = (mpl.colors.ListedColormap(['gray', '#1E90FF', '#187DE9', '#126AD2', '#0C56BC', '#0643A5', '#00308F'])
        .with_extremes(over='0.25', under='0.75'))
bounds = [1, 2, 4, 7, 8]
norm = mpl.colors.BoundaryNorm(bounds, cmap.N)

# Create figure and axes for Matplotlib
fig, ax = plt.subplots(1, figsize=(20, 8))
ax.axis('off') # Remove the axis
df_merged.plot(column=col, ax=ax, edgecolor='.8', linewidth=1, cmap=cmap)
ax.set_title(title, fontdict={'fontsize': '25', 'fontweight': '3'}) # Add a title
# Create an annotation for the data source
ax.annotate(source, xy=(0.1, .08), xycoords='figure fraction', horizontalalignment='left', 
            verticalalignment='bottom', fontsize=10)
            
sm = plt.cm.ScalarMappable(norm=plt.Normalize(vmin=vmin, vmax=vmax), cmap=cmap) # Create colorbar as a legend
sm._A = [] # Empty array for the data range
cbaxes = fig.add_axes([0.15, 0.25, 0.01, 0.4]) # Add the colorbar to the figure
cbar = fig.colorbar(sm, cax=cbaxes)

plt.savefig('heat_map.png')
