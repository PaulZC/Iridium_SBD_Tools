# Iridium 9603N Beacon HabHub Habitat Uploader

# Builds a dictionary of all existing sbd files
# Once per minute, checks for the appearance of a new sbd file
# When one is found, parses the file and uploads the data to the habhub habitat

# sbd file contains:
# Column 0 = GPS Tx Time (YYYYMMDDHHMMSS) (Start of 9603 Tx session)
# Column 1 = GPS Latitude (degrees) (float)
# Column 2 = GPS Longitude (degrees) (float)
# Column 3 = GPS Altitude (m) (int)
# Column 4 = GPS Speed (m/s) (float)
# Column 5 = GPS Heading (Degrees) (int)
# Column 6 = GPS HDOP (m) (float)
# Column 7 = GPS satellites (int)
# Coulmn 8 = Pressure (Pascals) (int)
# Column 9 = Temperature (C) (float)
# Column 10 = Battery (V) (float)
# Column 11 = Iteration Count (int)

# Converters
# 0:mdates.strpdate2num('%Y%m%d%H%M%S')

import os
import numpy as np
import time
import matplotlib.dates as mdates
import crcmod
import base64
import hashlib
import couchdb
from datetime import datetime

if __name__ == '__main__':
    try:

        print 'Iridium 9603 Beacon to habhub habitat uploader'

        couch = couchdb.Server('http://habitat.habhub.org/')
        db = couch['habitat']
        callsign = "UBSEDS22I"

        # Build a dictionary of all existing sbd files
        sbd = {}
        for root, dirs, files in os.walk("."):
            if len(files) > 0:
                #if root != ".": # Ignore files in this directory - only process subdirectories
                #if root == ".": # Ignore subdirectories - only process this directory
                    for filename in files:
                        if filename[-4:] == '.sbd': # check for sbd file suffix
                            longfilename = os.path.join(root, filename)
                            msnum = int(longfilename[-10:-4]) # extract the message sequence number
                            sbd[msnum] = longfilename # add the msn and filename to the dictionary
        print 'Found',len(sbd),'existing sbd files'
        print 'Checking once per minute for new ones...'

        # Once per minute, check for the appearance of a new sbd file
        while (True):
            for l in range(60): # Sleep for 60x1 seconds (to allow KeyboardInterrupt to be detected quickly)
                time.sleep(1)

            # Identify all the sbd files again 
            for root, dirs, files in os.walk("."):
                if len(files) > 0:
                    #if root != ".": # Ignore files in this directory - only process subdirectories
                    #if root == ".": # Ignore subdirectories - only process this directory
                        for filename in files:
                            if filename[-4:] == '.sbd':
                                longfilename = os.path.join(root, filename)
                                msnum = int(longfilename[-10:-4])

                                # Check if message sequence number is in the dictionary
                                # If it isn't then this must be a new sbd file so process it
                                if sbd.has_key(msnum) == False:
                                    print 'Found new sbd file with MOMSN',msnum
                                    sbd[msnum] = longfilename # Add new msn and filename to dictionary

                                    # Read the sbd file and unpack the data using numpy loadtxt
                                    gpstime,latitude,longitude,altitude,speed,heading,pressure,temperature,battery = \
                                        np.loadtxt(longfilename, delimiter=',', unpack=True, \
                                        usecols=(0,1,2,3,4,5,8,9,10), converters={0:mdates.strpdate2num('%Y%m%d%H%M%S')})

                                    pressure = int(round(pressure)) # Convert pressure to integer
                                    time_str = mdates.num2date(gpstime).strftime('%H:%M:%S,%y%m%d') # Time string (HH:MM:SS,YYMMDD)
                                    location_str = "{:.6f},{:.6f},{}".format(latitude, longitude, int(round(altitude))) # Location

                                    # Assemble the UKHAS format string
                                    ukhas_str = "{},{},{},{:.2f},{:.1f},{},{},{},{}".format( \
                                        callsign, time_str, location_str, speed, heading, pressure, temperature, battery, msnum);

                                    # Checksum test - comment out after testing - should produce checksum A36A
                                    # ukhas_str = "UBSEDS18,18:34:12,160816,51.4668,-2.5802,65,7,1.85,32.8,41.4,0,0"

                                    # Calculate checksum
                                    crc16 = crcmod.mkCrcFun(0x11021, 0xFFFF, False, 0x0000)
                                    checksum =  "{:04X}".format(crc16(ukhas_str))

                                    # Append the checksum
                                    ukhas_str = "$${}*{}".format(ukhas_str, checksum)
                                    print 'Uploading:',ukhas_str

                                    # Packet ID
                                    packet_base64 = base64.standard_b64encode(ukhas_str+"\n")
                                    packet_sha256 = hashlib.sha256(packet_base64).hexdigest()

                                    # Time Created = backlog time
                                    time_created = mdates.num2date(gpstime).strftime('%Y-%m-%dT%H:%M:%S+00:00')

                                    # Time Uploaded = now
                                    now = datetime.utcnow()
                                    time_uploaded = now.replace(microsecond=0).isoformat()+"+00:00"

## >>>>> Comment from here
##                                    # Upload to the habhub habitat database
##                                    doc_id, doc_rev = db.save({
##                                        "type":"payload_telemetry",
##                                        "_id": packet_sha256,
##                                        "data":{
##                                            "_raw": packet_base64
##                                        },
##                                        "receivers": {
##                                            "BACKLOG": {
##                                                "time_created": time_created,
##                                                "time_uploaded": time_uploaded,
##                                            }
##                                        }
##                                    })
##                                    print 'Doc ID:',doc_id
##                                    print 'Doc Rev:',doc_rev
## >>>>> to here to disable habitat upload

    except KeyboardInterrupt:
        print 'CTRL+C received...'

    finally:
        print 'Bye!'
     
    
