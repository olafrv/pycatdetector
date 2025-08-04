import cv2
import threading
from time import sleep
from queue import SimpleQueue
import logging
from urllib.parse import urlparse


class Recorder (threading.Thread):

    RECONNECT_DELAY = 10  # seconds
    CORRUPTED_DELAY = 1
    CORRUPTED_MAX_FRAMES = 60  # max corrupted frames (1 frame <=> 1 sec)
    must_stop = False

    def __init__(self, rtspUrl):
        threading.Thread.__init__(self)
        self.rtspUrl = rtspUrl
        self.logger = logging.getLogger(__name__)
        self.images = SimpleQueue()

    def get_images(self):
        return self.images

    def run(self):
        self.logger.info(
            "Starting with Thread ID: %s" % (threading.get_native_id())
        )
        self.record()
        self.logger.info("Stopped.")

    def stop(self):
        if not self.must_stop:
            self.logger.info("Stopping...")
            self.must_stop = True
        else:
            self.logger.info("Already stopped.")

    def _mask_url(self, url) -> str:
        parsed = urlparse(url)
        # 'https://user:???@example.com/path?key=value#hash'
        replaced = parsed._replace(
            netloc="{}:{}@{}".format(parsed.username, "???", parsed.hostname)
        )
        return replaced.geturl()

    def record(self, greyscale=False, showVisor=False, saveImage=False):

        # Used for debugging OpenCV issues with versions upgrade
        # Uncomment the following lines to enable detailed OpenCV logging
        # https://github.com/opencv/opencv/issues/27091 (Bug)
        #
        # See Dockerfile for activating global OpenCV logging:
        # export OPENCV_LOG_LEVEL=DEBUG
        # export OPENCV_VIDEOIO_DEBUG=1
        #
        # Alternative, here set the OpenCV log level to debug:
        # cv2.setLogLevel(5) # Set OpenCV log level to debug

        while (not self.must_stop):
            conn_error = False

            cap = cv2.VideoCapture(self.rtspUrl, cv2.CAP_FFMPEG)
            
            # Set buffer size and timeout properties to prevent stream timeout
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer to avoid lag
            cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 15000)  # 15 second open timeout
            cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000)    # 5 second read timeout
            
            # Additional RTSP optimizations
            cap.set(cv2.CAP_PROP_FPS, 30)  # Try to set target FPS
            
            if not cap.isOpened():
                self.logger.error(
                    "Connection error to: " + self._mask_url(self.rtspUrl)
                )
                conn_error = True
            else:
                # Log connection success and actual stream properties
                fps = cap.get(cv2.CAP_PROP_FPS)
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                self.logger.info(
                    "Connected successfully. Resolution: %dx%d, Reported FPS: %.1f" 
                    % (width, height, fps)
                )
                reads = 0
                total_reads = 0
                total_writes = 0
                corrupted_count = 0
                frames_to_skip = fps-1
                
                self.logger.info("Connected. FPS: %i, SKIP: %i"
                                 % (fps, frames_to_skip))

                

                while (not self.must_stop):
                    try:
                        ret, frame = cap.read()  # return numpy.array
                        reads += 1
                        total_reads += 1
                        
                        # Check if read was successful
                        if not ret:
                            self.logger.warning("Failed to read frame from stream")
                            corrupted_count += 1
                            if corrupted_count > self.CORRUPTED_MAX_FRAMES:
                                self.logger.error("Too many failed reads, reconnecting...")
                                break
                            continue
                            
                        corrupted = frame is None or len(frame.shape) != 3
                    except Exception as e:
                        self.logger.error("Error reading frame: %s" % (e))
                        break  # Exit inner loop to reconnect

                    if corrupted:
                        corrupted_count += 1
                        if corrupted_count > self.CORRUPTED_MAX_FRAMES:
                            self.logger.error(
                                "Reached max amount of corrupted frames." +
                                " Shape: " +
                                str(frame.shape if frame is not None else "-")
                            )
                            break    # retry conn
                        else:
                            self.logger.warn(
                                "Bad: %i/%i, R: %i, W: %i, Q: %i" %
                                (corrupted_count, self.CORRUPTED_MAX_FRAMES,
                                 total_reads, total_writes,
                                 self.images.qsize())
                            )
                            continue  # skip frame
                    else:
                        corrupted_count = 0  # reset counter

                        if reads % frames_to_skip == 0:
                            if greyscale:
                                frame = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                            if saveImage:
                                cv2.imwrite(
                                    'recording/opencv/imgx-' +
                                    str(total_reads) + '.jpg',
                                    frame
                                )
                            if showVisor:
                                cv2.imshow('frame', frame)
                                if cv2.waitKey(1) & 0xFF == ord('q'):
                                    break

                            reads = 0
                            total_writes += 1
                            self.images.put(frame)
                            self.logger.debug(
                                "Bad: %i/%i, R: %i, W: %i, Q: %i" %
                                (corrupted_count, self.CORRUPTED_MAX_FRAMES,
                                 total_reads, total_writes,
                                 self.images.qsize())
                            )

            cap.release()
            if showVisor:
                cv2.destroyAllWindows()

            if conn_error:
                self.logger.info(
                    "Retrying in " + str(self.RECONNECT_DELAY) + " seconds ..."
                )
                sleep(self.RECONNECT_DELAY)
