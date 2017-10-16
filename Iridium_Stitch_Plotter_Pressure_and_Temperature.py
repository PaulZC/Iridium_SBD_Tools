# Plots stitched Iridium data

# Column 0 = Email Rx Time (YY-MM-DD HH-MM-SS)
# Column 1 = Iridium Session DateTime (aaa bbb dd YYYY HH:MM:SS)
# Column 2 = MOMSN
# Column 3 = GPS Tx Time (YYYYMMDDHHMMSS) (Start of 9603 Tx session)
# Column 4 = GPS Latitude (degrees) (float)
# Column 5 = GPS Longitude (degrees) (float)
# Column 6 = GPS Altitude (m) (int)
# Column 7 = GPS Speed (m/s) (float)
# Column 8 = GPS Heading (Degrees) (int)
# Column 9 = GPS HDOP (m) (float)
# Column 10 = GPS satellites (int)
# Coulmn 11 = Pressure (Pascals) (int)
# Column 12 = Temperature (C) (float)
# Column 13 = Battery (V) (float)
# Column 14 = Iteration Count (int)

# Converters
# 0:mdates.strpdate2num('%y-%m-%d %H-%M-%S')
# 1:mdates.strpdate2num('%a %b %d %Y %H:%M:%S')
# 3:mdates.strpdate2num('%Y%m%d%H%M%S')

import numpy as np
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

times,pressures,temperatures = np.loadtxt('SBD_stitched.csv', \
    delimiter=',', unpack=True, usecols=(1,11,12), \
    converters={1:mdates.strpdate2num('%a %b %d %Y %H:%M:%S')})

f, (ax1, ax2) = plt.subplots(2, sharex=True)
ax1.plot(times, temperatures)
ax2.plot(times, pressures)
f.subplots_adjust(hspace=0)
plt.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)

ax2.xaxis.set_major_formatter(mdates.DateFormatter('%y/%m/%d %H:%M:%S'))
plt.xlabel('Time')

ax1.set_title('Iridium Data')

ax1.grid(True)
ax2.grid(True)

plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
    
