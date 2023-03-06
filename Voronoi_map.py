import os
import pandas as pd
import numpy as np
import re

import subprocess
from os.path import abspath

#Importando os dados já completos de prediction

sp_map_file = os.path.join("environment", "spcoords_25x25.csv")
sp_map = pd.read_csv(sp_map_file)

pollutant_values_file =  os.path.join("datasets", "airpol.csv")
airpol = pd.read_csv(pollutant_values_file)

"""
for column in airpol.columns:
    if(re.search("\d{2}\d?-PM10",column)):
        print(column + " this is PM10")
    else:
        print(column + " this is not PM10")
"""

stations_mean_pollutant = dict()

for station_polutant in list(airpol.columns):
    if(station_polutant != "date"):
        stations_mean_pollutant[station_polutant] = airpol[station_polutant].mean()

stations_mean_pollutant_df = pd.Dastations_mean_pollutant

print(stations_mean_pollutant)

    
stationsLonLat = {
    "X90": [-46.62289072700873,-23.578203822677633],
    "X94": [-47.008751971174014,-24.319241548200726],
    "X73": [-46.65660565954331,-23.6270297006414],
    "X83": [-46.66839679340679,-23.6093868814277],
    "X85": [-46.608500659544724,-23.557930926340703],
    "X72": [-46.625831286530456,-23.549441508445522],
    "X99": [-46.701850929651116,-23.567083954515862],
    "X64": [-46.719228544200085,-23.655776028908498],
    "X63": [-46.62467872886001,-23.502383869880937],
    }
    
#full_airpol_df = 
#print(list(airpol.columns))
print(stationsLonLat.get("X85"))