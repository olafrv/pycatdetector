import logging
import threading
from time import sleep
from datetime import datetime, timedelta

class Notifier(threading.Thread):
    detector = None
    must_stop = False
    object_labels = None
    logger = None
    iot = None
    notifications = {}
    delay_seconds = 2*60

    def __init__(self, detector, object_labels, iot):
        threading.Thread.__init__(self)
        self.detector = detector
        self.object_labels = object_labels
        self.iot = iot
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Starting...")

        detections = self.detector.get_detections()
        while(not self.must_stop):
            if not detections.empty():
                detection = detections.get(block=False)
                if detection['label'] in self.object_labels:                    
                    if self.notify():
                        self.logger.info('Notified via ' + self.iot.get_name() + ' about ' + repr(detection))
            else:
                self.logger.debug("Queue is empty.")
                sleep(0.1) # better to sleep than block=True and not react to termination signals

        self.logger.info("Stopped.")
       
    def stop(self):
        if not self.must_stop:
            self.logger.info("Stopping...")
            self.must_stop = True
        else:
            self.logger.info("Already stopped")
 
    def notify(self):
        now = datetime.now()
        send = True
        if self.iot.get_name() in self.notifications:
            last = self.notifications[self.iot.get_name()]
            delta_seconds = int((now - last).total_seconds())
            if delta_seconds <= self.delay_seconds:
                send = False
        if send:
            self.iot.notify()
            self.notifications[self.iot.get_name()] = now
        return send