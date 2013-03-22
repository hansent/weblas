"""

   Least-recently used (LRU) queue device
   Demonstrates use of pyzmq IOLoop reactor

   While this example runs in a single process, that is just to make
   it easier to start and stop the example. Each thread has its own
   context and conceptually acts as a separate process.

   Author: Min RK <benjaminrk(at)gmail(dot)com>
   Adapted from lruqueue.py by Guillaume Aubert (gaubert) <guillaume(dot)aubert(at)gmail(dot)com>

"""

import threading
import time
import zmq
import json
import random
import sys
import os
import subprocess
import tempfile

# DATADIR='/Volumes/lidar4/raw'
XML_TEMPLATE='/Users/howardbutler/dev/git/weblas/utils/loader/load-postgres.xml'
PDAL_BIN = '/Users/howardbutler/dev/git/pdal/bin/'
# DATADIR = '/Users/howardbutler/dev/git/pdal/test/data'

class LASfileError(Exception):
    pass

class LASfile(object):
    
    def __init__(self, lazfile):
        self.lazfile = lazfile
        
        self.template ='/Users/howardbutler/dev/git/weblas/utils/loader/load-postgres.xml'
        PDAL = '/Users/howardbutler/dev/git/pdal/bin/'
        self.PCPIPELINE=os.path.join(PDAL_BIN,'pcpipeline')
        self.PC2PC=os.path.join(PDAL_BIN, 'pc2pc')
        self.PCINFO=os.path.join(PDAL_BIN, 'pcinfo')        
    
    def verify(self):
        if not os.path.exists(self.lazfile):
            raise LASfileError("the filename '%s' does not exist"% self.lazfile)

        command = '%s --schema -i %s' % (self.PCINFO, self.lazfile)
        # print command
        process = subprocess.Popen( command.split(), 
                                    shell = False,
                                    stdin = subprocess.PIPE,
                                    stderr = subprocess.PIPE,
                                    stdout = subprocess.PIPE)
        output = process.communicate()
        # print "output[1]: '%s'" % output[1]
        bad_code="""ERROR 6: EPSG PCS/GCS code 5103 not found in EPSG support files.  Is this a valid
EPSG coordinate system?
"""
        if not (output[1] == '' or output[1] == bad_code):
            raise LASfileError("Unable to verify that '%s' is a LAZ/LAS file" % self.lazfile)

        
    def get_pipeline(self, template, filename):
        import xml.etree.ElementTree as ET
        root = ET.parse(template).getroot()
        reader = list(root.iter('Reader'))[0]
        for option in reader:
            if option.attrib['name'] == 'filename':
                option.text = filename
    
        return ET.tostring(root)

    def decompress(self):
    
        basename = os.path.splitext(os.path.basename(self.lazfile))[0]
        lasname = basename + ".las"
    
        lasname = os.path.join(tempfile.gettempdir(), lasname)    
        command = '%s -i %s -o %s' % (self.PC2PC, self.lazfile, lasname)
       # print command
        process = subprocess.Popen( command.split(), 
                                    shell=False, 
                                    stdin=subprocess.PIPE, 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)    
        d = process.communicate()
        return lasname

    def load(self):
        
        self.verify()
        
        lasname = self.decompress()
        xml = self.get_pipeline(self.template, lasname)

        command = '%s --stdin' % (self.PCPIPELINE)
        
        #print command

        process = subprocess.Popen( command.split(), 
                                    shell=False, 
                                    stdin=subprocess.PIPE, 
                                    stderr=subprocess.PIPE, 
                                    stdout=subprocess.PIPE)    
        d = process.communicate(input=xml)
        
        if d[0]:
            raise LASfileError("Unable to load file with error '%s'" % d[0])

        # delete tempfile
        try:
            os.remove(lasname)
        except OSError:
            pass
                
        return d    

def worker_thread(worker_url, logger_url, i):
    """ Worker using REQ socket to do LRU routing """
    
    context = zmq.Context()
    broker = context.socket(zmq.REQ)

    logger = context.socket(zmq.PUSH)
    logger.connect(logger_url)
    
    identity = "Worker-%d" % (i)

    broker.setsockopt(zmq.IDENTITY, identity) #set worker identity
    # 
    try:
        broker.connect(worker_url)
    except:
        print 'unable to connect'
        exit
    # Tell the borker we are ready for work
    
    j = {'status':'READY', 'address':identity }
    broker.send(json.dumps(j))

    try:
        while True:
            
            message = broker.recv_multipart()
            address, empty, s = message[0], message[1], message[2]

            j = json.loads(s)
            assert empty == ""
                
            try:
                
                f = LASfile(j['filename'])
                print 'loading ', j['filename']
                f.load()
                print 'loaded ', j['filename']
                j['status'] = 'OK'
            except LASfileError, e:
                j['status'] = 'FAILED'
                j['error'] = e.message
            
            if j['status'] == 'OK':
                j['success'] = True
                j['error'] = ""
            elif j['status'] == 'FAILED':
                j['success'] = False

            broker.send_multipart([address, "", json.dumps(j)])
            logger.send_multipart([address, "", json.dumps(j)])
    except zmq.ZMQError, zerr:
        # context terminated so quit silently
        if zerr.strerror == 'Context was terminated':
            return
        else:
            raise zerr




def main():
    """main method"""
    
    import sys
    broker_port = 5558
    logger_port = 5559
    workers = 1
    
    base_url = "tcp://0.0.0.0:%d" 
    
    broker_url = base_url % broker_port
    logger_url = base_url % logger_port   

    broker_url = 'ipc://worker'
    logger_url = 'ipc://logger'      
    
    if len(sys.argv) > 1:
        workers = int(sys.argv[1])
    for i in range(workers):
        thread = threading.Thread(target=worker_thread, args=(broker_url, logger_url, i, ))
        thread.start()



if __name__ == "__main__":
    main()