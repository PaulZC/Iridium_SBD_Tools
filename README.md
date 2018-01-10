# Iridium SBD Tools

A somewhat random collection of Python software tools to help Iridium SBD tracker projects like the [Iridium 9603N Beacon](https://github.com/PaulZC/Iridium_9603_Beacon).

![Mapper.jpg](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/img/Mapper.jpg)

## Background

This is a collection of Python software tools which I wrote to download, process, upload and visualise Short Burst Data messages from the [UBSEDS22I Iridium Tracker](https://github.com/PaulZC/Iridium_9603_Beacon/blob/master/Archive/V2/Iridium_9603_Beacon.pdf).

If you purchase an Iridium 9603N module for your tracker project, your provider will offer you the option of receiving the data messages via email or a web service (HTTP).
Personally I find email easier to work with. So, here are a somewhat random collection of software tools which will automatically download the SBD data email attachments from GMail, parse them,
display the tracker locations and paths using the Google Static Maps API, upload data to the [HabHub Habitat Tracker](https://tracker.habhub.org),
forward the data to another email address (with a Google Static Maps API link) and visualise the path of your tracker via Google Earth KML files.

## Downloading the SBD emails and attachments

The [Iridium 9603N Beacon](https://github.com/PaulZC/Iridium_9603_Beacon) transmits data messages containing its location, altitude, atmospheric pressure and temperature and other data.
The data is sent in Comma Separated Value (CSV) format:

- GNSS Time and Date (YYYYMMDDhhmmss) (string),
- GNSS Latitude (degrees) (float),
- GNSS Longitude (degrees) (float),
- GNSS Altitude (m) (int),
- GNSS Speed (m/s) (float),
- GNSS Heading (degrees) (int),
- GNSS HDOP (m) (float),
- GNSS satellites (int),
- Atmospheric Pressure (Pascals) (int),
- Temperature (C) (float),
- Battery (V) (float),
- Iteration Count (int)

E.g.:

_20170729144631,55.866573,-2.428458,103,0.1,0,3.0,5,99098,25.3,4.98,0_

It arrives as a .sbd file attached to an email from the Iridium system. The email itself contains other useful information:

- Message sequence numbers (so you can identify if any messages have been missed)
- The time and date the message session was processed by the Iridium system
- The status of the message session (was it successful or was the data corrupt)
- The size of the message in bytes
- The approximate latitude and longitude the message was sent from
- The approximate error radius of the transmitter’s location

E.g.:

   _From:	sbdservice@sbd.iridium.com_  
   _Sent:	20 August 2016 16:25_  
   _To:_  
   _Subject:	SBD Msg From Unit: 30043406174_  
   _Attachments:	30043406174-000029.sbd_  
  
   _MOMSN: 29_  
   _MTMSN: 0_  
   _Time of Session (UTC): Sat Aug 20 15:24:57 2016 Session Status: 00 - Transfer OK Message Size (bytes): 61_  
  
   _Unit Location: Lat = 55.87465 Long = -2.37135 CEPradius = 4_

So, it is beneficial to download both the email text and the .sbd attachment separately.

If you have your SBD messages sent to a GMail address, you can use IMAP4 to download the messages provided you alter your account settings
to allow IMAP access and [enable less secure apps](https://support.google.com/accounts/answer/6010255?hl=en)

[Iridium_SBD_GMail_IMAP_Downloader.py](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/Iridium_SBD_GMail_IMAP_Downloader.py)
will check your inbox once per minute for a new message from the Iridium system (with the subject: _SBD Msg From Unit_).
If it finds one it will download the email text, download the email attachment, mark the message as seen (read) and
'move' it to a folder called SBD by changing the message labels. You will need to manually create the SBD folder in GMail before running the code.

IMAP4 is an out-of-date way of accessing email. GMail's preferred method is to use the GMail API which is more secure. You can enable access with
Python by following the instructions [here](https://developers.google.com/gmail/api/quickstart/python).

[Iridium_SBD_GMail_API_Downloader.py](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/Iridium_SBD_GMail_API_Downloader.py) does the same job as the
IMAP downloader but using the API. As you will need _modify_ permission for your GMail mailbox, you will need to delete the default gmail-python-quickstart.json
file in the .credentials directory. Then when you run the code for the first time and sign in using your browser, your client_secret.json will get
copied across allowing modify access.

If you ever want to download all the SBD messages again, perhaps on a new computer, then
[Iridium_SBD_GMail_API_GetAllSBD.py](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/Iridium_SBD_GMail_API_GetAllSBD.py) will do just that.

## Mapping tracker locations and paths with the Google Static Maps API

[Iridium_9603N_Beacon_Mapper.py](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/Iridium_9603N_Beacon_Mapper.py) uses the Google Static Maps API to display beacon locations and paths.
It will check once per minute for the appearance of a new .sbd file, parse it and display the data in a Python Tkinter GUI.

You will need to download the [blank map image](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/map_image_blank.png) too. This is displayed until an sbd file is processed
or whenever the GUI isn't able to download map images from the API.

You can find more details about the API [here](https://developers.google.com/maps/documentation/static-maps/intro). To use the API, you will need to create
your own API Key, which you can do by following the instructions [here](https://developers.google.com/maps/documentation/static-maps/get-api-key). Copy the Key and save it in a file
called _Google_Static_Maps_API_Key.txt_ so the mapper can read it.

The intention is that you have Iridium_9603N_Beacon_Mapper.py and Iridium_SBD_GMail_API_Downloader.py running simultaneously.
Start Iridium_9603N_Beacon_Mapper.py first and allow it to build up a dictionary of any existing .sbd files, then start Iridium_SBD_GMail_API_Downloader.py.
When any new SBD messages arrive in your GMail inbox, they will be downloaded and then added to the map automatically.

If you want to test the mapper on its own, download the two example .sbd files
[18-01-01_01-00-00_123456789012345_000001.sbd](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/18-01-01_01-00-00_123456789012345_000001.sbd)
and
[18-01-01_01-00-01_123456789012345_000002.sbd](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/18-01-01_01-00-00_123456789012345_000001.sbd)
. When the code asks if you want to ignore any existing sbd files, answer 'n' and the data in these files will be displayed.

The displayed map is automatically centered on the position of a new beacon. The center position can be changed by left-clicking in the image.
A right-click will copy that location (lat,lon) to the clipboard. The zoom level defaults to '15' but can be changed using the zoom buttons.

A pull-down menu lists the latest locations of all beacons being tracked. Click on the entry for a beacon to center the map on its location and copy its location to the clipboard.

The beacon's path is displayed as a coloured line on the map. The oldest waypoints may not be shown as the map URL is limited to 8192 characters.

The GUI uses 640x480 pixel map images. Higher resolution images are available if you have a premium plan with Google.

![Mapper.jpg](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/img/Mapper.jpg)

The GUI has been tested with Python 2.7 on 64-bit Windows and on Linux on Raspberry Pi. You will need to install the Python libraries [listed below](https://github.com/PaulZC/Iridium_SBD_Tools#linux-python-27-libraries).

## Forwarding emails with Google Static Maps API links

[Iridium_SBD_GMail_API_Forwarder.py](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/Iridium_SBD_GMail_API_Forwarder.py) uses the GMail API to forward the contents of
an Iridium SBD message to another email address. It will check once per minute for the appearance of a new .sbd file, parse it, convert the contents
to a more user-friendly (html) format and then forward it as a new email message to the chosen recipient.

The beacon location in the .sbd message is converted into a link for the Google Static Maps API. This API is a great way to show a map image of where the beacon is located and the
path that it has followed. You can find more details about the API [here](https://developers.google.com/maps/documentation/static-maps/intro). To use the API, you will need to create
your own API Key, which you can do by following the instructions [here](https://developers.google.com/maps/documentation/static-maps/get-api-key). Copy the Key and save it in a file
called _Google_Static_Maps_API_Key.txt_ so the forwarder can read it.

The intention is that you have Iridium_SBD_GMail_API_Forwarder.py and Iridium_SBD_GMail_API_Downloader.py running simultaneously.
Start Iridium_SBD_GMail_API_Forwarder.py first and allow it to build up a dictionary of any existing .sbd files, then start Iridium_SBD_GMail_API_Downloader.py.
When any new SBD messages arrive in your GMail inbox, they will be downloaded and then forwarded automatically.

## Uploading data to the [HabHub Habitat Tracker Server](https://tracker.habhub.org)

If you want to use the excellent HabHub Habitat Tracker to track your flight, then first you need to talk to the [UKHAS team](https://ukhas.org.uk/) on [IRC](http://webchat.freenode.net/?channels=highaltitude) and register your flight.
Once you've done that, you can use [Iridium_9603N_Beacon_habhub_habitat_uploader.py](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/Iridium_9603N_Beacon_habhub_habitat_uploader.py)
to check for the download of new SBD files, parse the files and upload the data to Habitat. You will find the lines that actually upload the data to Habitat are commented out. Only uncomment them once you have registered
your flight and are ready to upload real data.

The intention is that you have Iridium_9603N_Beacon_habhub_habitat_uploader.py and Iridium_SBD_GMail_API_Downloader.py running simultaneously.
Start Iridium_9603N_Beacon_habhub_habitat_uploader.py first and allow it to build up a dictionary of any existing .sbd files, then start Iridium_SBD_GMail_API_Downloader.py.
When any new SBD messages arrive in your GMail inbox, they will be downloaded and then uploaded to habitat automatically.

## Stitching

So far, all of the SBD messages have been downloaded individually. If you want to combine these together into (e.g.) a single linestring for Google Earth, then you need to stitch the files together.

[Iridium_SBD_Header_Stitcher.py](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/Iridium_SBD_Header_Stitcher.py) goes through a directory and/or its subdirectories, looks for the text messages
downloaded from the Iridium system, parses them and builds up a csv ‘dictionary’ of the SBD message sequence numbers (MOMSN) together with their session times and the approximate lat & lon the message was sent from.
This is a good idea if you are sending SBD messages very quickly as it is possible for the messages to arrive by email in the same second.
Therefore you can’t reliably use the email arrival time to establish unique timings for each message. By using the Iridium session time, you can guarantee that the timings are unique. 

[Iridium_9603N_Beacon_Stitcher.py](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/Iridium_9603N_Beacon_Stitcher.py) goes through a directory and/or its subdirectories, looks for the .sbd message
attachments from the Iridium system (which contain the actual data transmitted by the beacon itself), appends them into a single csv file and adds the session time and message sequence numbers extracted by Header_Stitcher to the start of each entry.
That way you can be certain that each entry is unique (even if the emails arrived in the same second).

## Plotting

[Iridium_Stitch_Plotter_Pressure_and_Temperature.py](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/Iridium_Stitch_Plotter_Pressure_and_Temperature.py)
produces a very simple plot of the beacon pressure and temperature using Matplotlib.

## Converting to KML

[Iridium_9603N_Beacon_to_KML.py](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/Iridium_9603N_Beacon_to_KML.py) will convert the stitched SBD data into Google Earth linestring, points and arrows files, allowing you
to visualise your flight around the globe without using the HabHub Tracker.
You can alter the code to either produce a linestring which is clamped to the ground, or one which shows a 3D representation of the flight altitude. Points overlaid on top of a clamped linestring looks nice. Arrows overlaid on clamped linestring makes it obvious which way your tracker was heading.

![UBSEDS22I_GoogleEarthLinestring_3a.jpg](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/img/UBSEDS22I_GoogleEarthLinestring_3a.jpg)

## Linux Python 2.7 Libraries

To get the tools to run successfully under Linux, e.g. on Raspberry Pi, you will need to install the following:

### GMail API

- pip install --upgrade google-api-python-client

### PIL ImageTk

- sudo apt-get install python-pil.imagetk

### Matplotlib

- sudo apt-get install python-matplotlib

### CouchDB

- pip install couchdb

### CRCMOD

- pip install crcmod

### SimpleKML

- pip install simplekml

## Licence

This project is distributed under a [GNU GENERAL PUBLIC LICENSE](https://github.com/PaulZC/Iridium_SBD_Tools/blob/master/LICENSE.md)

Enjoy!

**_Paul_**











