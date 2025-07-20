import logging
import threading
import traceback
import numpy
import cv2
from time import sleep
from datetime import datetime
from typing import Optional
from pycatdetector.channels.AbstractChannel import AbstractChannel

class Notifier(threading.Thread):
    """
    A class representing a notifier thread that sends
    notifications based on detections.

    Attributes:
        detector: The detector object.
        must_stop: A boolean indicating whether the thread must stop.
        queue_sleep: The sleep time in seconds for empty queue polling.
        channels: A dictionary mapping labels to channel objects.
        logger: The logger object.
        notifications: A dictionary mapping channel IDs
                       to their last notification time.
        detections: The detections queue.
        NOTIFY_DELAY: The delay in seconds for same object detection.
        notify_window_start: The start time of the notification
                             window in HH:MM 24h format.
        notify_window_end: The end time of the notification
                           window in HH:MM 24h format.
    """
    NOTIFY_DELAY = 2*60  # seconds, less noise for same object detection

    def __init__(self, detections):
        """
        Initializes a Notifier object.

        Args:
            detections: The detections queue.
        """
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.detector = None
        self.must_stop = False
        self.queue_sleep = 1  # seconds, less queue polling, honor exit signals
        self.channels = {}  # indexed per object label (from the detected object)
        self.notifications = {}
        self.detections = detections
        self.notify_window = {}  # indexed per channel (class name snake cased)


    def add_channel(self, channel: AbstractChannel, labels: list[str]):
        """
        Adds channel used for notifications when labels are detected.

        Args:
            channel: The channel instance.
            labels: A list of object labels (detection).
        """
        for label in labels:
            self.logger.info(
                "Channel '%s' will notify for the label '%s'" % (channel.get_name(), label)
            )
            if label not in self.channels.keys():
                self.channels[label] = [channel]
            else:
                self.channels[label].append(channel)

    def get_labels(self) -> list:
        """
        Returns the list of labels.
        """
        return list(self.channels.keys())

    def add_notify_window(self, 
                          channel: AbstractChannel, 
                          window_name: str, 
                          window_schedule: dict):
        """
        Sets the channel's notification window (schedule).

        Args:
            channel_name (str): The name of the channel.
            window_name (str): The name of the notification window.
            window_schedule (dict): The schedule for the notification window.
        """
        channel_name = channel.get_name()
        if channel_name not in self.notify_window:
            self.notify_window[channel_name] = {}

        self.notify_window[channel_name][window_name] = window_schedule

    def is_notify_window_open(self, channel: AbstractChannel) -> bool:
        """
        Checks if the notification window is open.

        Returns:
            A boolean indicating whether the notification window is open.
        """
        channel_name = channel.get_name()
        if channel_name not in self.notify_window:
            self.logger.info(
                "Channel '%s' has no notify windows configured, skipping." % channel_name
            )
            return False
        else:
            opened = False
            for window_name, schedule in self.notify_window[channel_name].items():
                active_days = schedule["days"].split(",")
                active_days = [day.strip().lower() for day in active_days]
                now_day_name = datetime.now().strftime('%a').lower()
                if now_day_name in active_days:
                    notify_window_start = schedule["start"]
                    notify_window_end = schedule["end"]
                    now = datetime.now()
                    start = datetime.strptime(notify_window_start, "%H:%M")
                    start = start.replace(
                        day=now.day, month=now.month, year=now.year)
                    end = datetime.strptime(notify_window_end, "%H:%M")
                    end = end.replace(
                        day=now.day, month=now.month, year=now.year)
                    opened = start <= now <= end
                    if opened:
                        self.logger.info(
                            "Notify window '%s' for channel '%s' is open: %s <= %s <= %s"
                            % (window_name, channel_name, start, now, end)
                        )
                        break
            return opened

    def run(self):
        """
        Starts the notifier thread.
        """
        self.logger.info("Started Thread ID: %s" % (threading.get_native_id()))
        while (not self.must_stop):

            if self.detections.empty():
                self.logger.debug("Sleeping %.2fs due to empty queue..."
                                  % self.queue_sleep)
                sleep(self.queue_sleep)
                continue

            detection = self.detections.get(block=False)
            detected_label = detection['label']

            if detected_label in self.channels.keys():

                for channel in self.channels[detected_label]:

                    try:
                        detected_image = detection['image']  # numpy array
                        if self.notify(channel, detected_image):
                            self.logger.info(
                                "Notification sent on channel '%s' for %s" % 
                                (channel.get_name(), 
                                    'detection: ' + repr({
                                        'label': detection['label'],
                                        'score': detection['score']
                                    })
                                )
                            )

                    except:
                        self.logger.error(traceback.format_exc())

        self.logger.info("Stopped.")

    def stop(self):
        """
        Stops the notifier thread.
        """
        if not self.must_stop:
            self.logger.info("Stopping...")
            self.must_stop = True
        else:
            self.logger.info("Already stopped")

    def notify(self, 
               channel: AbstractChannel, 
               image: Optional[numpy.ndarray] = None) -> bool:
        """
        Sends a notification to the specified channel with attached image.

        Args:
            channel: The channel instance.
            image (numpy.ndarray): The image to be sent with the notification.

        Returns:
            A boolean indicating whether the notification was sent.
        """
        now = datetime.now()
        channel_id = str(id(channel))
        send = True
        if channel_id in self.notifications:
            last = self.notifications[channel_id]
            delta_seconds = int((now - last).total_seconds())
            if delta_seconds <= self.NOTIFY_DELAY:
                send = False
        if send:
            
            if image is not None:
                image_format = ".jpeg"
                _, buffer = cv2.imencode(image_format, image)
                image_data = buffer.tobytes()

                image_name = channel.get_name() \
                    + '-' + now.strftime("%Y-%m-%d_%H-%M-%S") + image_format
                channel.notify({'image_data': image_data, 'image_name': image_name})
            else:
                channel.notify()
                
            self.notifications[channel_id] = now
        
        return send
