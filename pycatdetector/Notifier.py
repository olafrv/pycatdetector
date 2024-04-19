import logging
import threading
import traceback
from time import sleep
from datetime import datetime


class Notifier(threading.Thread):
    detector = None
    must_stop = False
    queue_sleep = 1  # seconds, less queue polling and honor exit signals
    channels = {}
    logger = None
    notifications = {}
    detections = None
    notify_delay = 2*60  # seconds, less noise for same object detection
    notify_window_start = None  # string with HH:MM 24h format
    notify_window_end = None  # string with HH:MM 24h format

    def __init__(self, detections):
        threading.Thread.__init__(self)
        self.logger = logging.getLogger(__name__)
        self.detections = detections

    def add_channel(self, channel, labels):
        for label in labels:
            self.logger.info(
                "Adding '%s' for label '%s'" % (channel, label)
            )
            if label not in self.channels.keys():
                self.channels[label] = [channel]
            else:
                self.channels[label].append(channel)

    def get_labels(self):
        return self.channels.keys()

    def set_notify_window(self, start_hhmm, end_hhmm):
        self.notify_window_start = start_hhmm
        self.notify_window_end = end_hhmm

    def is_notify_window_open(self):
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
        if not self.must_stop:
            self.logger.info("Stopping...")
            self.must_stop = True
        else:
            self.logger.info("Already stopped")

    def notify(self, channel):
        now = datetime.now()
        channel_id = str(id(channel))
        send = True
        if channel_id in self.notifications:
            last = self.notifications[channel_id]
            delta_seconds = int((now - last).total_seconds())
            if delta_seconds <= self.notify_delay:
                send = False
        if send:
            channel.notify()
            self.notifications[channel_id] = now
        return send
