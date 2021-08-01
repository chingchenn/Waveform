# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 20:42:11 2020
@author: jiching
"""
    ############## python 下載波形兼畫cross section的程式  ##############

import pandas as pd
from toRTZ import enztortz
from plot_enzrt import WaveformPlotIndivENZRT
from waveform_plot_all import WaveformPlotAll
from download_waveform import download_waveform
from waveform_plot_indiv import WaveformPlotIndiv

     ######### Obervation Setup ##########
dleft, dright = 0, 30*60                # waveform cut length (left and right relative to origin time)
waveform_type = 'DISP'
model_name = "ak135"
freqmin = 0.01
freqmax = 1
minlat = 15
maxlat = 25
minlon = -105
maxlon = -95

    ############## DO WHAT ###############
data = 0                               # Download data and remove instrument response                           
waveform_plot_individual = 0            # Plot individual waveforms 
waveform_plot_all_in_distance = 0       # Plot the waveform of all stations (arrange in distance)
ENZtoRTZ = 1
plot_enzrt=1
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
    channel_list=['HHE','HHN','HHZ']
    for channel in channel_list:
        WaveformPlotAll(i,channel,event_name,waveform_type,dleft=dleft, download_dir=download_dir,event_catalog=event_catalog,
                    model_name=model_name, freqmin=freqmin, freqmax=freqmax)
if waveform_plot_individual:
    WaveformPlotIndiv(i,event_name,waveform_type,dleft=dleft, download_dir=download_dir,event_catalog=event_catalog,
                      model_name=model_name, freqmin=freqmin, freqmax=freqmax)
## ENZ to RTZ
if ENZtoRTZ:
    enztortz(i,event_name,waveform_type,dleft=dleft, download_dir=download_dir,event_catalog=event_catalog)
if plot_enzrt:
    WaveformPlotIndivENZRT(i,event_name,waveform_type,dleft=0, download_dir=download_dir,event_catalog="event_catalog.csv",model_name="iasp91", freqmin=0.01, freqmax=1)    