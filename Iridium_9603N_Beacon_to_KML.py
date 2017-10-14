# Converts stitched Iridium Beacon csv file into kml for GoogleEarth

# With thanks to Kyle Lancaster for simplekml:
# http://simplekml.readthedocs.io/en/latest/index.html
# https://pypi.python.org/pypi/simplekml

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
import simplekml
import matplotlib.dates as mdates

times,msns,lats,lons,alts,heads,pressures = np.loadtxt('SBD_stitched.csv', delimiter=',', unpack=True, \
    usecols=(1,2,4,5,6,8,11), converters={1:mdates.strpdate2num('%a %b %d %Y %H:%M:%S')})

# Convert pressures into heights
# Add height offset to compensate for local atmospheric pressure
# or to stop route going underground
height_offset = 0. 
heights = (44330.77 * (1 - ((pressures / 101326.)**0.1902632))) + height_offset

# Convert each message to a point

kml1 = simplekml.Kml()
style = simplekml.Style()
style.labelstyle.color = simplekml.Color.red  # Make the text red
#style.labelstyle.scale = 2  # Make the text twice as big
style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/placemark_circle.png'
for point in range(len(lats)):
    pnt = kml1.newpoint(name=str(int(msns[point])))
    pnt.coords=[(lons[point],lats[point],heights[point])]
    pnt.style = style
kml1.save("Iridium_9603N_Beacon_points.kml")

# Convert all messages to a LineString

kml2 = simplekml.Kml()
ls = kml2.newlinestring()
coords = []
ls.altitudemode = simplekml.AltitudeMode.absolute # Comment this line to show route clamped to ground
for point in range(len(lats)):
    coords.append((lons[point],lats[point],heights[point]))
ls.coords = coords
ls.extrude = 1
ls.tessellate = 1
ls.style.linestyle.width = 5
ls.style.linestyle.color = simplekml.Color.yellow
ls.style.polystyle.color = simplekml.Color.yellow
kml2.save("Iridium_9603N_Beacon_linestring.kml")

# Display headings as arrows

kml3 = simplekml.Kml()
heading_styles = []
for heading in range(361): # Create iconstyles for each heading 0:360
    heading_styles.append(simplekml.Style())
    heading_styles[-1].iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/shapes/arrow.png'
    heading_styles[-1].iconstyle.heading = (heading + 180.) % 360. # Fix arrow orientation
for point in range(len(lats)): # Create points, link style to nearest heading
    pnt = kml3.newpoint(name=str(int(msns[point])))
    pnt.coords=[(lons[point],lats[point],heights[point])]
    pnt.style = heading_styles[int(round(heads[point]))]
kml3.save("Iridium_9603N_Beacon_arrows.kml")

           
    
