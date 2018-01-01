# Iridium SBD GMail API Forwarder

# Builds a dictionary of all existing sbd files
# Once per minute, checks for the appearance of a new sbd file
# When one is found, parses the file and forwards via email using the GMail API

# Create an API Key using this link:
# https://developers.google.com/maps/documentation/static-maps/get-api-key
# Save the key in a file called "Google_Static_Maps_API_Key.txt"

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

from __future__ import print_function

import numpy as np
import matplotlib.dates as mdates

import httplib2
import os
import base64
import email
from datetime import datetime
import time
import re

from email.mime.text import MIMEText

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient import errors

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-python-quickstart.json
#SCOPES = 'https://www.googleapis.com/auth/gmail.readonly' # Read only
SCOPES = 'https://www.googleapis.com/auth/gmail.modify' # Everything except delete
#SCOPES = 'https://mail.google.com/' # Full permissions
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'gmail-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message in html format.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text, 'html')
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_string())}

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except errors.HttpError, error:
    print('An error occurred: %s' % error)

if __name__ == '__main__':
    try:

        print('Iridium SBD GMail API Forwarder')

        try:
            to = raw_input('Enter the email address you want the SBD messages forwarded to: ')
        except:
            raise ValueError('Invalid email address!')
        if not re.match(r"[^@]+@[^@]+\.[^@]+", to):
            raise ValueError('Invalid email address!')

        try:
            with open('Google_Static_Maps_API_Key.txt', 'r') as myfile:
                key = myfile.read().replace('\n', '')
                myfile.close()
        except:
            raise ValueError('Could not read API Key!')

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
        print('Found',len(sbd),'existing sbd files')
        print('Checking once per minute for new ones...')

        path_str = "&path=color:red|weight:5"

        # Once per minute, check for the appearance of a new sbd file
        while (True):
            for l in range(60): # Sleep for 60x1 seconds (to allow KeyboardInterrupt to be detected quickly)
                time.sleep(1)

            #print('Checking for new SBD files...')

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
                                    print('Found new sbd file with MOMSN',msnum)
                                    sbd[msnum] = longfilename # Add new msn and filename to dictionary

                                    # Read the sbd file and unpack the data using numpy loadtxt
                                    gpstime,latitude,longitude,altitude,speed,heading,pressure,temperature,battery = \
                                        np.loadtxt(longfilename, delimiter=',', unpack=True, \
                                        usecols=(0,1,2,3,4,5,8,9,10), converters={0:mdates.strpdate2num('%Y%m%d%H%M%S')})

                                    pressure = int(round(pressure)) # Convert pressure to integer
                                    altitude = int(round(altitude))
                                    time_str = mdates.num2date(gpstime).strftime('%H:%M:%S %y/%m/%d')
                                    position_str = "{:.6f},{:.6f}".format(latitude, longitude)
                                    path_str += "|" + position_str

                                    # Assemble the message string in html format
                                    message = "<html>\n"
                                    message += "<head></head>\n"
                                    message += "<body>\n"
                                    message += "<p>\n"
                                    message += "Message from: "
                                    message += filename[-26:-11]
                                    message += "<br>\n"
                                    message += "Time: {}<br>\n".format(time_str)
                                    message += "Position: {}<br>\n".format(position_str)
                                    message += "Altitude (m): {}<br>\n".format(altitude)
                                    message += "Speed (m/s): {:.2f}<br>\n".format(speed)
                                    message += "Heading (Degrees): {:.1f}<br>\n".format(heading)
                                    message += "Pressure (Pascals): {}<br>\n".format(pressure)
                                    message += "Temperature (C): {}<br>\n".format(temperature)
                                    message += "Battery (V): {}<br>\n".format(battery)
                                    message += "MSNUM: {}<br><br>\n".format(msnum)

                                    # Add the Google Maps Link
                                    message += "<a href=\"https://www.google.com/maps/search/?api=1&map_action=map&query="
                                    message += position_str
                                    message += "\">Map</a><br><br>\n"

                                    # Add the Google Maps API StaticMap Path
                                    message += "<a href=\"https://maps.googleapis.com/maps/api/staticmap?center="
                                    message += position_str
                                    message += "&markers=color:red|"
                                    message += position_str
                                    message += path_str
                                    message += "&zoom=11&size=640x480&maptype=hybrid&key="
                                    message += key
                                    message += "\">Path</a><br>\n"

                                    message += "</p>\n"
                                    message += "</body>\n"
                                    message += "</html>\n"
                                    
                                    credentials = get_credentials()
                                    http = credentials.authorize(httplib2.Http())
                                    service = discovery.build('gmail', 'v1', http=http)

                                    user_profile = service.users().getProfile(userId='me').execute()
                                    sender = user_profile['emailAddress']
                                    subject = "SBD Message from " + filename[-26:-11]
                                    msg = create_message(sender, to, subject, message)
                                    send_message(service, 'me', msg)

    except KeyboardInterrupt:
        print('CTRL+C received...')

    finally:
        print('Bye!')
     
    
