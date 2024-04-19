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
        self.sleep_time = 0.5  # seconds

    def close(self, event=None):  # noqa -- mpl_connect event required
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
                # better sleep than not react to termination signals
                self.logger.debug("Sleeping %.2f, due to empty queue..."
                                  % self.sleep_time)
                sleep(self.sleep_time)
        plt.close('all')
        self.detector.disable_screener()
        self.logger.info("Closed.")
