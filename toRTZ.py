import glob
import obspy
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from support_modules import create_dir
from obspy.geodetics.base import gps2dist_azimuth, kilometer2degrees
from obspy.clients.iris import Client
from obspy import read
from sklearn.preprocessing import MinMaxScaler
from obspy.core import UTCDateTime

client = Client()

def enztortz(j,event_name,waveform_type,dleft=0, download_dir="projects/",event_catalog="event_catalog.csv"):


    print('#############################################################')
    print('#####################  ENZ to RTZ  ##########################')
    print('#############################################################')


    event_info_df = pd.read_csv("event_catalog.csv")
    event_name = event_info_df.loc[j,'event_name']
    time = event_info_df.loc[j,'origin_time']
    evlat=event_info_df.loc[j,'latitude']
    evlon=event_info_df.loc[j,'longitude']

    station_info_df = pd.read_csv(download_dir+f"station_info_{event_name}.csv")

    new_waveforms_loc = download_dir+f"{waveform_type}_"+event_name #+ "_test"
    waveforms_vel = []

    mseed_RTZ_df = download_dir+event_name+"_mseed_RTZ/"
    if not os.path.exists(mseed_RTZ_df):
        create_dir(mseed_RTZ_df)

    

    for i,net in enumerate(station_info_df['Net']):
        net = net
        sta = station_info_df.loc[i,'Sta']
        filenames = glob.glob(new_waveforms_loc+f"/{waveform_type}_{net}.{sta}*BHZ*.mseed")
        if len(filenames):
            waveforms_vel.append(filenames[0])


    net_name = []
    station_name = []
    station_lon = []
    station_lat = []
    all_azm = []
    all_gcarc = []
    # Work on individual waveform
    for i,wavefm in enumerate(waveforms_vel):
        filename = wavefm.split("/")[-1]
        filename = wavefm.split("/")[-1]
        print(f"----> {i+1}/{len(waveforms_vel)} Working on {filename}")
        net = filename.split(".")[0].split("_")[-1]
        sta = filename.split(".")[1]
        new_sta_df = station_info_df[(station_info_df['Net']==net) & (station_info_df['Sta']==sta)]
        new_sta_df.reset_index(inplace=True,drop=True)

        if new_sta_df.shape[0]==3:
            stalon,stalat = new_sta_df.loc[0,'Sta_lon'],new_sta_df.loc[0,'Sta_lat']
            result = client.distaz(stalat=stalat, stalon=stalon, evtlat=evlat, evtlon=evlon)


            # Read waveform
            stream = read(wavefm)
            stream.starttime = UTCDateTime(time)
            if len(stream) != 0 :
                tr = stream[0]
                tr_times = tr.times() 
                tr_data = tr.data

            # Read in E Component
            e_filename = glob.glob(new_waveforms_loc+f"/{waveform_type}_{net}.{sta}*BH1*.mseed")
            if len(e_filename) == 1:
                print(f"--> Got E component.")
                stream1 = read(e_filename[0])
                if len(stream1) != 0:
                    tr1 = stream1[0]
                    tr1_times = tr1.times() 
                    tr1_data = tr1.data
                    stream.extend(stream1)
                else:
                    print('--> Empty trace.')     
           
            # Read in N Component
            n_filename = glob.glob(new_waveforms_loc+f"/{waveform_type}_{net}.{sta}*BH2*.mseed")
            if len(n_filename) == 1:
                print(f"--> Got N component.")
                stream2 = read(n_filename[0])
                if len(stream2) != 0:
                    tr2 = stream2[0]
                    tr2_times = tr2.times()
                    tr2_data = tr2.data
                    stream.extend(stream2)
                else:
                    print('--> Empty trace.')  
            print(f'--> {len(stream)} component(s) in the stream.')

            if len(stream) == 3:
                # Rotate
                print('--> Rotate to RTZ')
                try:
                    stream.rotate('NE->RT', result['backazimuth'])
                    # Plot Z Component
                    trZ = stream[0]
                    trZ.write(mseed_RTZ_df+f'{net}_{sta}_Z.mseed', format='MSEED')
                
                    # Plot T Component
                    trT = stream[1]
                    trT.write(mseed_RTZ_df+f'{net}_{sta}_T.mseed', format='MSEED')

                    # Plot R Component
                    trR = stream[2]
                    trR.write(mseed_RTZ_df+f'{net}_{sta}_R.mseed', format='MSEED')
                
                    # Write out stations with all RTZ components
                    azm= result['azimuth']
                    gcarc=result['distance']
                    net_name.append(net)
                    station_name.append(sta)
                    station_lat.append(stalat)
                    station_lon.append(stalon)
                    all_azm.append(azm)
                    all_gcarc.append(gcarc)
                    print(f'--> {net}.{sta} / azm:{azm} / gcarc:{gcarc} / stalat:{stalat} / stalon:{stalon}')
                except Exception as e:
                    print('--> ERROR | ', e)               


        print()
        print()

    print("--> Writing stations with 3 components into a text file")
    dff = pd.DataFrame({'Net':net_name,'Sta':station_name,'Sta_long':station_lon,'Sta_lat':station_lat,'azm':all_azm,'gcarc':all_gcarc})
    dff.to_csv(download_dir+f'rtz_info_{event_name}.csv', index=False)
   
               
