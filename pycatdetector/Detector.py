import logging
import threading
import logging
from . import NeuralNet
from . import Recorder
from queue import Queue
from time import sleep
from datetime import datetime

class Detector(threading.Thread):
    net = None
    images = None
    tests = None
    detections = None
    must_stop = False
    logger = None

    def __init__(self, recorder: Recorder, net: NeuralNet):
        threading.Thread.__init__(self)
        self.images = recorder.getImages()
        self.net = net
        self.net_min_score = 0.5
        self.tests =  Queue(60*60)  # 1 hour of frames = 1 fps * 60 sec * 60 min
        self.detections = Queue(60*60)  # 1 hour of frames = 1 fps * 60 sec * 60 min
        self.logger = logging.getLogger(__name__)
        
    def stop(self):
        if not self.must_stop:
            self.logger.info("Stopping...")
            self.must_stop = True
        else:
            self.logger.info("Already stopped")

    def run(self):
        self.logger.info("Starting...")
        minScore = 0.5
        while(not self.must_stop):
            if not self.images.empty():                
                image = self.images.get(block=False)
                
                try:
                    result = self.net.analyze(image)
                except ValueError:
                    self.logger.error("Corruptied image")
                    continue

                self.tests.put(result)
                self.logger.debug('Test: ' + repr(self.net.get_scored_labels(-1, result)))
                detections = self.net.get_scored_labels(minScore, result)
                for detection in detections:
                    detection['timestamp'] = datetime.now()
                    detection['minScore'] = minScore 
                    self.detections.put(detection)
                    self.logger.info('Detected:' + repr(detection))
            else:
                self.logger.debug("Queue is empty.")
                sleep(0.1) # better to sleep than block=True and not react to termination signals

        self.logger.info("Stopped.")

    def get_detections(self) -> Queue:
        return self.detections

    def get_tests(self) -> Queue:
        return self.tests

    def get_net(self):
        return self.net