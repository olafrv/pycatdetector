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
    labels = []
    detections = None
    video_path = None
    screenerOn = False
    SLEEP_TIME_MIN = 0.05  # seconds, avoid CPU overload
    sleep_time = 10  # seconds, start with worst case
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

    def disable_screener(self):
        self.screener_enabled = False
        self.images_boxed.empty()
        self.logger.info("Screener disabled. Queue: %i "
                         % self.images_boxed.qsize())

    def get_detections(self):
        return self.detections

    def get_images(self):
        return self.images_boxed

    def set_labels(self, labels):
        self.labels = labels

    def get_video_path(self):
        return self.video_path

    def set_video_path(self):
        if not os.path.exists(self.encoder_folder):
            self.logger.info('Creating folder: ' + self.encoder_folder)
            os.makedirs(self.encoder_folder)
        video_name = "output-" + \
            datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".avi"
        self.video_path = os.path.join(self.encoder_folder, video_name)

    def stop(self):
        if not self.must_stop:
            self.logger.info("Stopping...")
            self.must_stop = True
        else:
            self.logger.info("Already stopped")

    def run(self):

        self.logger.info("Starting with Thread ID: %s"
                         % threading.get_native_id())
        self.logger.info('Minimum Score: '+str(self.notify_min_score))

        if len(self.encoder_folder) > 0:
            self.logger.info('Encoder folder: ' + self.encoder_folder)
            self.set_video_path()
            self.logger.info('Encoding video to: ' + self.video_path)
            encoder = Encoder(self.video_path)
            self.encoder_active = True

        while (not self.must_stop):

            if not self.images.empty():

                image_raw = self.images.get(False)
                images_queued = self.images.qsize()

                try:
                    analyze_begin = datetime.now()
                    result = self.net.analyze(image_raw)
                    analyze_end = datetime.now()
                except:  # noqa -- flake8 skip
                    self.logger.error(traceback.format_exc())
                    continue

                analyze_duration = analyze_end - analyze_begin
                analyze_duration = analyze_duration.total_seconds()
                if analyze_duration < self.SLEEP_TIME_MIN:
                    # Avoid CPU overload on next cycle
                    self.sleep_time = self.SLEEP_TIME_MIN
                else:
                    if analyze_duration > self.sleep_time:
                        # Keep worst case for one more cycle
                        self.sleep_time = analyze_duration
                    else:
                        # Reduce based on average on next sleep
                        self.sleep_time = \
                            (analyze_duration + self.sleep_time)/2

                self.logger.debug(
                    "Analisis: %.3fs, Shape: %s, Queue: %i"
                    % (analyze_duration, str(image_raw.shape), images_queued)
                )

                all_scored_labels = self.net.get_scored_labels(result)
                min_scored_labels = \
                    self.net.get_scored_labels(result, self.notify_min_score)

                self.logger.debug("Scores: %s" % repr(all_scored_labels))
                self.logger.debug("Scores >%.2f): %s" %
                                  (self.notify_min_score,
                                   repr(min_scored_labels)))

                if self.screener_enabled or self.encoder_active:
                    image_boxed = self.net.plot(result)

                if self.screener_enabled:
                    self.images_boxed.put(image_boxed)

                for detection in min_scored_labels:
                    if detection['label'] not in self.labels:
                        self.logger.debug('Ignored: ' + repr(detection))
                        continue
                    detection['timestamp'] = \
                        str(datetime.now().astimezone().isoformat())
                    self.detections.put(detection)
                    self.logger.info('Match: ' + repr(detection))
                    if self.encoder_active:
                        self.logger.debug(
                            'Adding +1 frame to: %s', self.video_path)
                        encoder.add_image(image_boxed)

                self.logger.debug("Sleeping %.3fs due to empty queue..."
                                  % self.sleep_time)

                # Better sleep than not answering termination signals
                sleep(self.sleep_time)

        if self.encoder_active:
            self.logger.info('Closing video at: ' + self.video_path)
            encoder.close()

        self.logger.info("Stopped.")
