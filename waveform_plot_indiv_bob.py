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

def WaveformPlotIndiv(i,event_name,waveform_type,dleft=0, download_dir="projects/",event_catalog="event_catalog.csv",model_name="iasp91", freqmin=2, freqmax=4):

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
    new_waveforms_loc = download_dir+f"{waveform_type}_"+event_name 
    # storage directory
    p_s_df = download_dir+event_name+f"_{waveform_type}_{freqmin}-{freqmax}/"
    if os.path.exists(p_s_df):
        print(f'{p_s_df} exists!')
    else:
        create_dir(p_s_df)

    # station info read in
    old_sta='bob'
    station_info_df = pd.read_csv(download_dir+f"station_info_{event_name}.csv")
    for i,net in enumerate(station_info_df['Net']):
        sta = station_info_df.loc[i,'Sta']
        loc = station_info_df.loc[i,'Loc']
        cha = station_info_df.loc[i,'Cha']
        sta_lon = station_info_df.loc[i,'Sta_lon']
        sta_lat = station_info_df.loc[i,'Sta_lat']
        #print(loc, sta_lat, cha)
        if math.isnan(loc):
            wavefm = f"{new_waveforms_loc}/{waveform_type}_{net}.{sta}..{cha}.mseed"
        else:
            wavefm = f"{new_waveforms_loc}/{waveform_type}_{net}.{sta}.{int(loc):02}.{cha}.mseed"
        #wavefm = f"{new_waveforms_loc}/{waveform_type}_{net}.{sta}.{loc:02}.{cha}.mseed"
        print(wavefm)

        if sta != old_sta:
            
            j = 0
            dist = gps2dist_azimuth(evlat,evlon,sta_lat,sta_lon)
            dis_deg = kilometer2degrees(dist[0]/1000)
            #plt.title(f'{sta}-{net} Distance: ${dis_deg}\degree$', fontsize=15, x=0.5,y=0.95)
            plt.close('all')
            phase_list=['p', 's', 'P', 'S', 'Pn', 'Sn', 'PKP', 'SKS','SKKS', 'PKiKP', 'SKiKS', 'PKIKP', 'SKIKS']
            arrivals = model.get_travel_times(source_depth_in_km=event_info_df.loc[0,'depth'],\
                                              distance_in_degree=dis_deg,phase_list=phase_list)
            #                                 distance_in_degree=dis_deg, phase_list=["P","S"])
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
        
            fig, ax = plt.subplots(3,1,figsize=(10,10)) 

            print("----> plotting trace")

        # Read waveform
        stream = read(wavefm)
        stream.starttime = UTCDateTime(time)
        t1 = stream.starttime + p_arrival - 50
        t2 = stream.starttime + s_arrival + 50
        #stream.trim(t1, t2)
        tr = stream[0]
        tr.normalize()
        tr_filt = tr.filter('bandpass', freqmin=freqmin, freqmax=freqmax, corners=2, zerophase=True)
        tr_times = tr_filt.times()
        tr_data = tr_filt.data
        # plot
        for arr in range(len(arrivals)):
            #ax[j].axvline(x = arrivals[arr].time, color = 'blue')
            if arrivals[arr].time < 1800 and arrivals[arr].time > 800 and arrivals[arr].name != "SKS" and arrivals[arr].name != "SKKS":
                ax[j].plot(arrivals[arr].time,0,'^', color='b')
                ax[j].text(arrivals[arr].time,0.2*arr-0.8*(arr//5), f'{arrivals[arr].name}')
            if (arrivals[arr].name == "SKS") or (arrivals[arr].name == "SKKS"):
                ax[j].vlines(arrivals[arr].time,-0.5,0.5,color='orange',linestyles='solid')
                ax[j].text(arrivals[arr].time,0.2*arr-0.8*(arr//5), f'{arrivals[arr].name}')
        #ax[j].axvline(x = 50+p_s, color='red', label="S")
        ax[j].plot(tr_times,tr_data,'k',lw=1)
        #ax[j].set_xlim([0,t2-t1])  
        ax[j].set_xlim(800, 1800)  
        ax[j].legend()            
        ax[j].set_title('sta='+sta+'  '+f'{cha}    Dis.:${round(dis_deg,1)}\degree$    \
                        Azi.:${round(dist[1],1)}\degree$',\
                        fontsize=12, color='k')
        plt.savefig(p_s_df+f'{net}_{sta}.png',bbox_inches='tight',dpi=300)            
        j += 1
        old_sta = sta


        print()
        print()

