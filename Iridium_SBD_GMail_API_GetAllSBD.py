# Iridium SBD GMail Get-All-BSD-Messages using the GMail API

# Logs into GMail using the API, finds all messages with the label SBD,
# saves the messages and attachments to file

# Follow these instructions to create your credentials:
# https://developers.google.com/gmail/api/quickstart/python

from __future__ import print_function
import httplib2
import os
import base64
import email
import datetime
import time

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

def ListMessagesWithLabel(service, user_id, lbl):
    """List all Messages of the user's mailbox with label lbl applied.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        lbl: Only return Messages with this label applied.

    Returns:
        List of Messages that have the specified label applied. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate id to get the details of a Message.
    """
    # Find Label_ID of lbl
    results = service.users().labels().list(userId=user_id).execute()
    labels = results.get('labels', [])
    for label in labels:
        if label['name'] == lbl: lbl_id = label['id']

    response = service.users().messages().list(userId=user_id,labelIds=lbl_id).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])

    while 'nextPageToken' in response:
        page_token = response['nextPageToken']
        response = service.users().messages().list(userId=user_id, labelIds=lbl_id, pageToken=page_token).execute()
        messages.extend(response['messages'])

    return messages
    
def SaveAttachments(service, user_id, msg_id):
    """Get and store attachment from Message with given id.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: ID of Message containing attachment.
    """
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    local_date = datetime.datetime.fromtimestamp(float(message['internalDate'])/1000.)
    date_str = local_date.strftime("%y-%m-%d_%H-%M-%S_")

    for part in message['payload']['parts']:
        if part['filename']:
            if 'data' in part['body']:
                data=part['body']['data']
            else:
                att_id=part['body']['attachmentId']
                att=service.users().messages().attachments().get(userId=user_id, messageId=msg_id,id=att_id).execute()
                data=att['data']
            file_data = base64.urlsafe_b64decode(data.encode('UTF-8'))
            path = date_str+part['filename']

            with open(path, 'w') as f:
                f.write(file_data)
                f.close()

def SaveMessageBody(service, user_id, msg_id):
    """Save the body from Message with given id.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: ID of Message.
    """
    message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mime_msg = email.message_from_string(msg_str)
    messageMainType = mime_msg.get_content_maintype()
    file_data = ''
    #print(messageMainType)
    if messageMainType == 'multipart':
        for part in mime_msg.get_payload():
            partType = part.get_content_maintype()
            #print('...'+partType)
            if partType == 'multipart':
                for multipart in part.get_payload():
                    multipartType = multipart.get_content_maintype()
                    #print('......'+multipartType)
                    if multipartType == 'text':
                        file_data += multipart.get_payload()
                        break # Only get the first text payload
            elif partType == 'text':
                file_data += part.get_payload()
    elif messageMainType == 'text':
        file_data += mime_msg.get_payload()

    local_date = datetime.datetime.fromtimestamp(float(message['internalDate'])/1000.)
    date_str = local_date.strftime("%y-%m-%d_%H-%M-%S_")
    
    subject = GetSubject(service, user_id, msg_id);
    for c in r' []/\;,><&*:%=+@!#^()|?^': # substitute any invalid characters
        subject = subject.replace(c,'_')
 
    path = date_str+subject+".txt"

    with open(path, 'w') as f:
        f.write(file_data)
        f.close()

def GetSubject(service, user_id, msg_id):
    """Returns the subject of the message with given id.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: ID of Message.
    """
    subject = ''
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()
    payload = message["payload"]
    headers = payload["headers"]
    for header in headers:
        if header["name"] == "Subject":
            subject = header["value"]
            break
    return subject

def main():
    """Creates a Gmail API service object.
    Searches for all messages with the label SBD.
    Saves the message body and attachment to disk.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    messages = ListMessagesWithLabel(service, 'me', 'SBD')
    if messages:
        for message in messages:
            print('Processing: '+GetSubject(service, 'me', message["id"]))
            SaveMessageBody(service, 'me', message["id"])
            SaveAttachments(service, 'me', message["id"])
    else:
        print('No messages found!')

if __name__ == '__main__':
    print('Iridium SBD GMail API - Get All SBD Messages')
    main()
