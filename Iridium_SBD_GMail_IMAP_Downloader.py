# Iridium SBD GMail Downloader using IMAP

# Logs into GMail using IMAP4, checks for Iridium SBD messages every minute,
# saves the message and attachment to file, and moves the message out of the inbox

# You need to enable IMAP in your GMail settings (Forwarding and POP/IMAP) and enable less secure apps:
# https://myaccount.google.com/lesssecureapps

# Based on https://gist.github.com/jasonrdsouza/1674794

import email, getpass, imaplib, os, datetime, time

folder = 'SBD' # Move messages to this GMail folder/label
search_str = '(SUBJECT \"SBD Msg From Unit\")' # Search for these messages
detach_dir = '.' # directory where to save attachments (default: current)

print 'Iridium SBD GMail Downloader'

# ask for username and password
user = raw_input("Enter your GMail username: ")
pwd = getpass.getpass("Enter your password: ")

print 'Use Ctrl-C to quit'

try:
    while True:

        # connect to the gmail imap server
        # (do this each time around the loop in case the connection has timed out)
        m = imaplib.IMAP4_SSL("imap.gmail.com")
        m.login(user,pwd)
        m.select("Inbox")

        #print 'Searching for messages:',search_str
        resp, items = m.search(None, search_str) 
        items = items[0].split() # get the mail ids

        for emailid in items:
            resp, data = m.fetch(emailid, "(RFC822)") # fetching the mail, "(RFC822)" means "get the whole stuff", but you can ask for headers only, etc
            email_body = data[0][1] # getting the mail content
            mail = email.message_from_string(email_body) # parsing the mail content to get a mail object

            # Check if message has any attachments at all
            if mail.get_content_maintype() != 'multipart':
                continue

            print mail["Subject"] + " " + mail["Date"]

            date_tuple = email.utils.parsedate_tz(mail['Date'])
            if date_tuple:
                local_date = datetime.datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                date_str = local_date.strftime("%y-%m-%d_%H-%M-%S_")

            # Create filename for message body from date and message subject
            body_filename = date_str + mail["Subject"] + ".txt"
            for c in r' []/\;,><&*:%=+@!#^()|?^': # substitute any invalid characters
                body_filename = body_filename.replace(c,'_')

            # we use walk to create a generator so we can iterate on the parts and forget about the recursive headach
            for part in mail.walk():
                # multipart are just containers, so we skip them
                if part.get_content_maintype() == 'multipart':
                    continue

                # is this the message body in text ?
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True)
                    att_path = os.path.join(detach_dir, body_filename)
                    #if not os.path.isfile(att_path) : # if the file does not already exist
                    fp = open(att_path, 'wb')
                    fp.write(str(body))
                    fp.close()
                    continue

                # is this part an attachment ?
                if part.get('Content-Disposition') is None:
                    continue

                # assemble filename for attachment
                filename = part.get_filename()
                filename = date_str + filename
                att_path = os.path.join(detach_dir, filename)
                #if not os.path.isfile(att_path) : # if the file does not already exist
                fp = open(att_path, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

            # Mark message as seen
            m.store(emailid, '+FLAGS', '(\Seen)')

            # 'Move' message
            m.store(emailid, '+X-GM-LABELS', folder)
            m.store(emailid, '+FLAGS', '(\Deleted)')
            m.expunge()

        for i in range(60):
            time.sleep(1) # Sleep for 1 min

except KeyboardInterrupt:
    print 'Ctrl-C received!'

finally:
    # logout
    m.close()
    m.logout()
    print 'Bye!'

    
