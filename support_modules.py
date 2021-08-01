# import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import os, shutil
#from plotting_libs import plot_merc


def create_dir(direc):
    '''
    Create a directory
    '''
    try:
        os.makedirs(direc, exist_ok=True)
    except OSError:
        print("--> Creation of the directory {} failed".format(direc))
    else:
        print("--> Successfully created the directory {}".format(direc))

def rem_dir(direc):
    '''
    Delete a directory
    '''
    if os.path.exists(direc):
        shutil.rmtree(direc)




def plot_map(coord_event, coord_stations, figname='test_event.png'):
    map = plot_merc(resolution='f', lat_0 = coord_event[0], lon_0 = coord_event[1])
    for stalat,stalon,staname in coord_stations:
        x,y = map(stalon, stalat)
        map.plot(x, y,'^', color='b', markersize=4,markeredgecolor='k',markeredgewidth=0.1,linewidth=0.1)#,label=staname)
        plt.text(x,y+0.1,staname,fontsize=5)
    xe,ye = map(coord_event[1], coord_event[0])
    map.plot(xe, ye,'*', color='r', markersize=10,markeredgecolor='k',markeredgewidth=0.1,linewidth=0.1, label='0318 Utah Mainshock')
    map.plot(-115.14,44.45,'*',color='g', markersize=10,markeredgecolor='k',markeredgewidth=0.1,linewidth=0.1, label='0331 Idaho Mainshock')
    plt.legend(fontsize=6,loc='lower left')
    plt.savefig(figname, dpi=1000, bbox_inches='tight')
    plt.close('all')



