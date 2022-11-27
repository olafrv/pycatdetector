import logging
import threading
import traceback
import logging
from . import NeuralNet
from . import Recorder
from queue import SimpleQueue
from time import sleep
from datetime import datetime

class Detector(threading.Thread):
    net = None
    net_min_score = 0.9
    images = None
    tests = None
    detections = None
    sleep_time = 1 # seconds
    must_stop = False
    logger = None

    def __init__(self, recorder: Recorder, net: NeuralNet):
        threading.Thread.__init__(self)
        self.images = recorder.getImages()
        self.net = net
        self.tests =  SimpleQueue()  
        self.detections = SimpleQueue()
        self.logger = logging.getLogger(__name__)
        
    def stop(self):
        if not self.must_stop:
            self.logger.info("Stopping...")
            self.must_stop = True
        else:
            self.logger.info("Already stopped")

    def run(self):

        self.logger.info("Starting with Thread ID: %s" % (threading.get_native_id()))
        self.logger.info('Minimum Score: '+str(self.net_min_score))

        while(not self.must_stop):               
            
            if not self.images.empty():
                image = self.images.get(False)

                try:
                    result = self.net.analyze(image)
                except:
                    self.logger.error(traceback.format_exc())
                    continue

                self.tests.put(result)
                self.logger.debug('Test: ' + repr(self.net.get_scored_labels(-1, result)))

                detections = self.net.get_scored_labels(self.net_min_score, result)
                for detection in detections:
                    detection['timestamp'] = str(datetime.now())
                    self.detections.put(detection)
                    self.logger.info('Queued: '+str(self.images.qsize())+', Detection: ' + repr(detection))
            else:
                self.logger.debug("Sleeping "+str(self.sleep_time)+"s due to empty queue...")
                sleep(self.sleep_time) # Better sleep than not answering signals

        self.logger.info("Stopped.")


    def get_detections(self):
        return self.detections

    def get_tests(self):
        return self.tests

    def get_net(self):
        return self.net