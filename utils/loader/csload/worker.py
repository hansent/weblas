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


def worker_thread(worker_url, logger_url, i):
    """ Worker using REQ socket to do LRU routing """
    
    context = zmq.Context()
    broker = context.socket(zmq.REQ)

    logger = context.socket(zmq.PUSH)
    logger.connect(logger_url)
    
    identity = "Worker-%d" % (i)

    broker.setsockopt(zmq.IDENTITY, identity) #set worker identity
    broker.connect(worker_url)

    # Tell the borker we are ready for work
    
    j = {'status':'READY', 'address':identity }
    broker.send(json.dumps(j))

    try:
        while True:
            
            message = broker.recv_multipart()
            print 'message: ', message
            address, empty, s = message[0], message[1], message[2]
            # import pdb;pdb.set_trace()
            j = json.loads(s)
            assert empty == ""
            print("%s: %s\n" %(identity, j))
            time.sleep (3.1)
            statuses = ['OK', 'FAILED']
            status = random.choice(statuses)      
            j['status'] = status
            # j['address'] = identity
            print 'did work, sending: ', [address, "", json.dumps(j)]
            
            if status == 'OK':
                j['success'] = True
                j['error'] = ""
            elif status == 'FAILED':
                j['success'] = False
                j['error'] = ' We failed '

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
    
    if len(sys.argv) > 1:
        workers = int(sys.argv[1])
    for i in range(workers):
        thread = threading.Thread(target=worker_thread, args=(broker_url, logger_url, i, ))
        thread.start()




if __name__ == "__main__":
    main()