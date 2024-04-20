
from pycatdetector.channels.HaGoogleSpeak import HaGoogleSpeak
from pycatdetector.channels.DiscordWebhook import DiscordWebhook
from pycatdetector.Config import Config


def test_main():
    print()
    config = Config()
    channel_name = "ha_google_speak"
    if config.get("notifiers_" + channel_name + "_enabled"):
        filtered_config = config.get_prefix("notifiers_" + channel_name)
        channel = HaGoogleSpeak(filtered_config)
        assert channel.notify("Disculpa, esto es una prueba, te quiero.")
    else:
        print("Channel not enabled, test skipped.")
        assert True

    print()
    channel_name = "discord_webhook"
    if config.get("notifiers_" + channel_name + "_enabled"):
        filtered_config = config.get_prefix("notifiers_" + channel_name)
        channel = DiscordWebhook(filtered_config)
        assert channel.notify("Disculpa, esto es una prueba, te quiero.")
