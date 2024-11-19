# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 20:22:00 2022

@author: 
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#=============================================================================================#
# read in data and pre-process river data
#=============================================================================================#
eu_riv = gpd.read_file('D:/ProgStuff/Shapefiles/Rivers/europe/eurivs.shp')
eu_riv = eu_riv.drop(['a_cat', 'b_cat', 'b_value', 'b_label'], axis=1)
eu_riv.columns = eu_riv.columns.str.lstrip('a_') 

af_riv = gpd.read_file('D:/ProgStuff/Shapefiles/Rivers/africa/afrivs.shp')
af_riv = af_riv.drop(['DISCHARGE'], axis=1)

au_riv = gpd.read_file('D:/ProgStuff/Shapefiles/Rivers/australia/aurivs.shp')
au_riv = au_riv.drop(['DISCHARGE'], axis=1)

ca_riv = gpd.read_file('D:/ProgStuff/Shapefiles/Rivers/camerica/carivs.shp')
ca_riv = ca_riv.drop(['a_cat', 'b_cat', 'b_value', 'b_label'], axis=1)
ca_riv.columns = ca_riv.columns.str.lstrip('a_') 

na_riv = gpd.read_file('D:/ProgStuff/Shapefiles/Rivers/namerica/narivs.shp')
na_riv = na_riv.drop(['DISCHARGE'], axis=1)

sa_riv = gpd.read_file('D:/ProgStuff/Shapefiles/Rivers/samerica/sarivs.shp')
sa_riv = sa_riv.drop(['a_cat', 'b_cat', 'b_value', 'b_label'], axis=1)
sa_riv.columns = sa_riv.columns.str.lstrip('a_') 

as_riv = gpd.read_file('D:/ProgStuff/Shapefiles/Rivers/asia/asrivs.shp')
as_riv = as_riv.drop(['a_cat', 'b_cat', 'b_value', 'b_label'], axis=1)
as_riv.columns = as_riv.columns.str.lstrip('a_') 

# if file too big read in chunks with rows arg OR just increase / add swap file space to 4 GB (linux)
lakes = gpd.read_file('D:/ProgStuff/Shapefiles/HydroBasins/HydroLAKES_polys_v10_shp/HydroLAKES_polys_v10_shp/HydroLAKES_polys_v10.shp')

#list all river dfs and combine
dflist = [eu_riv, af_riv, au_riv, ca_riv, na_riv, sa_riv, as_riv]
all_riv = gpd.GeoDataFrame(pd.concat(dflist, ignore_index=True), crs=dflist[0].crs)

# subset "rivers in lakes"
excl_riv = gpd.sjoin(all_riv, lakes[['Hylak_id', 'Lake_name', 'geometry']], predicate = 'within')

# remove "rivers in lakes"
all_rivexcl = all_riv.loc[~all_riv.index.isin(excl_riv.index.tolist())]

# plot the rivers to get an idea
fig, ax = plt.subplots(dpi=300)
all_rivexcl.plot(ax=ax, lw=.1)
ax.axis('off')
plt.show()

# create func to compute linewidth based on depth
def scale_lw(df: gpd.GeoDataFrame, column_name: str, min_value: float = 0.005, max_value: float = 0.6, exaggeration_factor: float = 2.0):
    leftSpan = np.amax(df[column_name]) - np.amin(df[column_name])
    rightSpan = exaggeration_factor * (max_value - min_value)
    valueScaled = (df[column_name] - np.amin(df[column_name])) / leftSpan
    df[f'LW_{column_name}'] = 0.005 + (valueScaled * rightSpan)
    return df

# scale the depth col
all_rivexcl = scale_lw(all_rivexcl, 'DEPTH', min_value=0.005, max_value=0.6)

#=============================================================================================#
                          ### COLOURS BASED ON LONGITUDE ###
#=============================================================================================#
fig, ax = plt.subplots(dpi=300)
all_rivexcl.plot(ax=ax, lw=all_rivexcl['LW_DEPTH'])
ax.axis('off')
plt.show()

# extract the y coordinate to use to colour (use [0][0] if need latitude )
all_rivexcl["longitude"] = all_rivexcl['geometry'].apply(lambda geom: geom.xy[1][0] if geom else None) 


# try to add colout to the plot by longitude
fig, ax = plt.subplots(dpi=300)
all_rivexcl.plot(ax=ax, column="longitude", lw=all_rivexcl["LW_DEPTH"], cmap="rainbow")
ax.set_ylim(-75, 75)
ax.axis("off")
plt.show()



