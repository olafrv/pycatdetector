#!/usr/bin/env bash

# Used for debugging OpenCV issues with versions upgrade
# Uncomment the following lines to enable detailed OpenCV logging
# See also Recorder.py for more OpenCV debugging options
# https://github.com/opencv/opencv/issues/27091 (Bug)
# export OPENCV_LOG_LEVEL=DEBUG
# export OPENCV_VIDEOIO_DEBUG=1

# Entrypoint script for PyCatDetector Docker container
python3 -c "from pycatdetector.Preloader import preload; preload()" \
    && python3 main.py