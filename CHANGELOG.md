# 1.2.1

* Bug: Fixed missing notification window configuration in `config.example.yaml`
* Blinkstick Square Channel: https://github.com/olafrv/pycatdetector/issues/2
* Added black for code formatting

# 1.2.0

* Infrastructure & Dependencies
  * Updated Docker base image from Ubuntu 22.04 → 24.04
  * Updated Python version from 3.10 → 3.12
  * Updated NumPy from 1.23 → 2.2.6 (compatible with OpenCV)
  * Updated OpenCV from 4.10.0.82 → 4.12.0.88 (latest with NumPy 2.x support)
  * Updated PyTorch from 2.2.2+cpu → 2.7.1 and torchvision 0.17.2+cpu → 0.22.1
  * Updated colorlog from 6.9.0 → 6.8.2
  * Added discord-webhook 1.4.1 dependency
* Neural Network Migration
  * Deprecated Apache MXNet support 
    https://github.com/olafrv/pycatdetector/issues/6
  * Switched to PyTorch-only neural network implementation
  * Updated model preloading to only use PyTorch models
  * Added error handling for unsupported MXNet usage
  * Removed Preloader class and MXNet-specific code
* RTSP Stream Improvements
  * Enhanced connection handling with explicit FFmpeg backend usage
  * Added timeout configurations (15s open, 5s read timeouts)
  * Improved stream optimization with H.264 codec preference and buffer management
  * Better error handling for failed frame reads and connection timeouts
  * Enhanced logging of stream properties (resolution, FPS)
* Notification System Enhancements
  * Implemented abstract Channel class for better code organization
  * Enhanced Channel with image attachment using discord-webhook library
  * Updated Home Assistant Google Speak channel with improved API calls
  * Added image data support in notification system with automatic encoding
  * Renamed configuration parameter from "content" → "message" for consistency
  * Added images with boxes, labels and scores to messages for better visibility
* Application Architecture
  * Enhanced Docker configuration with torch models volume mounting
  * Decided for no entrypoint.sh for initialization of model preloading
  * Enhanced screener with TkAgg backend fallback for headless environments
* Configuration & Documentation
  * Enhanced Docker installation documentation
  * Updated example configuration with new parameter names
  * Updated changelog with comprehensive version history (this one)
  * Improved Makefile with better Docker handling and volume mounting
  * Added support for multiple notification windows per channel
  * Removed configuration flattening for easy config reading
* Bug Fixes & Stability
  * A lot of Pylance type checks and prototype fixes
  * Fixed NumPy 2.x compatibility issues with OpenCV
  * Resolved dependency conflicts between packages in requirements.txt
  * Improved detection data structure with proper image and timestamp handling
  * Enhanced error handling for missing TkAgg backend in headless mode
  * Fixed channel loading to skip abstract base classes
  * Resurrected commented code on Recorder for debugging OpenCV issues
  * Refactor Encoder class methods for improved video writer handling
  
# 1.1.12

* Fixed Dockerfile ENV definitions.
* Eliminated credential printing for docker login.
* Switched to custom centralized docker installer.

# 1.1.11

* Reduced maximum corrupted frames counts.
* Added statistics about corrupted frames.

# 1.1.10

* Moved preload to Preloader helper.

# 1.1.9

* Shortener an reduced DEBUG log messages.
* Added test cases for notification channels.
* Decoupled all but screener constructor (with queues).
* Added support for multiple notification time windows.
* Fixed a lot of linting flake and PEP recommendations.
* Added docstrings to all classes and methods.

# 1.1.8

* Added support in Makefile to check for outdated dependencies.
* Improved docker build time to few seconds seconds (with cache).
* Fixed PyTorch download speed with '--find-link' (requirements.txt).
* Updated references, legacy notices and improvement to README.
* Available PyTorch object detections models are heavier (memory).
* Removed log producer full path to shorten DEBUG log messages.
* Added Detector variable sleep time based on analysis speed.
* Create an encoder to be allowed to save video files from boxed images.
* Renamed some variables, classes and methods for better readability.
* Started to create a PoC to migrate from MXNet to PyTorch.
* Bumped serveral dependencies to latest versions.

# 1.1.7

* Switched docker single run to be tty interactive.
* Added suppport for one time window for notifications.

# 1.1.6

* Added missing dependencies for venv installation.
* Improved Makefile regarding docker compose usage.
* Check speed/scores with different RTSP cameras, CPUs and resolutions.
* Started to fix linting issues related to 'flake8', 'pylint' and 'pylance'
* Added PoC for Home Assistant new Google Tranlate / Speak services integration.

# 1.1.5

* Switched from restnet to mobilenet for object detection (faster/smaller).
* Tried but ditched ARM builds for Apache MXNet (too many issues).
* Remove deprecated 'version' key in 'docker-compose.yaml'.
* Added docker installation shell script.

# 1.1.4

* Added METADATA support in Makefile to easy release versioning.
* Added missing binary tk, pil and ffmepeg dependencies (make run).
* Small Makefile improvements related to venv.

# 1.1.3
* Added support for different timezones
* Added IoT optimization (mobile mxnet models)
* Added missing fresh install hints/packages (make, pip3)
* Fix memory leak when screener is not used (headless)
* Fix mxnet 1.9.1 with numpy>=1.24 error [#21165](https://github.com/apache/mxnet/issues/21165)
* Add better logging inside channels/*.py classes.
* Add hints on documentation about Notifiers/Channels configurations.
* Fix missing HomeAssistant service endpoint URL for Google TTS service.
* Fix GUI crash when X11 display forward (python3-pil.imagetk + mathplotlib/TkAgg)
* Ensure container is always restarted even if stopped manually

# 1.1.2
* Added CHANGELOG.md
* Added flake as defaut linter.
* [Linting](https://code.visualstudio.com/docs/python/linting) code fixes.
* Readded .vscode with dev config.
* Fix not honoring 'headless' config.
* Ensure multiple instance of the same channel class in Notifer.py
* Ensure container is auto restarted in docker compose.

# 1.1.1
* First release

