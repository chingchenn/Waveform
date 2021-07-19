# Waveform

need a csv catalog file named event_catalog.csv  
event_catalog.csv should contain event_name, origin_time (UTC Time), latitude, longitude, depth  

example:  
![image](https://user-images.githubusercontent.com/87369245/126101550-694026e6-c766-491e-b4a2-92a2b1047dce.png)  

-------------------------------------------------------------------------------------------------
run main_code.py to download waveform and plot waveform  
in main_code.py:  
     ######### Obervation Setup ##########  
dleft, dright = 0, 120*60                waveform cut length (left and right relative to origin time)  
waveform_type = 'DISP'  : can choose VEL or DISP   
model_name = "iasp91" : model detail:https://docs.obspy.org/packages/obspy.taup.html  
freqmin = 0.01   
freqmax = 10  
minlat = 15  #station where you want, here is the Mexico location  
maxlat = 25  
minlon = -105  
maxlon = -95  
    
   ######### DO WHAT ########## 
data = 0                                # Download data and remove instrument response                                          
waveform_plot_individual = 0            # Plot individual waveforms   
waveform_plot_all_in_distance = 0       # Plot the waveform of all stations (arrange in distance)  
ENZtoRTZ = 0  
