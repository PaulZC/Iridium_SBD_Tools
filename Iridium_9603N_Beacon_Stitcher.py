# Recursively stitches all sbd files into one csv file
# Reads Iridium Session Times from SBD_headers_stitched.csv
# Needs at least two sbd files to work properly

import os
import numpy as np

try:
    momsns = np.loadtxt('SBD_headers_stitched.csv', delimiter=',', unpack=True, usecols=(1,))
    session_times = np.genfromtxt('SBD_headers_stitched.csv', delimiter=',', unpack=True, usecols=(3,), dtype='str')
except:
    raise Exception('Could not process SBD_headers_stitched.csv!')

fp = open('SBD_stitched.csv','wb')
print 'Stitching sbd files into SBD_stitched.csv'
#print 'Using momsns:'
#print momsns
#print 'Using session_times:'
#print session_times

for root, dirs, files in os.walk("."):
    if len(files) > 0:
        #if root != ".": # Only check sub-directories
        if root == ".": # Only check this directory
            for filename in files:
                if filename[-4:] == '.sbd':
                    longfilename = os.path.join(root, filename)
                    msn = longfilename[-10:-4] + ','
                    rxtime = filename[0:8] + ' ' + filename[9:17] + ','
                    msnum = float(longfilename[-10:-4])
                    session_time = ''
                    for index, seqnum in enumerate(momsns):
                        if seqnum == msnum: session_time = session_times[index] + ','
                    if session_time != '':
                        print 'Appending',longfilename
                        fp.write(rxtime)
                        fp.write(session_time)
                        fp.write(msn)
                        fr = open(longfilename,'rb')
                        fp.write(fr.read())
                        fp.write('\r\n')
                    else:
                        print 'Skipping',longfilename,'(Could not match momsn)'
                    fr.close()
                
fp.close()

            
    
