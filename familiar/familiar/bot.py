import familiar.db as db

from python_twitch_irc import TwitchIrc
import pkg_resources
import sys
import time
import traceback

CHANNEL = '#gliitchwiitch'
RATE_LIMIT_COUNT = 10
RATE_LIMIT_SECONDS = 30
BOT_NAME = 'WiitchFamiliar'
OAUTH_TOKEN = pkg_resources.resource_string(__name__, "data/secret-token.txt")

# People who have power for certain bot commands.
# For now, this should be a set of all-lowercase names.
# TODO: check if they're a mod instead.
COOL_PEOPLE = {'gliitchwiitch', 'arborelia', 'karma_dragoness', 'mus_musculus', 'jayricochet'}


COMMANDS = {
    '!addquote': 'cmd_add_quote',
    '!quoteadd': 'cmd_add_quote',
    '!q+': 'cmd_add_quote',
    '!quote': 'cmd_get_quote',
    '!q': 'cmd_get_quote',
    '!cocoron': 'cmd_random_cocoron',
    '!addmsg': 'cmd_add_message',
    '!addmessage': 'cmd_add_message',
    '!delmsg': 'cmd_delete_message',
    '!delmessage': 'cmd_delete_message',
}


class FamiliarBot(TwitchIrc):
    # bot infrastructure, keep scrolling for interesting methods
    def __init__(self, *args):
        self.prev_timestamps = []
        super().__init__(*args)

    def on_connect(self):
         self.join(CHANNEL)

    def on_message(self, timestamp, tags, channel, user, message):
        if channel == CHANNEL and user != BOT_NAME:
            self.on_channel_message(
                message,
                user=user,
            )

    def on_channel_message(self, message, user):
        """
        What should happen when a chat message appears in the channel (and it
        isn't from this bot).
        """
        if user == BOT_NAME:
            return
        message = message.strip()
        if message:
            try:
                cmd, _, rest = message.partition(" ")
                if cmd in COMMANDS:
                    method_name = COMMANDS[cmd]
                    method = getattr(self, method_name, default=None)
                    if method is None:
                        self.send("I should know how to do that, but I don't NotLikeThis")
                    else:
                        method(rest, user)
                elif cmd.startswith('!'):
                    self.try_custom_command(cmd[1:])
            except Exception as e:
                traceback.print_exc()
                error_type, error_value = sys.exc_info()[:2]
                self.send(f"{error_type}: {error_value}")

    def send(self, message):
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
        print("welp, rate limited")

    def is_power_user(self, user):
        return user.lower() in COOL_PEOPLE

    def complain_no_permission(self, user):
        self.send(f"Sorry, {user}, I don't believe you")

    # the chat commands start here!
    def cmd_add_quote(self, quote, user):
        quote_id = db.new_row(
            "INSERT INTO quotes (quote, user, timestamp) VALUES (?, ?, datetime('now'))",
            quote,
            user
        )
        self.send(f"Added quote #{quote_id}.")
    
    def cmd_add_message(self, message_def, user):
        if self.is_power_user(user):
            if ' ' not in message_def:
                self.send("Tell me what the response to that command should be.")
                return
            name, response = message_def.split(' ', 1)
            name = name.lstrip('!')
            try:
                db.new_row(
                    "INSERT INTO commands (name, response) VALUES (?, ?)",
                    name,
                    response
                )
                self.send("Added command !{name}.")
            except db.IntegrityError:
                self.send("That command already exists.")
        else:
            self.complain_no_permission(user)
    
    def cmd_get_quote(self, query, user):
        if not query:
            self._quote_random()
        else:
            try:
                rownum = int(query)
                self._quote_by_rownum(rownum)
            except ValueError:
                self._quote_by_search(query)
    
    def try_custom_command(self, cmd):
        row = db.run("SELECT (name, response) FROM commands WHERE name=?", cmd)
        if row:
            name, response = row
            self.send(response)

    def _quote_random(self):
        quotes = db.run("""
            SELECT (id, quote, user) FROM quotes
            WHERE id IN (SELECT id FROM table ORDER BY random() LIMIT 1)
        """)
        if quotes:
            self._send_quote(quotes[0])

    def _quote_by_rownum(self, rownum):
        quotes = db.run("SELECT (id, quote, user) FROM quotes WHERE id=?", rownum)
        if quotes:
            self._send_quote(quotes[0])
    
    def _quote_by_search(self, query):
        search = f'%{query}%'
        quotes = db.run("SELECT (id, quote, user) FROM quotes WHERE id=?", rownum)
        if quotes:
            self._send_quote(quotes[0])

    def _send_quote(self, row):
        id, quote, user = row
        self.send(f'"{quote}"')
        self.send(f'(#{id}, submitted by {user})')
    

def main():
    client = FamiliarBot(BOT_NAME, OAUTH_TOKEN).start()
    client.handle_forever()


if __name__ == '__main__':
    main()
