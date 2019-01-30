# Importing packages
from netCDF4 import Dataset
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from pickle import dump
from sys import argv
#%matplotlib inline

# import a soil moisture product to retrieve the 5km grid
# import FMC 

year_ref = int(argv[1])
path_ss = '/g/data/oe9/project/to_hot_in_here/soil_moisture/ss_pct_2017_Actual_day.nc'
ss = Dataset(path_ss, 'r')

#read longitude latitude to obtain the grid
lat_grid = ss['latitude'][:]
lon_grid = ss['longitude'][:]

# retrieve FMC data by year
for year in range(year_ref,year_ref+1):
    url_fmc = 'http://dapds00.nci.org.au/thredds/dodsC/ub8/au/FMC/c6/mosaics/fmc_c6_'+ str('%i' % year) + '.nc'
    fmc = Dataset(url_fmc, 'r')
    lat_fmc = fmc['latitude'][:]
    lon_fmc = fmc['longitude'][:]
    
    #identify FMC pixels within each SM cell
    a = [np.where((lat_fmc < lat_grid[i]+0.0251) & (lat_fmc > lat_grid[i]-0.0251))[0] for i in range(lat_grid.size)]
    b = [np.where((lon_fmc < lon_grid[i]+0.0251) & (lon_fmc > lon_grid[i]-0.0251))[0] for i in range(lon_grid.size)]

    #change FMC time to days since epoch
    time = fmc['time'][:]
    
     # create matrix to store median data
    m = np.zeros((time.size, lat_grid.size, lon_grid.size))*np.nan
    
    #input time
    for i in range(time.size):
        x = datetime(1970,1,1) + timedelta(seconds = int(time[i]))
        x = x-datetime(1900,1,1)
        time[i] = x.days
        
        tref = datetime.now()
        print('\nday', i, ':', tref)
        dfmc = fmc['fmc_mean'][i,:,:]
        #print('A', year, i, np.nanmin(dfmc), np.nanmax(dfmc))
        tc = datetime.now() - tref
        print('download in', tc, ';   dfmc.shape =', dfmc.shape)
    
        # input lat and lon values
        for l in range(lat_grid.size):
            for c in range(lon_grid.size):
                #print(l, c, a[l], b[c])
                try:
                    aux = dfmc[a[l][0]:a[l][-1], b[c][0]:b[c][-1]]
                    #aux = aux.flatten()
                    #compute median
                    #m[i, l, c] = np.nanmedian(aux)
                    m[i, l, c] = np.ma.median(aux[np.isfinite(aux)])
                except:
                    pass
        tc = datetime.now() - tref
        print('median computed in', tc, ';   i=', i)
        #print('B', year, i, np.nanmin(m[i]), np.nanmax(m[i]))

        fname = str('fmc_upscale/upscalemedian_%4.4i.pkl' % year_ref)
        with open(fname, 'wb') as f:
            dump((i, time, lat_grid, lon_grid, m), f)
    
        #break
        
