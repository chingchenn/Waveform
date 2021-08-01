# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 22:20:58 2020

@author: grace
"""

import glob
import obspy
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from support_modules import create_dir
from obspy.geodetics.base import gps2dist_azimuth, kilometer2degrees
from obspy.taup import TauPyModel
from obspy.clients.iris import Client
from obspy import read
from obspy.core import UTCDateTime
import math

client = Client()
plt.style.use('seaborn')

def WaveformPlotIndivENZRT(i,event_name,waveform_type,dleft=0, download_dir="projects/",event_catalog="event_catalog.csv",model_name="iasp91", freqmin=0.03, freqmax=1):

    print('####################################################################')
    print('#################### Individual Waveform Plot  #####################')
    print('####################################################################')
    
        # event info read in
    event_info_df = pd.read_csv("event_catalog.csv")
    event_name = event_info_df.loc[i,'event_name']
    time = event_info_df.loc[i,'origin_time']
    evlat=event_info_df.loc[i,'latitude']
    evlon=event_info_df.loc[i,'longitude']
    model = TauPyModel(model=model_name)
    
        # waveforms location  
    # new_waveforms_loc = download_dir+f"{waveform_type}_"+event_name 
    rtz_waveforms_loc = download_dir+f"{event_name}_mseed_RTZ"
    # storage directory
    p_s_df = download_dir+event_name+f"_enzrt_{freqmin}-{freqmax}/"
    if os.path.exists(p_s_df):
        print(f'{p_s_df} exists!')
    else:
        create_dir(p_s_df)
    
        # station info read in
    old_sta='bob'
    station_info_df = pd.read_csv(download_dir+f"enzrt_station_info_{event_name}.csv")
    # rtz_info_df = pd.read_csv(download_dir+f"rtz_info_{event_name}.csv")
    for i,net in enumerate(station_info_df['Net']):
        print('==========================================')
        sta = station_info_df.loc[i,'Sta']
        cha = station_info_df.loc[i,'Cha']
        sta_lon = station_info_df.loc[i,'Sta_lon']
        sta_lat = station_info_df.loc[i,'Sta_lat']
        # if math.isnan(loc):
        #     wavefm = f"{new_waveforms_loc}/{waveform_type}_{net}.{sta}..{cha}.mseed"
        # else:
        #     wavefm = f"{new_waveforms_loc}/{waveform_type}_{net}.{sta}.{int(loc):02}.{cha}.mseed"
        wavefm=rtz_waveforms_loc+'/*'+net+'*'+sta+'*'+cha+'.mseed'
        print(wavefm)
        r_wave = f"{rtz_waveforms_loc}/{net}_{sta}_R.mseed"
        t_wave = f"{rtz_waveforms_loc}/{net}_{sta}_T.mseed"
        e_wave = download_dir+'waveforms_20060127_Banda_Sea/'+net+'*'+sta+'*'+'HHE'+'*.mseed'
        n_wave = download_dir+'waveforms_20060127_Banda_Sea/'+net+'*'+sta+'*'+'HHN'+'*.mseed'
        z_wave = download_dir+'waveforms_20060127_Banda_Sea/'+net+'*'+sta+'*'+'HHZ'+'*.mseed'
        if sta != old_sta:      
            j = 0
            dist = gps2dist_azimuth(evlat,evlon,sta_lat,sta_lon)
            dis_deg = kilometer2degrees(dist[0]/1000)
            #plt.title(f'{sta}-{net} Distance: ${dis_deg}\degree$', fontsize=15, x=0.5,y=0.95)
            plt.close('all')
            arrivals = model.get_travel_times(source_depth_in_km=event_info_df.loc[0,'depth'],\
                                               # distance_in_degree=dis_deg)
                                            distance_in_degree=dis_deg, phase_list=["P","S","SKS"])
            #print(arrivals)
            p_arrival = 0
            s_arrival = 0
            for arr in range(len(arrivals)):
                if (arrivals[arr].name == "P") & (p_arrival == 0 ):
                    p_arrival = float(arrivals[arr].time)
                    continue
                if (arrivals[arr].name == "S") & (s_arrival == 0 ):
                    s_arrival = float(arrivals[arr].time)
                    continue
            p_s = s_arrival - p_arrival
        
            fig, ax = plt.subplots(5,1,figsize=(20,10)) 
            print("----> plotting trace")       
        j += 1
        old_sta=sta
        if j==3:
            stream=[]
            stream.append(read(e_wave))
            stream.append(read(n_wave))
            stream.append(read(z_wave))
            stream.append(read(r_wave))
            stream.append(read(t_wave))
            for kk in range(len(stream)):
                stream[kk][0].starttime = UTCDateTime(time)
                tr = stream[kk][0]
                tr.normalize()
                tr_filt = tr.filter('bandpass', freqmin=freqmin, freqmax=freqmax, corners=4, zerophase=True)
                tr_times = tr_filt.times()
                tr_data = tr_filt.data
                #ax[j].axvline(x = 50+p_s, color='red', label="S")
                ax[kk].plot(tr_times,tr_data,'k',lw=1)
                #ax[j].set_xlim([0,t2-t1])  
                ax[kk].set_xlim(800, 1800)  
                ax[kk].legend()
                if kk==0:
                    ax[kk].set_title('E    '+f'Dis.:${round(dis_deg,1)}\degree$   Azi.:${round(dist[1],1)}\degree$',fontsize=12, color='k')
                elif kk==1:
                    ax[kk].set_title('N    '+f'Dis.:${round(dis_deg,1)}\degree$   Azi.:${round(dist[1],1)}\degree$',fontsize=12, color='k')
                elif kk==2:
                    ax[kk].set_title('Z    '+f'Dis.:${round(dis_deg,1)}\degree$   Azi.:${round(dist[1],1)}\degree$',fontsize=12, color='k')
                elif kk==3:
                    ax[kk].set_title('R    '+f'Dis.:${round(dis_deg,1)}\degree$   Azi.:${round(dist[1],1)}\degree$',fontsize=12, color='k')
                elif kk==4:
                    ax[kk].set_title('T    '+f'Dis.:${round(dis_deg,1)}\degree$   Azi.:${round(dist[1],1)}\degree$',fontsize=12, color='k')
                for arr in range(len(arrivals)):
                    #ax[j].axvline(x = arrivals[arr].time, color = 'blue')
                    if arrivals[arr].time < 1800:
                        # ax[kk].plot(arrivals[arr].time,-0.4,'^', color='orange')
                        ax[kk].vlines(arrivals[arr].time,-0.5,0.5,color='orange',linestyles='solid')
                        ax[kk].text(arrivals[arr].time, -0.4+0.2*arr, f'{arrivals[arr].name}')
        
        plt.savefig(p_s_df+f'{net}_{sta}.png',bbox_inches='tight',dpi=300)
        print()