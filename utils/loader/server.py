# Task ventilator
# Binds PUSH socket to tcp://localhost:5557
# Sends batch of tasks to workers via that socket
#
# Author: Lev Givon <lev(at)columbia(dot)edu>

import zmq
import random
import time
import json
import subprocess

DATADIR='/Volumes/lidar4/raw'

context = zmq.Context()

# Socket to send messages on
sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:5557")

# Socket with direct access to the sink: used to syncronize start of batch
sink = context.socket(zmq.PUSH)
sink.connect("tcp://localhost:5558")


# The first message is "0" and signals start of batch
start = {'status':'start'}
sink.send(json.dumps(start))

l = 'ls %s' % DATADIR
process = subprocess.Popen(l.split(), shell=False, stdout=subprocess.PIPE)
files = process.communicate()[0].split()

files = ['05484602.laz',]
for f in files:

    # Random workload from 1 to 100 msecs
    s = {'task':'load', 'filename': f}
    j = json.dumps(s)

    sender.send(j)

# end = {'status':'shutdown'}
# sink.send(json.dumps(end))

