# 1.1.3
+ Fix mxnet 1.9.1 with numpy>=1.24 error [#21165](https://github.com/apache/mxnet/issues/21165)
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

