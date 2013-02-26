import subprocess
import psycopg2
import os
import tempfile

XML_TEMPLATE='load-postgres.xml'
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
    return ET.dump(root)

def decompress(filename):
    
    basename = os.path.splitext(os.path.basename(filename))[0]
    lasname = basename + ".las"
    
    tempname = os.path.join(tempfile.gettempdir(), lasname)
    
    command = '%s -i %s -o %s' % (PC2PC, os.path.join(DATADIR,filename), tempname)
    print command
    process = subprocess.Popen(command.split(), shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)    
    d = process.communicate()
    # print d
    
    return tempname


if __name__ == '__main__':
    connection = psycopg2.connect('host=localhost dbname=iowa')
    l = 'ls %s' % DATADIR
    process = subprocess.Popen(l.split(), shell=False, stdout=subprocess.PIPE)
    files = process.communicate()[0].split()
    print len(files)
    
    print decompress('05484602.laz')
    # print get_pipeline(files[0])