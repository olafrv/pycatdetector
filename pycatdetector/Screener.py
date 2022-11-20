from time import sleep
from queue import Queue
from matplotlib import pyplot as plt
import logging

class Screener:
    detector = None
    must_stop = False
    logger = None
    neuralnet = None

    def __init__(self, detector):
        self.detector = detector
        self.logger = logging.getLogger(__name__)

    def close(self, event = None):
        if not self.must_stop:
            self.logger.info("Closing...")
            self.must_stop = True
        else:
            self.logger.info("Already closed.")

    def show(self):
        self.logger.info("Showing...")
        plt.ion()
        fig = plt.figure()
        fig.canvas.mpl_connect('close_event', self.close)
        ax = fig.add_subplot()
        tests = self.detector.get_tests()
        net = self.detector.get_net()
        while(not self.must_stop):
            ax.clear()
            if not tests.empty():
                detection = tests.get(block=False)
                net.plot(detection, ax)
                fig.canvas.draw()
                fig.canvas.flush_events()
            else:
                self.logger.debug("Queue is empty.")
                sleep(0.1) # better to sleep than block=True and not react to termination signals
        plt.close('all')
        self.logger.info("Closed.")
