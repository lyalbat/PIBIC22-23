import os
import pandas as pd
import numpy as np
import re
import pykrige
import matplotlib.pyplot as plt

import subprocess
from os.path import abspath
import pykrige.kriging_tools as kt
from pykrige.ok import OrdinaryKriging

def as_grid25(dataMatrix, gridsize = 25, nmax = 1000):
    step = int(nmax/gridsize)
    sectors = np.arange(0,1000,step)
    coverageMatrix = np.zeros((25,25))
    
    #Creating the gridded map
    for i in range(0, len(sectors)):
        for j in range(0, len(sectors)):
            
            #analysing the original sectors and downsizing
            for x in range(sectors[i],sectors[i]+(step-1)):
                for y in range(sectors[j],sectors[j] + (step -1)):
                    #if there's a sample, cover the sector
                    if(dataMatrix[x,y] == 1):
                        coverageMatrix[i,j] = 1
    return coverageMatrix

#Importando os dados já completos de prediction

sp_map_file = os.path.join("environment", "spcoords_25x25.csv")
sp_map = pd.read_csv(sp_map_file)

pollutant_values_file =  os.path.join("datasets", "airpol.csv")
airpol = pd.read_csv(pollutant_values_file)

PM10_list, CO_list, NO2_list, SO2_list, O3_list = [], [], [], [], []
PM10_coords_list, CO_coords_list, NO2_coords_list, SO2_coords_list, O3_coords_list = [], [], [], [], []  


def checkStation(station_number, coords):
    return "Ok"

for station_polutant in list(airpol.columns):
    if(re.search("\d{2}\d?-PM10",station_polutant)):
        PM10_coords_list.append(station_polutant)
        PM10_list.append(airpol[station_polutant].mean())
    elif(re.search("\d{2}\d?-CO",station_polutant)):
        CO_coords_list.append(station_polutant)
        CO_list.append(airpol[station_polutant].mean())
    elif(re.search("\d{2}\d?-NO2",station_polutant)):
        NO2_coords_list.append(station_polutant)
        NO2_list.append(airpol[station_polutant].mean())
    elif(re.search("\d{2}\d?-SO2",station_polutant)):
        SO2_coords_list.append(station_polutant)
        SO2_list.append(airpol[station_polutant].mean())
    elif(re.search("\d{2}\d?-O3",station_polutant)):
        O3_coords_list.append(station_polutant)
        O3_list.append(airpol[station_polutant].mean())
        
#stations_mean_pollutant_df = pd.stations_mean_pollutant

stations_pollutants_pd = {
    "PM10": PM10_list,
     "CO": CO_list,
     "NO2": NO2_list,
     "SO2": SO2_list,
     "O3": O3_list,
     }
#print(stations_pollutants_pd)

    
stationsLonLat = {
    "X90" : [-23.578203822677633,-46.62289072700873],
    "X94": [-24.319241548200726,-47.008751971174014],
    "X73": [-23.6270297006414,-46.65660565954331],
    "X83": [-23.6093868814277,-46.66839679340679],
    "X85": [-23.557930926340703,-46.608500659544724],
    "X72": [-23.549441508445522,-46.625831286530456],
    "X99": [-23.567083954515862,-46.701850929651116,],
    "X64": [-23.655776028908498,-46.719228544200085],
    "X63": [-23.502383869880937,-46.62467872886001],
    }
    
#full_airpol_df = 
#print(list(airpol.columns))

import itertools

X_coords = [
         stationsLonLat["X90"][0],
         stationsLonLat["X83"][0],
         stationsLonLat["X85"][0],
         stationsLonLat["X72"][0],
         stationsLonLat["X99"][0],
         stationsLonLat["X64"][0],
         stationsLonLat["X63"][0]
         ]
Y_coords = [stationsLonLat["X90"][1],
         stationsLonLat["X83"][1],
         stationsLonLat["X85"][1],
         stationsLonLat["X72"][1],
         stationsLonLat["X99"][1],
         stationsLonLat["X64"][1],
         stationsLonLat["X63"][1]
         ]

coords_matrix = np.column_stack((X_coords,Y_coords))
coords_25_25 = as_grid25(coords_matrix)
'''
OK = OrdinaryKriging(
    X_coords,
    Y_coords,
    stations_pollutants_pd["PM10"],
    variogram_model="linear",
    verbose=False,
    enable_plotting=False)


gridx = np.arange(-23.4, -24.4, -0.0001)
gridy = np.arange(-46.6, -47.1, -0.0001)

z, ss = OK.execute("grid", gridx, gridy)
kt.write_asc_grid(gridx, gridy, z, filename="OK_PM10.asc")
plt.imshow(z)
plt.show()

'''
