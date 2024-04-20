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

