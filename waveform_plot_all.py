import glob
import pandas as pd
import matplotlib.pyplot as plt
from obspy.geodetics.base import gps2dist_azimuth, kilometer2degrees
from obspy.taup import TauPyModel
from obspy.clients.iris import Client
from obspy import read
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import obspy
from obspy.core import UTCDateTime
import math
client = Client()

def WaveformPlotAll(j,CHANN,event_name,waveform_type,dleft=0, download_dir="projects/",event_catalog="event_catalog.csv",model_name="iasp91", freqmin=0.01, freqmax=1):
    print('#############################################################')
    print('#####################  Phase Plot  ##########################')
    print('#############################################################')
    event_info_df = pd.read_csv("event_catalog.csv")
    event_name = event_info_df.loc[j,'event_name']
    time = event_info_df.loc[j,'origin_time']
    
    
    direc_df = pd.read_csv(download_dir+f"station_info_{event_name}.csv")
    new_waveforms_loc = download_dir+f"{waveform_type}_"+event_name
    station_info_df = pd.read_csv(download_dir+f"station_info_{event_name}.csv")
    event_info_df = pd.read_csv("event_catalog.csv")
    evlat=event_info_df.loc[j,'latitude']
    evlon=event_info_df.loc[j,'longitude']
    model = TauPyModel(model=model_name)
        # Read in waveforms and save in waveforms_vel 
    waveforms_vel = []
    fig, ax = plt.subplots(1,1,figsize=(18,25))
    
    max_of_all = 0 
    for i,net in enumerate(direc_df['Net']):
        net = net
        sta = direc_df.loc[i,'Sta']
        loc = direc_df.loc[i,'Loc']
        cha = direc_df.loc[i,'Cha']
        sta_lon = direc_df.loc[i,'Sta_lon']
        sta_lat = direc_df.loc[i,'Sta_lat']
            #print(loc, sta_lat)
    
        if cha==CHANN:
            if math.isnan(loc):
                wavefm = f"{new_waveforms_loc}/{waveform_type}_{net}.{sta}..{cha}.mseed"
            else:
                wavefm = f"{new_waveforms_loc}/{waveform_type}_{net}.{sta}.{int(loc):02}.{cha}.mseed"
            outfile = f'{event_name}_{cha}_cross_section.png'
            #wavefm = f"{new_waveforms_loc}/{waveform_type}_{net}.{sta}.{int(loc):02}.{cha}.mseed"
            dist = gps2dist_azimuth(evlat,evlon,sta_lat,sta_lon)
            print('---> Great circle distance in km:', dist[0]/1000)
            print('---> Great circle distance in degree:', kilometer2degrees(dist[0]/1000))
            dis_deg = kilometer2degrees(dist[0]/30)
            print('azi', dist[1])
        
            # IASP91 P arrival time
            arrivals = model.get_travel_times(source_depth_in_km=event_info_df.loc[j,'depth'],distance_in_degree=dis_deg)
            #print(arrivals)
            print(wavefm)
        
            p_arrival = 0
            s_arrival = 0
            for arr in range(len(arrivals)):
                if (arrivals[arr].name == "P") & (p_arrival == 0 ):
                    p_arrival = float(arrivals[arr].time)
                    continue
                if (arrivals[arr].name == "S") & (s_arrival == 0 ):
                    s_arrival = float(arrivals[arr].time)
                    continue
            if ( s_arrival > max_of_all ):
                max_of_all = s_arrival
                max_p = p_arrival
    
    
            # Read waveform
            stream = read(wavefm)
            stream.starttime = UTCDateTime(time)
            tr = stream[0]
            tr.normalize()
            # Bandpass filtered
            #tr_filt = tr.filter('bandpass', freqmin=2, freqmax=4, corners=2, zerophase=True)
            tr_times = tr.times() #- dleft - p_arrival
            tr_data = tr.data
    
            #plot 
            print("----> plotting trace")
            ax.plot(tr_times,tr_data+dis_deg,'k',lw=1)
            ax.text(700+50*(-1)**i, dis_deg, f'{sta}', fontsize=12)
            #ax.text(np.float(result['distance'])*10,np.float(result['distance']), f"{net}-{sta}")
            for arr in range(len(arrivals)):
                # ax.plot(arrivals[arr].time,dis_deg,marker='^', color='b')
                if (arrivals[arr].name == "SKS") or (arrivals[arr].name == "SKKS"):
                    # ax.plot(arrivals[arr].time,dis_deg,'^',ms=20, color='orange')
                    ax.vlines(arrivals[arr].time,dis_deg-0.5,dis_deg+0.5,color='orange',linestyles='solid')
            if p_arrival != 0: 
                # ax.plot(p_arrival,dis_deg,'^', color='b')
                ax.vlines(p_arrival,dis_deg-0.3,dis_deg+0.3,color='b',linestyles='solid')
            if s_arrival != 0: 
                # ax.plot(s_arrival,dis_deg,'^', color='red')
                ax.vlines(s_arrival,dis_deg-0.3,dis_deg+0.3,color='red',linestyles='solid')
        print()
        print()
    
    ax.plot(p_arrival,dis_deg,'^', color='b', label="P")
    ax.plot(s_arrival,dis_deg,'^', color='red', label="S")       
    
    plt.xlim([600, 1750])    
    # plt.xlim([600, 1800])    
    plt.xlabel('Time from Start Time') #P-arrival (in seconds)')
    plt.ylabel('Distance (in degrees)')
    plt.title(f'{event_name}')
    plt.legend()
    plt.savefig(download_dir+f'{outfile}',bbox_inches='tight',\
                dpi=300,facecolor='w')
    # plt.close('all')
