import os
import logging
import threading
import traceback
from .AbstractNeuralNet import AbstractNeuralNet
from .Recorder import Recorder
from .Encoder import Encoder
from queue import SimpleQueue
from time import sleep
from datetime import datetime


class Detector(threading.Thread):
    net = None
    notify_min_score = None
    images = None
    images_boxed = None
    detections = None
    screenerOn = False
    sleep_time = 0.1  # seconds
    must_stop = False
    logger = None

    def __init__(self,
                 recorder: Recorder,
                 screener_enabled: bool,
                 net: AbstractNeuralNet,
                 notify_min_score: int,
                 encoder_folder: str):
        threading.Thread.__init__(self)
        self.images = recorder.get_images()
        self.net = net
        self.notify_min_score = notify_min_score
        self.screener_enabled = screener_enabled
        self.images_boxed = SimpleQueue() if self.screener_enabled else None
        self.detections = SimpleQueue()
        self.logger = logging.getLogger(__name__)
        self.encoder_folder = encoder_folder
        self.encoder_active = False

    def stop(self):
        if not self.must_stop:
            self.logger.info("Stopping...")
            self.must_stop = True
        else:
            self.logger.info("Already stopped")

    def run(self):

        self.logger.info(
                        "Starting with Thread ID: %s"
                        % (threading.get_native_id())
                        )
        self.logger.info('Minimum Score: '+str(self.notify_min_score))

        if len(self.encoder_folder) > 0:
            if not os.path.exists(self.encoder_folder):
                self.logger.info('Creating folder: ' + self.encoder_folder)
                os.makedirs(self.encoder_folder)
            video_name = "output-" + \
                datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".avi"
            video_path = os.path.join(self.encoder_folder, video_name)
            self.logger.info('Encoding video to: ' + video_path)
            encoder = Encoder(video_path)
            self.encoder_active = True

        while (not self.must_stop):

            if not self.images.empty():

                image_raw = self.images.get(False)

                try:
                    result = self.net.analyze(image_raw)
                except:  # noqa -- flake8 skip
                    self.logger.error(traceback.format_exc())
                    continue

                all_scored_labels = self.net.get_scored_labels(-1, result)
                min_scored_labels = \
                    self.net.get_scored_labels(self.notify_min_score, result)

                self.logger.debug("ALL: " + repr(all_scored_labels))
                self.logger.debug("MIN: " + repr(min_scored_labels))

                if self.screener_enabled or self.encoder_active:
                    image_boxed = self.net.plot(result)

                if self.screener_enabled:
                    self.images_boxed.put(image_boxed)

                for detection in min_scored_labels:
                    detection['timestamp'] = str(datetime.now())
                    self.detections.put(detection)
                    self.logger.info(
                        'Queued: ' + str(self.images.qsize()) +
                        ', Shape:' + str(image_raw.shape) +
                        ', Detection: ' + repr(detection)
                    )
                    if self.encoder_active:
                        self.logger.debug('Adding to video...')
                        encoder.add_image(image_boxed)

                self.logger.debug(
                    "Sleeping " +
                    str(self.sleep_time) +
                    "s due to empty queue...")

                # Better sleep than not answering termination signals
                sleep(self.sleep_time)

        if self.encoder_active:
            self.logger.info('Closing video at: ' + video_path)
            encoder.close()

        self.logger.info("Stopped.")

    def get_detections(self):
        return self.detections

    def get_images(self):
        return self.images_boxed
