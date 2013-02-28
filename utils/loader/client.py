# Task worker
# Connects PULL socket to tcp://localhost:5557
# Collects workloads from ventilator via that socket
# Connects PUSH socket to tcp://localhost:5558
# Sends results to sink via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import sys
import time
import zmq
import json
import subprocess
import psycopg2
import os
import tempfile
from cStringIO import StringIO

XML_TEMPLATE='/Users/howardbutler/dev/git/weblas/utils/loader/load-postgres.xml'
PDAL = '/Users/howardbutler/dev/git/pdal/bin/'
PCPIPELINE=os.path.join(PDAL,'pcpipeline')
PC2PC=os.path.join(PDAL, 'pc2pc')
DATADIR='/Volumes/lidar4/raw'

def get_pipeline(filename):
    import xml.etree.ElementTree as ET
    root = ET.parse(XML_TEMPLATE).getroot()
    reader = list(root.iter('Reader'))[0]
    for option in reader:
        if option.attrib['name'] == 'filename':
            option.text = os.path.join(DATADIR,filename)
    
    return ET.tostring(root)

def decompress(filename):
    
    basename = os.path.splitext(os.path.basename(filename))[0]
    lasname = basename + ".las"
    
    tempname = os.path.join(tempfile.gettempdir(), lasname)
    
    command = '%s -i %s -o %s' % (PC2PC, os.path.join(DATADIR,filename), tempname)
    # print command
    process = subprocess.Popen(command.split(), shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    
    d = process.communicate()
    return tempname

def load(filename):
    
    command = '%s --stdin' % (PCPIPELINE)
    xml = get_pipeline(filename)
    process = subprocess.Popen(command.split(), shell=False, stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE)    
    d = process.communicate(input=xml)
    return d


if __name__ == "__main__":
    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.PULL)
    receiver.connect("tcp://localhost:5557")

    # Socket to send messages to
    logger = context.socket(zmq.PUSH)
    logger.connect("tcp://localhost:5558")

    # Process tasks forever
    while True:
        s = receiver.recv()
        
        j = json.loads(s)
        
        task = j['task']
        
        if task == 'load':
            filename = j['filename']
            lasname = decompress(filename)
            loaded = load(lasname)
            
            success = True
            error = ''
            if loaded[0]:
                error = loaded[0]
                success = False
            output = {  'success': success, 
                        'filename': filename, 
                        'error':error }

            j = json.dumps(output)

            logger.send(j)