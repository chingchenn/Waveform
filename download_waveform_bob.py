import obspy, os
from glob import glob
#from support_modules import plot_map, create_dir, rem_dir
from support_modules import create_dir, rem_dir
import pandas as pd
from obspy import read_inventory, read
from obspy.clients.fdsn.mass_downloader import CircularDomain, Restrictions, MassDownloader, RectangularDomain

def download_waveform(event_name,time,cevent,dleft,dright,waveform_type,minlat,minlon,maxlat,maxlon,download_data=1,remove_ins = 1, download_dir="projects/"):
    
    waveform_storage_loc = download_dir+"waveforms_"+event_name
    stationxml_loc = download_dir+"stations_"+event_name
    new_waveforms_loc = download_dir+f"{waveform_type}_"+event_name
    print(new_waveforms_loc)

    if download_data:
        if os.path.exists(waveform_storage_loc):
            # rem_dir(waveform_storage_loc)
            print(f'--> The download directory {waveform_storage_loc} exists!')

        if os.path.exists(stationxml_loc):
            print(f'--> The download station info {stationxml_loc} exists!')
            # rem_dir(stationxml_loc)

        # downloading waveform data
        origin_time = obspy.UTCDateTime(time)
        domain = RectangularDomain(minlatitude=minlat, maxlatitude=maxlat,
                                  minlongitude=minlon, maxlongitude=maxlon)
        # domain = CircularDomain(latitude=cevent[0], longitude=cevent[1], minradius=100.0, maxradius=140.0) #epicenter and search radius

        restrictions = Restrictions(
            starttime=origin_time - 3*60,
            endtime=origin_time + dright,
            reject_channels_with_gaps=False, #any trace with a gap/overlap will be discarded
            minimum_length=0.7, #traces less than 70% are discarded
            minimum_interstation_distance_in_m=10, #No two stations should be closer than 0.01 km to each other
            network="TO,MX,AK,AT,AV,CN,II,IU,NY,TA",
            channel_priorities=["HH[ZNE]", "BH[ZNE]"],#broadband vertical component seismogram 
            #sanitize=False,
            # location_priorities=["00"],
            location_priorities=["", "00", "10", "01", "02", "03", "20"]
        ) 
        
        #attempt to download data from all FDSN data centers that ObsPy knows of and combine it into one data set.
        mdl = MassDownloader()
        print(f"--> Downloading data for {event_name}")
        mdl.download(domain, restrictions, mseed_storage=waveform_storage_loc, stationxml_storage=stationxml_loc)
        all_downloads = glob(waveform_storage_loc+"/*")
        print(f"--> Total downloads: {len(all_downloads)}")
        
        # Plot map  (Use with cautious - several parameters need to be changed)
        #print(f"--> Plotting downloaded station map.")
        #all_stationxmls = glob(f"{stationxml_loc}/*.xml")
        #c0stations = []
        #net0_name = []
        #station0_name = []
        #station0_lat = []
        #station0_lon = []
        #for xml in all_stationxmls:
        #    inv = read_inventory(xml, format="STATIONXML")
        #    net = inv[0]
        #    sta = net[0]
        #    stalat,stalong,netc,stac = sta.latitude, sta.longitude, net.code, sta.code
        #    c0stations.append((stalat, stalong))
        #    net0_name.append(netc)
        #    station0_name.append(stac)
        #    station0_lat.append(stalat)
        #    station0_lon.append(stalong)
        #plot_map(coord_event=cevent, coord_stations=c0stations,coord0_stations=c0stations, figname=download_dir+f'downloaded_{event_name}.png')
        #print("--> Writing the downloaded stations coordinates in a text file")
        #dff = pd.DataFrame({'Net':net0_name,'Sta':station0_name,'Sta_long':station0_lon,'Sta_lat':station0_lat})
        #dff.to_csv(download_dir+f'downloaded_station_info_{event_name}.csv', index=False)

    ## Visualizing downloaded data and removing instrument response
    if remove_ins:
        if os.path.exists(new_waveforms_loc):
            print(f'{new_waveforms_loc} exists!')
        else:
            create_dir(new_waveforms_loc)

        all_stationxmls = glob(f"{stationxml_loc}/*.xml")
        net_name = []
        station_name = []
        station_lat = []
        station_lon = []
        station_loc = []
        station_cha = []
        station_azi = []
        station_dip = []

        #pre_filt = (0.005, 0.006, 30.0, 35.0) # define a filter band to prevent amplifying noise during the deconvolution
        dleft_utc = obspy.UTCDateTime(time)
        for xml in all_stationxmls:
            inv = read_inventory(xml, format="STATIONXML")
            net = inv[0]
            sta = net[0]
            print(f"--> {net.code}-{sta.code} :")
            #waveform_file_string_ori = f"{waveform_storage_loc}/{net.code}.{sta.code}*.mseed"
            pre_filt = [0.001, 0.005, 45, 50]
            for i in range(len(sta)):
                loc = sta[i].location_code
                cha = sta[i].code
                azi = sta[i].azimuth
                dip = sta[i].dip
                # wave_data = glob(f"{waveform_storage_loc}/{net.code}.{sta.code}.{loc}.{cha}*.mseed")
                wave_data = glob(f"{waveform_storage_loc}/{net.code}.{sta.code}.{loc}.{cha}*.sac")
                print(wave_data)
                if wave_data:
                    st = read(wave_data[0])
                    st_wir = st.remove_response(inventory=inv, pre_filt=pre_filt,\
                                                water_level=60, output='DISP')
                    # new_stream = f"{new_waveforms_loc}/{waveform_type}_{net.code}.{sta.code}.{loc}.{cha}.mseed"
                    new_stream = f"{new_waveforms_loc}/{waveform_type}_{net.code}.{sta.code}.{loc}.{cha}.sac"
                    print(new_stream)
                    if os.path.exists(new_stream):
                        os.remove(new_stream)
                    # st_wir.write(new_stream, format="MSEED")
                    st_wir.write(new_stream, format="SAC")
                    net_name.append(net.code)
                    station_name.append(sta.code)
                    station_lat.append(sta.latitude)
                    station_lon.append(sta.longitude)
                    station_loc.append(loc)
                    station_cha.append(cha)
                    station_azi.append(azi)
                    station_dip.append(dip)

        print("--> Writing the selected stations coordinates in a text file")
        dff = pd.DataFrame({'Net':net_name,'Sta':station_name,'Loc':station_loc,\
                            'Cha':station_cha,'Sta_lon':station_lon,\
                            'Sta_lat':station_lat,'Cha_azi':station_azi,\
                            'Cha_dip':station_dip})
        dff.to_csv(download_dir+f'station_info_{event_name}.csv', index=False)
        
if __name__=="__main__":
    event_info_df = pd.read_csv("event_catalog.csv")
    event_name=event_info_df.loc[0,'event_name'] # event name (arbitrary)
    time = event_info_df.loc[0,'origin_time'] #UTC origin time
    cevent = [event_info_df.loc[0,'latitude'], event_info_df.loc[0,'longitude']]  # latitude and longitude of epicenter

    dleft, dright = 0, 35*60 #waveform cut length - left and right relative to origin time
    waveform_type = 'VEL'

    download_data = 1 #1 to download the data
    plot_station_event_map = 1 #1 to remove intrument response and plot the event-station map

    download_waveform(event_name,time,cevent,dleft,dright,waveform_type,download_data=1,plot_station_event_map = 1)
    # download_waveform(event_name,time,cevent,dleft,dright,waveform_type,download_data=1)