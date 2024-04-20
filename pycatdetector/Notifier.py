import logging
import threading
import traceback
from time import sleep
from datetime import datetime


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
        self.channels = {}
        self.notifications = {}
        self.detections = detections
        self.notify_window_start = None  # string with HH:MM 24h format
        self.notify_window_end = None  # string with HH:MM 24h format

    def add_channel(self, channel, labels):
        """
        Adds a channel for the specified labels.

        Args:
            channel: The channel object.
            labels: A list of labels.
        """
        for label in labels:
            self.logger.info(
                "Adding '%s' for label '%s'" % (channel.get_name(), label)
            )
            if label not in self.channels.keys():
                self.channels[label] = [channel]
            else:
                self.channels[label].append(channel)

    def get_labels(self) -> list:
        """
        Returns the list of labels.
        """
        return self.channels.keys()

    def set_notify_window(self, start_hhmm, end_hhmm):
        """
        Sets the notification window (time frame).

        Args:
            start_hhmm: The start time of the window in HH:MM 24h format.
            end_hhmm: The end time of the window in HH:MM 24h format.
        """
        self.notify_window_start = start_hhmm
        self.notify_window_end = end_hhmm

    def is_notify_window_open(self):
        """
        Checks if the notification window is open.

        Returns:
            A boolean indicating whether the notification window is open.
        """
        if self.notify_window_start is None or self.notify_window_end is None:
            return True
        else:
            now = datetime.now()
            start = datetime.strptime(self.notify_window_start, "%H:%M")
            start = start.replace(day=now.day, month=now.month, year=now.year)
            end = datetime.strptime(self.notify_window_end, "%H:%M")
            end = end.replace(day=now.day, month=now.month, year=now.year)
            opened = start <= now <= end
            self.logger.debug(
                "Notify window: %s <= %s <= %s <=> %s" % (
                    str(start),
                    str(now),
                    str(end),
                    str(opened)
                )
            )
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

            if not self.is_notify_window_open():
                self.logger.debug(
                    "Window closed, sleeping " + str(self.queue_sleep) + "s")
                sleep(self.queue_sleep)
                continue

            self.logger.debug("Notify window is open")
            detection = self.detections.get(block=False)
            detected_label = detection['label']
            if detected_label in self.channels.keys():
                for channel in self.channels[detected_label]:
                    try:
                        if self.notify(channel):
                            self.logger.info(
                                channel.get_name() +
                                ': ' + repr(detection)
                            )
                    except:  # noqa -- flake8 skip
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

    def notify(self, channel) -> bool:
        """
        Sends a notification to the specified channel.

        Args:
            channel: The channel object.

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
            channel.notify()
            self.notifications[channel_id] = now
        return send