#---------------------------------------------------#
# scrub up the plot
#---------------------------------------------------#

#set fontdict for text
font = {'family': 'serif',
        'color':  'lightgray',
        'weight': 'bold',
        'size': 3}

# start plotting
# create a plot
fig, ax = plt.subplots(dpi=500, facecolor = 'slategray')
# plot the df with required colour and line width
all_rivexcl.plot(ax=ax, column="longitude", lw=all_rivexcl["LW_DEPTH"], cmap="rainbow")
# set axis limits so that nothing is cut off
ax.set_xlim(left=-130, right=180)
ax.set_ylim(-75, 75)
# turn the axis off because they don't look good in the plot
ax.axis('off')
# make some customisation
#plt.text(-125, -60, '@plottedstuff', fontdict=font)
#plt.text(-125, -65, 'data from Global River Database and Hydrosheds', fontdict=font)
#fig.savefig("world_rivs_lvl2_rainbow.png", dpi = 500, bbox_inches='tight')
plt.show()



#=============================================================================================#
                          ### COLOURS BASED ON Hydbas ###
#=============================================================================================#
# read in hydbas data - only australia here
hydbas_au = gpd.read_file('D:/ProgStuff/Shapefiles/HydroBasins/hybas_au_lev01-12_v1c/hybas_au_lev03_v1c.shp')

# subset australia lakes
lakes.head(10) # have a llok at the first few rows
list(lakes.columns) # have a look at the cols in the df
print(lakes["Continent"].tail()) # have a look at the first/last few rows of a column
print(lakes["Country"].eq("Australia")) # check ig the col contains the entry
cond = lakes["Country"] == "Australia" # create condition to subset
lake_au = lakes[cond] # create subset

# subset
excl_riv = gpd.sjoin(au_riv, lake_au[["Hylak_id", "Lake_name", "geometry"]], predicate = "within")

# remove lakes from au_riv df
au_rivexcl = au_riv.loc[~au_riv.index.isin(excl_riv.index.tolist())]

# plot the df
fig, ax = plt.subplots(dpi=300)
au_rivexcl.plot(ax=ax, lw=.1)
ax.axis("off")
plt.show()

# compute the linewidth - make sure function (above) is run
au_rivexcl_d = scale_lw(au_rivexcl, "DEPTH", min_value=0.005, max_value=0.6)

# plot with adjusted linewidth
fig, ax = plt.subplots(dpi=300)
au_rivexcl_d.plot(ax=ax, lw=au_rivexcl_d["LW_DEPTH"])
ax.axis("off")
plt.show()

# create list with colours to use later
cols = ["red", "lawngreen", "cyan", "blue", "yellow", "silver", "fuchsia",
        "lightcoral", "brown", "maroon", "gray", "chocolate", "saddlebrown", "peru",
        "darkorange", "burlywood", "violet", "orange", "goldenrod", "gold", "darkkhaki",
        "olivedrab", "yellowgreen", "darkseagreen", "palegreen", "forestgreen", "limegreen","lime", 
        "plum", "springgreen", "aquamarine", "lightseagreen", "teal","cadetblue","lightblue", 
        "deepskyblue", "steelblue", "dodgerblue", "slategray","rebeccapurple","indigo", "darkorchid", 
        "mediumseagreen", "tan", "mediumvioletred","deeppink","lightpink"]

# convert cols to df and include hydrobasins
cols_df = pd.DataFrame({'hydbasin': hydbas_au.HYBAS_ID.unique().tolist(), 'cols': cols})

# merge cols_df and hydbas
hydbas_au_col = pd.merge(hydbas_au, cols_df, left_on='HYBAS_ID', right_on='hydbasin', how='left')

# join the rivers df and hydbas df
riv_hydbas = gpd.sjoin(au_rivexcl, hydbas_au_col, how='inner', predicate='intersects')

# scale linewidth based on depth
riv_hydbas = scale_lw(riv_hydbas, 'DEPTH', min_value=0.005, max_value=.6, exaggeration_factor=1)

# plot
fig, ax = plt.subplots(dpi=500, facecolor = "linen")
riv_hydbas.plot(ax=ax, edgecolor="black", linewidth=3)
riv_hydbas.plot(ax=ax, color=riv_hydbas["cols"], lw=riv_hydbas["LW_DEPTH"])
ax.axis("off")
#plt.text(-125, -60, "@plottedstuff", fontdict=font)
#plt.text(-125, -65, "data from Global River Database and Hydrosheds", fontdict=font)
plt.show()



# play aroung with exaggeration factor, and remove Oceania islands - except NZ














