from time import sleep
from matplotlib import pyplot as plt
import matplotlib
import logging


class Screener:

    detector = None
    must_stop = False
    logger = None

    def __init__(self, detector):
        self.detector = detector
        self.logger = logging.getLogger(__name__)

    def close(self, event = None):  # noqa
        if not self.must_stop:
            self.logger.info("Closing...")
            self.must_stop = True
        else:
            self.logger.info("Already closed.")

    def show(self):
        self.logger.info("Showing...")
        matplotlib.use('TkAgg')
        plt.ion()
        fig = plt.figure("PyCatDetector")
        fig.canvas.mpl_connect('close_event', self.close)
        ax = fig.add_subplot()
        imgs = self.detector.get_images()
        while (not self.must_stop):
            ax.clear()
            if not imgs.empty():
                img = imgs.get(block=False)
                ax.imshow(img)
                fig.canvas.draw()
                fig.canvas.flush_events()
            else:
                self.logger.debug("Queue is empty.")
                # better sleep than not react to termination signals
                sleep(0.1)
        plt.close('all')
        self.logger.info("Closed.")
