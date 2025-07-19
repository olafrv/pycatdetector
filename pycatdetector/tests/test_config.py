import logging
from pycatdetector.Config import Config


def test_main(caplog):
    
    caplog.set_level(logging.DEBUG)
    print()
    config = Config()
    json = config.to_json()
    print(json)
    assert isinstance(json, str)
