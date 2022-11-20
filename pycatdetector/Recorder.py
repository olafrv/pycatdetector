import cv2
import threading
from time import ctime, time
from queue import Queue
import logging
from urllib.parse import urlparse

class Recorder (threading.Thread):

    images = None
    rtspUrl = None
    must_stop = False
    logger = None

    def __init__(self, rtspUrl):
        threading.Thread.__init__(self)
        self.rtspUrl = rtspUrl
        self.logger = logging.getLogger(__name__)
        self.images = Queue(60*60)  # 1 hour of frames = 1 fps * 60 sec * 60 min
    
    def getImages(self) -> Queue:
        return self.images

    def run(self):
        self.logger.info("Starting...")
        self.record()
        self.logger.info("Stopped.")
        
    def stop(self):
        if not self.must_stop:
            self.logger.info("Stopping...")
            self.must_stop = True
        else:
            self.logger.info("Already stopped.")

    def maskUrl(self, url) -> str:
        parsed = urlparse(url)
        parsed.password # 'password'
        replaced = parsed._replace(netloc="{}:{}@{}".format(parsed.username, "???", parsed.hostname))
        return replaced.geturl() # 'https://user:???@example.com/path?key=value#hash'
        
    def record(self, greyscale=False, showVisor=False, saveImage=False):
        cap = cv2.VideoCapture(self.rtspUrl)
        if not cap.isOpened():
            self.logger.error("Connection error to: " + self.maskUrl(self.rtspUrl))
            self.stop()

        i = 0
        while(not self.must_stop):
            start_frame_number = 5
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame_number) # Skip n frames
            ret, frame = cap.read() # return numpy.array
            if greyscale: 
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if saveImage:
                cv2.imwrite('recording/opencv/imgx-' + str(i) + '.jpg', frame)
            if showVisor:
                cv2.imshow('frame', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                  break
            self.images.put(frame)
            i = i + 1

        cap.release()

        if showVisor:
            cv2.destroyAllWindows()