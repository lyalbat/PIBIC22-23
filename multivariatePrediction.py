#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  5 13:26:56 2022

@author: larissa
"""

#from prediction import estacoes_t
import os
import pandas as pd
from datetime import *
from functools import reduce
import numpy as np
from numpy import asarray
import cv2


import subprocess
from os.path import abspath

'''
#Importando pacotes necessarios para conversao R -> Python
import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr, data

#Loading basic R packages
utils = importr('utils')
base = importr('base')

#Loading gstats
utils.chooseCRANmirror(ind=1)
utils.install_packages('gstat')
gstat = importr('gstat')

#from rpy2.robjects import pandas2ri

#from rpy2.robjects.packages import gstat
#from rpy2.robjects.conversion import localconverter
'''

#Importando os dados já completos de prediction

#from prediction import estacoes_t as airpol
#airpol.to_csv(r'/home/larissa/Documents/airPolution\airpol.csv', index=False)
airpol = pd.read_csv('/home/larissa/Documents/airPolution/airpol.csv')


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


def sectorize_coord():
    all_stations = np.zeros((1000,1000));
    all_stations[240][540] = 1 # X73 (meu) : X8 - CONGONHAS
    all_stations[300][780] = 1 # X94 (meu) : X12 - CENTRO
    all_stations[320][680] = 1 # X90 (meu) : X4 - CAMBUCI
    all_stations[230][600] = 1 # X83 (meu) : X5 - IBIRAPUERA
    all_stations[360][720] = 1 # X85 (meu) : X3 - MOOCA
    all_stations[250][430] = 1 # X72 (meu) : X1 - P. D. PEDRO II
    all_stations[210][720] = 1 # X99 (meu) : X27 - PINHEIROS
    all_stations[230][810] = 1 # X63 (meu) : X2 - SANTANA
    all_stations[250][480] = 1 # X64 (meu) : X16 - SANTO AMARO
    
    all_stations = as_grid25(all_stations) # 1
    rows, cols = np.where(all_stations == 1)
    all_stations = np.vstack((rows, cols)).T
    #Talvez usar: all_stations[np.arange(condicional- all_stations == 1)]
	#all_stations = all_stations[order(all_stations[,1]),] # 3
    
    return(all_stations)


def map_coords():
    img_path = os.path.join(os.path.expanduser('~'),'Documents','airPolution','spmap.png')
    img = cv2.imread(img_path,0);
    spmap = img / 255.0;
    
    coords = as_grid25(spmap).astype(int)
    coords = np.where((coords==0)|(coords==1), (coords)^1, coords)
    #print(coords)
    
    return coords

def combination(station_id, var_name):
    df_cols = np.array(np.meshgrid(station_id,var_name)).T
    
    df_cols = np.concatenate((df_cols[0],df_cols[2],df_cols[4],df_cols[7],df_cols[8]),axis=0)
    
    df_cols = np.delete(df_cols,np.where(df_cols[:,1] == 'SO2') ,axis=0)
    df_cols = np.delete(df_cols,np.where(df_cols[:,1] == 'NO2') ,axis=0)
    df_cols = pd.DataFrame(data = df_cols,columns = ['Var2', 'Var1'])
    return df_cols


sp_coords = map_coords()
#No original as coordenadas sao convertidas em um csv...talvez fazer
#write.csv(sp_coords, "../environment/spcoords_25x25.csv", row.names=FALSE)

station_coord = sectorize_coord()
#tation_coord['coordinates'] = df[['Year', 'quarter', ...]].agg('-'.join, axis=1)

station_id = [["73"],["94"],["90"],["83"],["85"],["72"],["99"],["63"],["64"]]
var_name = [["CO"],["PM10"], ["O3"], ["NO2"], ["SO2"]]

station_id_coord = np.append(station_id,station_coord, axis = 1)

df_cols = combination(station_id, var_name)


#Deve ser modularizado como uma funcao snapshot:

def snapshot_series(airpol, station_ids,var_names,station_coords,snapshot_prev=None):
    if(var_names[-1] == 'O3'):
        PM10,CO,O3 = [],[],[]
        station_id_CO_PM10_03 = station_ids
        var_name_CO_PM10_O3 = var_names
        
        #Ainda nao sei se vai ser util, mas adicionei
        to_predict = []
        
        for row in airpol:
          station, pol = row.split('-')
          if(station in station_id_CO_PM10_03 and pol in var_name_CO_PM10_O3):
            if(pol == "CO"):
              CO.append(airpol[row])
            elif(pol == "PM10"):
              PM10.append(airpol[row])
            else:
              O3.append(airpol[row])
          else:
            to_predict.append(airpol.pop(row))
        
        PM10,CO,O3 = np.array(PM10),np.array(CO), np.array(O3)
        new_PM10,new_CO,new_O3 = [], [], []
        
        #Possivel usar len(CO[0]), porque todos tem mesmo comprimento
        #Formatacao - cada array é um timestamp, cada coluna uma estacao
        
        for row2 in range(len(CO[0])):
          new_CO.append(CO[:,row2])
          new_O3.append(O3[:,row2])
          new_PM10.append(PM10[:,row2])
        
        new_CO, new_PM10, new_O3 = np.vstack(new_CO), np.vstack(new_PM10), np.vstack(new_O3)
        
        snapshot = []
        CO_PM10_O3_coords = station_coords
        
        for timestamp in range(len(new_CO)):
            aux  = CO_PM10_O3_coords.copy()
            aux['CO'] = new_CO[timestamp].tolist()
            aux['PM10'] = new_PM10[timestamp].tolist()
            aux['O3'] = new_O3[timestamp].tolist()
            snapshot.append(aux)
    #A partir daqui tem que adaptar:
            
    elif(var_names[-1] == 'NO2'):
        #Precisa arrumar ainda - o snapshot_prev serve para reduzir tempo de processamento
        PM10,CO,O3 = [],[],[]
        station_id_CO_PM10_03 = station_ids
        var_name_CO_PM10_O3 = var_names
        
        #Ainda nao sei se vai ser util, mas adicionei
        to_predict = []
        
        for row in airpol:
          station, pol = row.split('-')
          if(station in station_id_CO_PM10_03 and pol in var_name_CO_PM10_O3):
            if(pol == "CO"):
              CO.append(airpol[row])
            elif(pol == "PM10"):
              PM10.append(airpol[row])
            else:
              O3.append(airpol[row])
          else:
            to_predict.append(airpol.pop(row))
        
        PM10,CO,O3 = np.array(PM10),np.array(CO), np.array(O3)
        new_PM10,new_CO,new_O3 = [], [], []
        
        #Possivel usar len(CO[0]), porque todos tem mesmo comprimento
        #Formatacao - cada array é um timestamp, cada coluna uma estacao
        
        for row2 in range(len(CO[0])):
          new_CO.append(CO[:,row2])
          new_O3.append(O3[:,row2])
          new_PM10.append(PM10[:,row2])
        
        new_CO, new_PM10, new_O3 = np.vstack(new_CO), np.vstack(new_PM10), np.vstack(new_O3)
        
        snapshot = []
        CO_PM10_O3_coords = station_coords
        
        for timestamp in range(len(new_CO)):
            aux  = CO_PM10_O3_coords.copy()
            aux['CO'] = new_CO[timestamp].tolist()
            aux['PM10'] = new_PM10[timestamp].tolist()
            aux['O3'] = new_O3[timestamp].tolist()
            snapshot.append(aux)
    elif(var_names[-1] == 'SO2'):
        #Precisa arrumar ainda - o snapshot_prev serve para reduzir tempo de processamento
        PM10,CO,O3 = [],[],[]
        station_id_CO_PM10_03 = station_ids
        var_name_CO_PM10_O3 = var_names
        
        #Ainda nao sei se vai ser util, mas adicionei
        to_predict = []
        
        for row in airpol:
          station, pol = row.split('-')
          if(station in station_id_CO_PM10_03 and pol in var_name_CO_PM10_O3):
            if(pol == "CO"):
              CO.append(airpol[row])
            elif(pol == "PM10"):
              PM10.append(airpol[row])
            else:
              O3.append(airpol[row])
          else:
            to_predict.append(airpol.pop(row))
        
        PM10,CO,O3 = np.array(PM10),np.array(CO), np.array(O3)
        new_PM10,new_CO,new_O3 = [], [], []
        
        #Possivel usar len(CO[0]), porque todos tem mesmo comprimento
        #Formatacao - cada array é um timestamp, cada coluna uma estacao
        
        for row2 in range(len(CO[0])):
          new_CO.append(CO[:,row2])
          new_O3.append(O3[:,row2])
          new_PM10.append(PM10[:,row2])
        
        new_CO, new_PM10, new_O3 = np.vstack(new_CO), np.vstack(new_PM10), np.vstack(new_O3)
        
        snapshot = []
        CO_PM10_O3_coords = station_coords
        
        for timestamp in range(len(new_CO)):
            aux  = CO_PM10_O3_coords.copy()
            aux['CO'] = new_CO[timestamp].tolist()
            aux['PM10'] = new_PM10[timestamp].tolist()
            aux['O3'] = new_O3[timestamp].tolist()
            snapshot.append(aux)
    else:
        pass
    
    return snapshot

#PREDICTION - FIRST STEP
var_name_CO_PM10_O3 = ["CO", "PM10", "O3"]
station_id_CO_PM10_O3 = ["83","85","72","99"]

CO_PM10_O3_coords = pd.DataFrame(station_id_coord, columns = ['station_id', 'x','y']).drop([0,1,2,7,8]).reset_index()
#CO_PM10_O3_coords['coordinates'] = CO_PM10_O3_coords.apply(lambda x: [x['x'], x['y']], axis=1)
airpol_1st_pred = airpol.copy()

airpol_1st_pred = airpol_1st_pred.set_index('date')
CO_PM10_O3_coords = CO_PM10_O3_coords.drop('index',axis=1)
#CO_PM10_O3_coords = CO_PM10_O3_coords.drop(['index','x','y'],axis=1)
station_id_CO_PM10_03 = ["83","85","72","99"]
var_name_CO_PM10_O3 = ["CO", "PM10", "O3"]


CO_PM10_03_snapshot_series = snapshot_series(airpol_1st_pred, station_id_CO_PM10_03,var_name_CO_PM10_O3,CO_PM10_O3_coords)

#Exportando o snapshot do 1st step para o usar no R (teste)
#CO_PM10_03_snapshot_series.to_csv('CO_PM10_03_snapshot_series.csv')

def callingR(snapshots):
  for elemIndex in range(len(snapshots)):
      path = "dataframes_snapshots/snapshot_series_" + str(elemIndex + 1)  + ".csv"
      absPath = abspath(path)
      df = snapshots[elemIndex]
      
      #Criação de arquivo csv síncrona
      df.to_csv(absPath)
      print(df)
      
  return len(snapshots)

def predict_series():
    
    rPath = abspath("listR_teste.R")
    command = "Rscript " + rPath
    subprocess.call(command, shell=True)

print("Numero de dataframes observados: ", callingR(CO_PM10_03_snapshot_series))


#CO_PM10_03_reconst = predict_series(CO_PM10_03_snapshot_series,var_name_CO_PM10_O3,sp_coords)

#print(new_CO)
