import logging
import threading
import traceback
from time import sleep
from datetime import datetime


class Notifier(threading.Thread):
    detector = None
    must_stop = False
    sleep_time = 1  # seconds
    channels = {}
    logger = None
    notifications = {}
    delay_seconds = 2*60

    def __init__(self, detector):
        threading.Thread.__init__(self)
        self.detector = detector
        self.logger = logging.getLogger(__name__)

    def add_channel(self, channel, labels):
        for label in labels:
            self.logger.info(
                "Adding '%s' for label '%s'" % (channel, label)
            )
            if label not in self.channels.keys():
                self.channels[label] = [channel]
            else:
                self.channels[label].append(channel)

    def run(self):
        self.logger.info(
            "Starting with Thread ID: %s" % (threading.get_native_id())
        )

        detections = self.detector.get_detections()
        while (not self.must_stop):
            if not detections.empty():
                detection = detections.get(block=False)
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
            else:
                self.logger.debug(
                    "Sleeping "+str(self.sleep_time) +
                    "s due to empty queue..."
                )
                # Better sleep than not answering signals
                sleep(self.sleep_time)

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
            if delta_seconds <= self.delay_seconds:
                send = False
        if send:
            channel.notify()
            self.notifications[channel_id] = now
        return send
