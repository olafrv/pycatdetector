import os
import logging
import threading
import traceback
from typing import Optional
from numpy import ndarray
from queue import SimpleQueue
from time import sleep
from datetime import datetime
from PIL import Image
from .AbstractNeuralNet import AbstractNeuralNet
from .Encoder import Encoder


class Detector(threading.Thread):
    """
    The Detector class represents a thread that performs object
    detection using a neural network reading from image queue.

    Args:
        recorder (Recorder): The recorder object providing the image queue.
        screener_enabled (bool): Flag indicating if the screener is enabled.
        net (AbstractNeuralNet): The neural network object.
        notify_min_score (int): The minimum score for notifications.
        encoder_folder (str): The folder path for encoding videos.
    """

    SLEEP_TIME_MIN = 0.05  # seconds, avoid CPU overload

    def __init__(
        self,
        images: SimpleQueue,
        screener_enabled: bool,
        net: AbstractNeuralNet,
        notify_min_score: float,
        encoder_folder: str,
    ):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.images = images
        self.net = net
        self.notify_min_score = notify_min_score
        self.screener_enabled = screener_enabled
        self.images_boxed = SimpleQueue()
        self.labels = []
        self.detections = SimpleQueue()
        self.encoder_folder = encoder_folder
        self.video_path = ""
        self.sleep_time = 10  # seconds, start with worst case
        self.must_stop = False

    def disable_screener(self):
        """
        Disable the screener (stop pushing images to the image_boxes queue)
        """
        self.screener_enabled = False

        if self.images_boxed is not None:
            self.images_boxed.empty()
            self.logger.info(
                "Screener disabled. Queue: %i." % self.images_boxed.qsize()
            )

    def get_detections(self):
        """
        Get the detections queue, used by the notifier.

        Returns:
            SimpleQueue: The detections queue.
        """
        return self.detections

    def get_images(self) -> SimpleQueue:
        """
        Get the images queue coming from the recorder.

        Returns:
            SimpleQueue: The images queue.
        """
        return self.images_boxed

    def set_labels(self, labels):
        """
        Set the labels for which if detected a notification must be sent.

        Args:
            labels (list): The list of labels.
        """
        self.labels = labels

    def get_video_path(self) -> str:
        """
        Get the video path.

        Returns:
            str: The video path.
        """
        return self.video_path

    def set_video_path(self):
        """
        Set the video path.
        """
        if not os.path.exists(self.encoder_folder):
            self.logger.info("Creating folder: " + self.encoder_folder)
            os.makedirs(self.encoder_folder)
        video_name = "output-" + datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".avi"

        self.video_path = os.path.join(self.encoder_folder, video_name)

    def stop(self):
        """
        Stop the detector thread.
        """
        if not self.must_stop:
            self.logger.info("Stopping...")

            self.must_stop = True
        else:
            self.logger.info("Already stopped")

    def run(self):
        """
        Run the detector thread.
        """
        self.logger.info("Starting with Thread ID: %s" % threading.get_native_id())
        self.logger.info("Minimum Score: " + str(self.notify_min_score))

        encoder = None
        if len(self.encoder_folder) > 0:
            self.logger.info("Encoder folder: " + self.encoder_folder)
            self.set_video_path()
            self.logger.info("Encoding video to: " + self.video_path)
            encoder = Encoder(self.video_path)

        while not self.must_stop:
            if not self.images.empty():
                image_raw: ndarray = self.images.get(False)

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
                        self.sleep_time = (analyze_duration + self.sleep_time) / 2

                images_queued = self.images.qsize()
                self.logger.debug(
                    "Analisis: %.3fs, Shape: %s, Queue: %i"
                    % (analyze_duration, str(image_raw.shape), images_queued)
                )

                all_scored_labels = self.net.get_scored_labels(result=result)

                min_scored_labels = self.net.get_scored_labels(
                    result=result, min_score=self.notify_min_score
                )

                self.logger.debug("Scores: %s" % repr(all_scored_labels))
                self.logger.debug(
                    "Scores >%.2f): %s"
                    % (self.notify_min_score, repr(min_scored_labels))
                )

                image_boxed: Optional[Image.Image] = None
                if self.screener_enabled or encoder:
                    image_boxed = self.net.plot(result)
                    if self.screener_enabled:
                        self.images_boxed.put(image_boxed)

                # detection: dict
                # 'image': The original image data (e.g., numpy array).
                # 'label': The detected object's class label (e.g., "cat").
                # 'score': The confidence score for the detection (e.g., 0.92).
                # 'box': The bounding box coordinates (e.g., [x1, y1, x2, y2]).
                # 'timestamp': The time (e.g., "2023-10-01T12:00:00Z").

                for detection in min_scored_labels:

                    if detection["label"] not in self.labels:
                        self.logger.debug("Ignored: " + repr(detection))
                        continue

                    detection["image"] = image_boxed
                    detection["timestamp"] = str(
                        datetime.now().astimezone().isoformat()
                    )

                    self.detections.put(detection)

                    self.logger.info(
                        "Match: "
                        + repr(
                            {"label": detection["label"], "score": detection["score"]}
                        )
                    )

                    if encoder and image_boxed is not None:
                        self.logger.debug("Adding +1 frame to: %s", self.video_path)
                        encoder.add_image(image_boxed)

                self.logger.debug(
                    "Sleeping %.3fs due to empty queue..." % self.sleep_time
                )

                # Better sleep than not answering termination signals
                sleep(self.sleep_time)

        if encoder:
            self.logger.info("Closing video at: " + self.video_path)
            encoder.close()

        self.logger.info("Stopped.")
