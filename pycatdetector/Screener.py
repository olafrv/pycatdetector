import logging
import matplotlib
import matplotlib.pyplot as plt
from time import sleep
from queue import SimpleQueue


class Screener:
    """
    A class that represents a image screener for PyCatDetector.

    Attributes:
        images (SimpleQueue): A queue containing images from the detector.
        must_stop (bool): flag indicating whether the thread must stop.
        logger (object): logger object for logging messages.
        SLEEP_TIME (float): sleep time in seconds between image updates.
    """

    SLEEP_TIME = 0.5  # seconds

    def __init__(self, images: SimpleQueue):
        """
        Initializes a new instance of the Screener class.

        Args:
            images (SimpleQueue): A queue containing images from the detector,
                                  images are PIL.Image.Image objects.
        """
        self.images = images
        self.must_stop = False
        self.logger = logging.getLogger(__name__)

    def close(self, event=None):
        """
        Closes the screener.

        Args:
            event (object, optional): The event object.
                                      Defaults to None, required by
                                      Matplotlib window close_event.
        """
        if not self.must_stop:
            self.logger.info("Closing...")
            self.must_stop = True
        else:
            self.logger.info("Already closed.")

    def show(self):
        """
        Shows the screener (Matplotlib window with images from the detector)
        """
        self.logger.info("Showing...")

        try:
            matplotlib.use("TkAgg")
        except ImportError:
            self.logger.warning("TkAgg backend is not available, headless=true?")
            return

        plt.ion()
        fig = plt.figure("PyCatDetector")
        fig.canvas.mpl_connect("close_event", self.close)
        ax = fig.add_subplot()
        imgs = self.images
        while not self.must_stop:
            ax.clear()
            if not imgs.empty():
                img = imgs.get(block=False)
                ax.imshow(img)
                fig.canvas.draw()
                fig.canvas.flush_events()
            else:
                self.logger.debug(
                    "Sleeping %.2f, due to empty queue..." % self.SLEEP_TIME
                )
                sleep(self.SLEEP_TIME)
        plt.close("all")
        self.logger.info("Closed.")
