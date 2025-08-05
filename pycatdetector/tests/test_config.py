import logging
from pycatdetector.Config import Config


def test_main(caplog):

    caplog.set_level(logging.DEBUG)
    config = Config().get_dict()
    root_keys = config.keys()
    print()
    print("Checking mandatory keys...")
    print(root_keys)
    for key in [
        "log_tty",
        "log_dir",
        "log_level",
        "rtsp_url",
        "headless",
        "net_model_name",
        "notify_min_score",
        "videos_folder",
        "notifiers",
    ]:
        assert (
            key in root_keys
        ), f"Mandatory key '{key}' not found in root configuration"
