from familiar import db, cocoron

import irc.bot
import pkg_resources
import requests
import sys
import time
import traceback

CHANNEL = '#gliitchwiitch'
RATE_LIMIT_COUNT = 10
RATE_LIMIT_SECONDS = 30
BOT_NAME = 'WiitchFamiliar'
CLIENT_ID = pkg_resources.resource_string(__name__, "data/client-id.txt").decode('utf-8').strip()
OAUTH_TOKEN = pkg_resources.resource_string(__name__, "data/secret-token.txt").decode('utf-8').strip()

# People who have power for certain bot commands.
# For now, this should be a set of all-lowercase names.
#
# TODO: make sure this is unused because now we check for mods
COOL_PEOPLE = {'gliitchwiitch', 'arborelia', 'karma_dragoness', 'mus_musculus', 'jayricochet'}


COMMANDS = {
    '!addquote': 'cmd_add_quote',
    '!quoteadd': 'cmd_add_quote',
    '!q+': 'cmd_add_quote',
    '!delquote': 'cmd_del_quote',
    '!quotedel': 'cmd_del_quote',
    '!q-': 'cmd_del_quote',

    '!quote': 'cmd_get_quote',
    '!q': 'cmd_get_quote',
    '!cocoron': 'cmd_cocoron',
    '!cchar': 'cmd_cocoron_char',

    '!addmsg': 'cmd_add_message',
    '!addmessage': 'cmd_add_message',
    '!addcmd': 'cmd_add_message',
    '!addcommand': 'cmd_add_message',
    '!msg': 'cmd_add_message',
    '!message': 'cmd_add_message',
    '!cmd': 'cmd_add_message',
    '!command': 'cmd_add_message',
    '!delmsg': 'cmd_delete_message',
    '!delmessage': 'cmd_delete_message',
    '!delcmd': 'cmd_delete_message',
    '!delcommand': 'cmd_delete_message',
}


class FamiliarBot(irc.bot.SingleServerIRCBot):
    # bot infrastructure, keep scrolling for interesting methods
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = channel
        self.prev_timestamps = []

        url = f'https://api.twitch.tv/kraken/users?login={username}'
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        resp = requests.get(url, headers=headers)
        print(resp.text)
        r = resp.json()
        self.channel_id = r['users'][0]['_id']

        connect_options = [('irc.chat.twitch.tv', 6667, token)]
        super().__init__(connect_options, username, username)

    def on_welcome(self, connection, _e):
        print(f"Joining {self.channel}")
        connection.cap('REQ', ':twitch.tv/membership')
        connection.cap('REQ', ':twitch.tv/tags')
        connection.cap('REQ', ':twitch.tv/commands')
        connection.join(self.channel)
        print("Joined")

    def on_pubmsg(self, _c, event):
        """
        Handle the irc library's stupid way of reporting a message, and extract
        the Twitch-relevant info.
        """
        message = event.arguments[0]
        channel = event.target
        is_moderator = False
        is_subscriber = False
        user = '?'
        for tag in event.tags:
            if tag['key'] == 'mod' and tag['value'] == '1':
                is_moderator = True
            if tag['key'] == 'subscriber' and tag['value'] == '1':
                is_subscriber = True
            if tag['key'] == 'display-name':
                user = tag['value']
        if user == 'GliitchWiitch':
            is_moderator = True
        tags = {
            'mod': is_moderator,
            'sub': is_subscriber
        }
        self.on_message(
            channel, user, message, tags
        )

    def on_message(self, channel, user, message, tags):
        print(f"<{user}> {message}")
        if channel == CHANNEL and user != BOT_NAME:
            self.on_channel_message(
                message,
                user=user,
                tags=tags
            )

    def on_channel_message(self, message, user, tags):
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
                    method = getattr(self, method_name, None)
                    if method is None:
                        self.send("I should know how to do that, but I don't NotLikeThis")
                    else:
                        method(rest, user, tags)
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
            conn = self.connection
            conn.privmsg(self.channel, message)
            print(f"<bot> {message}")
        else:
            self.on_rate_limit()

    def on_rate_limit(self):
        print("welp, rate limited")

    def complain_no_permission(self, user):
        self.send(f"Sorry, {user}, I don't know if I should listen to you")

    # the chat commands start here!
    def cmd_add_quote(self, quote, user, tags):
        if tags['mod']:
            quote_id = db.new_row(
                "INSERT INTO quotes (quote, user, timestamp) VALUES (?, ?, datetime('now'))",
                quote,
                user
            )
            self.send(f"Added quote #{quote_id}.")
        else:
            self.complain_no_permission(user)

    def cmd_del_quote(self, number, user, tags):
        num2 = number.lstrip('#')
        try:
            rownum = int(num2)
            db.run("DELETE FROM quotes WHERE id=?", rownum)
            self.send("Deleted!")
        except ValueError:
            self.send("Uh that's not a number")

    def cmd_add_message(self, message_def, user, tags):
        if tags['mod']:
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
                self.send(f"Added command !{name}.")
            except db.IntegrityError:
                db.run("DELETE FROM commands WHERE name=?", name)
                db.new_row(
                    "INSERT INTO commands (name, response) VALUES (?, ?)",
                    name,
                    response
                )
                self.send(f"Redefined command !{name}.")
        else:
            self.complain_no_permission(user)

    def cmd_get_quote(self, query, user, tags):
        if not query:
            self._quote_random()
        else:
            try:
                query2 = query.lstrip('#')
                rownum = int(query2)
                self._quote_by_rownum(rownum)
            except ValueError:
                self._quote_by_search(query)

    def cmd_cocoron(self, query, user, tags):
        if tags['mod']:
            messages = cocoron.cocoron_rando()
            for message in messages:
                self.send(message)

    def cmd_cocoron_char(self, query, user, tags):
        if tags['mod']:
            char = cocoron.cocoron_char()
            self.send(f"Your new character is {char}.")

    def try_custom_command(self, cmd):
        rows = db.run("SELECT name, response FROM commands WHERE name=?", cmd)
        if rows:
            name, response = rows[0]
            self.send(response)
        else:
            print(f"no command named {cmd}")

    def _quote_random(self):
        quotes = db.run("""
            SELECT id, quote, user FROM quotes
            WHERE id IN (SELECT id FROM quotes ORDER BY random() LIMIT 1)
        """)
        if quotes:
            self._send_quote(quotes[0])

    def _quote_by_rownum(self, rownum):
        quotes = db.run("SELECT id, quote, user FROM quotes WHERE id=?", rownum)
        if quotes:
            self._send_quote(quotes[0])

    def _quote_by_search(self, query):
        search = f'%{query}%'
        quotes = db.run(
            "SELECT id, quote, user FROM quotes WHERE quote LIKE ? ORDER BY random()",
            search
        )
        if quotes:
            self._send_quote(quotes[0])
        else:
            self.send("I don't know that quote.")

    def _send_quote(self, row):
        id, quote, user = row
        self.send(quote)
        self.send(f'(#{id}, submitted by {user})')


def main():
    bot = FamiliarBot(BOT_NAME, CLIENT_ID, OAUTH_TOKEN, CHANNEL)
    bot.start()


if __name__ == '__main__':
    main()
