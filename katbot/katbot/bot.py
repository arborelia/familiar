from .db import BotDB

from python_twitch_irc import TwitchIrc
import pkg_resources
import time

CHANNEL = '#gliitchwiitch'
RATE_LIMIT_COUNT = 10
RATE_LIMIT_SECONDS = 30
BOT_NAME = 'WiitchsFamiliar'
OAUTH_TOKEN = pkg_resources.resource_string("secret-token.txt")

COMMANDS = {
    '!addquote': 'cmd_add_quote',
    '!quoteadd': 'cmd_add_quote',
    '!q+': 'cmd_add_quote',
    '!quote': 'cmd_random_quote',
    '!q': 'cmd_random_quote',
    '!cocoron': 'cmd_random_cocoron',
    '!addmsg': 'cmd_add_message',
    '!addmessage': 'cmd_add_message',
    '!delmsg': 'cmd_delete_message',
    '!delmessage': 'cmd_delete_message',
}


class FamiliarBot(TwitchIrc):
    def __init__(self, *args):
        self.prev_timestamps = []
        self.db = BotDB()
        super().__init__(*args)

    def on_connect(self):
         self.join(CHANNEL)

    def on_message(self, timestamp, tags, channel, user, message):
        if channel == CHANNEL and user != BOT_NAME:
            self.on_channel_message(
                message,
                timestamp=timestamp,
                user=user,
            )

    def on_channel_message(self, message, timestamp, user):
        """
        What should happen when a chat message appears in the channel (and it
        isn't from this bot).
        """
        if 

    def safe_send(self, message):
        """
        Send a message to the channel, unless this would go over the rate limit
        configured above.
        """
        current_time = time.monotonic()
        while self.prev_timestamps:
            if self.prev_timestamps[0] < current_time - RATE_LIMIT_SECONDS:
                self.prev_timestamps = self.prev_timestamps[1:]
            else:
                break
        
        if len(self.prev_timestamps) < RATE_LIMIT_COUNT:
            self.message(CHANNEL, message)
        else:
            self.on_rate_limit()
    
    def on_rate_limit(self):
        print("welp rate limited")

            

client = FamiliarBot(BOT_NAME, 'MyTwitchOAuthToken').start()
client.handle_forever()

