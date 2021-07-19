# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 20:42:11 2020

@author: jiching
"""
    ############## python 下載波形兼畫cross section的程式  ##############

import pandas as pd
from toRTZ import enztortz
from waveform_plot_all_bob import WaveformPlotAll
from download_waveform_bob import download_waveform
from waveform_plot_indiv_bob import WaveformPlotIndiv

     ######### Obervation Setup ##########
dleft, dright = 0, 120*60                # waveform cut length (left and right relative to origin time)
waveform_type = 'DISP'
model_name = "ak135"
freqmin = 0.01
freqmax = 10
minlat = 15
maxlat = 25
minlon = -105
maxlon = -95

    ############## DO WHAT ###############
data = 0                               # Download data and remove instrument response
                                        # Download data 
                                        # remove instrument response
                                        
waveform_plot_individual = 1            # Plot individual waveforms 
waveform_plot_all_in_distance = 0       # Plot the waveform of all stations (arrange in distance)
ENZtoRTZ = 0
############## read catalog ##############
i = 12
event_info_df = pd.read_csv("event_catalog.csv")
event_name = event_info_df.loc[i,'event_name']
time = event_info_df.loc[i,'origin_time']
# latitude and longitude
cevent = [ event_info_df.loc[i,'latitude'], event_info_df.loc[i,'longitude'] ]

# files define
download_dir = event_name + "_projects/"
event_catalog = "event_catalog.csv"
################ download the data & plot stations##############
if data:
    download_waveform(event_name, time, cevent, dleft, dright, waveform_type,
                      minlat,minlon,maxlat,maxlon, download_dir = download_dir)
################ plot waveform for individual stations ##############
if waveform_plot_all_in_distance:
    WaveformPlotAll(i,'HHZ',event_name,waveform_type,dleft=dleft, download_dir=download_dir,event_catalog=event_catalog,
                    model_name=model_name, freqmin=freqmin, freqmax=freqmax)
if waveform_plot_individual:
    WaveformPlotIndiv(i,event_name,waveform_type,dleft=dleft, download_dir=download_dir,event_catalog=event_catalog,
                      model_name=model_name, freqmin=freqmin, freqmax=freqmax)
## ENZ to RTZ
if ENZtoRTZ:
    enztortz(i,event_name,waveform_type,dleft=dleft, download_dir=download_dir,event_catalog=event_catalog)    