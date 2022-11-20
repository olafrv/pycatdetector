import signal
from pycatdetector.Config import Config
from pycatdetector.Recorder import Recorder
from pycatdetector.Detector import Detector
from pycatdetector.Notifier import Notifier
from pycatdetector.Screener import Screener
from pycatdetector.NeuralNet import NeuralNet
from HAGoogleSay import HAGoogleSay

images = recorder = detector = notifier = screener = None

def main():
    global images, recorder, detector, notifier, screener
    
    config = Config() # Do not log anything before loading config!
    
    signal.signal(signal.SIGINT, handler)
    recorder = Recorder(config.get("RTSP_URL"))
    detector = Detector(recorder, NeuralNet())

    if config.get("HOMEASSISTANT_ON").lower() == "yes": 
        service = HAGoogleSay(config.get_regex("^HOMEASSISTANT.*"))
    else:
        service = None
    notifier = Notifier(detector, config.get("OBJECTS"), service)

    recorder.start()
    detector.start()
    notifier.start()

    if str(config.get("HEADLESS")).lower() != "yes":
        screener = Screener(detector)
        screener.show()

    notifier.join()
    recorder.join()
    detector.join()

def handler(signum, frame):
    global recorder, detector, notifier, screener
    if not screener is None:
        screener.close()
    notifier.stop()
    recorder.stop()
    detector.stop()

if __name__ == '__main__':
    main()