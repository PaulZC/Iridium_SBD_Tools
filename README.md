# Iridium SBD Tools

A somewhat random collection of Python software tools to help Iridium SBD tracker projects like the [Iridium 9603N Beacon](https://github.com/PaulZC/Iridium_9603_Beacon).

## Background

This is a collection of Python software tools which I wrote to download, process, upload and visualise Short Burst Data messages from the [UBSEDS22I Iridium Tracker](https://github.com/PaulZC/Iridium_9603_Beacon/blob/master/Archive/V2/Iridium_9603_Beacon.pdf).

If you purchase an Iridium 9603N module for your tracker project, your provider will offer you the option of receiving the data messages via email or a web service (HTTP).
Personally I prefer email. So, here are a somewhat random collection of software tools which will automatically download the SBD data email attachments from GMail, parse them, upload data to the [HabHub Habitat Tracker](https://tracker.habhub.org),
and visualise the path of your tracker via Google Earth KML files.

## Downloading the SBD emails and attachments

The [Iridium 9603N Beacon](https://github.com/PaulZC/Iridium_9603_Beacon) transmits data messages containing its location, altitude, atmospheric pressure and temperature and other data.
The data is sent in Comma Separated Value (csv) format:

- GNSS Time and Date (YYYYMMDDhhmmss) (string),
- GNSS Latitude (degrees) (float),
- GNSS Longitude (degrees) (float),
- GNSS Altitude (m) (int),
- GNSS Speed (m/s) (float),
- GNSS Heading (Degrees) (int),
- GNSS HDOP (m) (float),
- GNSS satellites (int),
- Atmospheric Pressure (Pascals) (int),
- Temperature (C) (float),
- Battery (V) (float),
- Iteration Count (int)

E.g.:

20170729144631,55.866573,-2.428458,103,0.1,0,3.0,5,99098,25.3,4.98,0

It arrives as a .sbd file attached to an email from the Iridium system. The email itself contains other useful information:

- Message sequence numbers (so you can identify if any messages have been missed)
- The time and date the message session was processed by the Iridium system
- The status of the message session (was it successful or was the data corrupt)
- The size of the message in bytes
- The approximate latitude and longitude the message was sent from
- The approximate error radius of the transmitter�s location

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

So, it is beneficial to download both the email text and the attachment separately.

If you have your SBD messages sent to a GMail address, you can use IMAP4 to download the messages provided you alter your account settings
to allow IMAP access and [enable less secure apps](https://support.google.com/accounts/answer/6010255?hl=en)

[Iridium_SBD_GMail_IMAP_Downloader.py](https://github.com/PaulZC/Iridium_SBD_Tools/Iridium_SBD_GMail_IMAP_Downloader.py)
will check your inbox every 10 minutes for a new message from the Iridium system (with the subject _SBD Msg From Unit_).
If it finds one it will download the email text, download the email attachment, mark the message as seen (read) and
'move' it to a folder called SBD by changing the message labels. You will need to manually create the SBD folder in GMail before running the code.

IMAP4 is an out-of-date way of accessing email. GMail's preferred method is to use the GMail API which is more secure. You can enable access with
Python by following the instructions [here](https://developers.google.com/gmail/api/quickstart/python).

[Iridium_SBD_GMail_API_Downloader.py](https://github.com/PaulZC/Iridium_SBD_Tools/Iridium_SBD_GMail_API_Downloader.py) does the same job as the
IMAP downloader but using the API. As you will need _modify_ permission for your GMail mailbox, you will need to delete the gmail-python-quickstart.json
file in the .credentials directory. Then when you run the code for the first time, and sign in using your browser, your client_secret.json will get
copied across allowing modify access.

If you ever want to download all the SBD messages again, perhaps on a new computer, then
[Iridium_SBD_GMail_API_GetAllSBD.py](https://github.com/PaulZC/Iridium_SBD_Tools/Iridium_SBD_GMail_API_GetAllSBD.py) will do just that.

## Uploading data to the [HabHub Habitat Tracker Server](https://tracker.habhub.org)

If you want to use the excellent HabHub Habitat Tracker to track your flight, then first you need to talk to the [UKHAS team](https://ukhas.org.uk/) on [IRC](http://webchat.freenode.net/?channels=highaltitude) and register your flight.
Once you've done that, you can use [Iridium_9603N_Beacon_habhub_habitat_uploader.py](https://github.com/PaulZC/Iridium_SBD_Tools/Iridium_9603N_Beacon_habhub_habitat_uploader.py)
to check for the download of new SBD files, parse the files and upload the data to Habitat.

## Stitching

So far, all of the SBD messages have been downloaded individually. If you want to combine these together into a single linestring for Google Earth, then we need to stitch the files together.

[Iridium_SBD_Header_Stitcher.py](https://github.com/PaulZC/Iridium_SBD_Tools/Iridium_SBD_Header_Stitcher.py) goes through a directory and/or its subdirectories, looks for the text messages
downloaded from the Iridium system, parses them and builds up a csv �dictionary� of the SBD message sequence numbers (MOMSN) together with their session times and the approximate lat & lon the message was sent from.
This is a good idea if you are sending SBD messages very quickly as it is possible for the messages to arrive by email in the same second.
Therefore you can�t reliably use the email arrival time to establish unique timings for each message. By using the Iridium session time, you can guarantee that the timings are unique. 

[Iridium_9603N_Beacon_Stitcher.py](https://github.com/PaulZC/Iridium_SBD_Tools/Iridium_9603N_Beacon_Stitcher.py) goes through a directory and/or its subdirectories, looks for the .sbd message
attachments from the Iridium system (which contain the actual data transmitted by the beacon itself), appends them into a single csv file and adds the session time and message sequence numbers extracted by Header_Stitcher to the start of each entry.
That way you can be certain that each entry is unique (even if the emails arrived in the same second).

## Converting to KML

[Iridium_9603N_Beacon_to_KML.py](https://github.com/PaulZC/Iridium_SBD_Tools/Iridium_9603N_Beacon_to_KML.py) will convert the stitched SBD data together into Google Earth linestring, points and arrows format, allowing you
to visualise your flight around the globe without using the HabHub Tracker.
You can alter the code to either produce a linestring which is clamped to the ground, or one which shows a 3D representation of the flight altitude. Points overlaid on top of a clamped linestring looks nice. Arrows overlaid on clamped linestring makes it obvious which way your tracker was heading.

Enjoy!

**_Paul_**










