import logging
from pycatdetector.channels.HaGoogleSpeak import HaGoogleSpeak
from pycatdetector.channels.DiscordWebhook import DiscordWebhook
from pycatdetector.Config import Config


def test_main(caplog):
    
    caplog.set_level(logging.DEBUG)
    print()
    config = Config()
    channel_name = "ha_google_speak"
    if config.get("notifiers_" + channel_name + "_enabled"):
        print(f"Channel '{channel_name}' enabled, running test...")
        filtered_config = config.get_prefix("notifiers_" + channel_name)
        channel = HaGoogleSpeak(filtered_config)
        assert channel.notify(custom_content={
            "message": "Esto es una prueba de sonido más larga."
        })
    else:
        print(f"Channel '{channel_name}' not enabled, test skipped.")
        assert True

    print()
    channel_name = "discord_webhook"
    if config.get("notifiers_" + channel_name + "_enabled"):
        print(f"Channel '{channel_name}' enabled, running test...")
        filtered_config = config.get_prefix("notifiers_" + channel_name)
        channel = DiscordWebhook(filtered_config)
        assert channel.notify(
            custom_content={
                "message": "Esto es una prueba a través de chat.",
                "image_name": "test_image.jpg",
                "image_data": open("cookie.jpg", "rb").read()
            }
        )
    else:
        print(f"Channel '{channel_name}' not enabled, test skipped.")
        assert True