This is WiitchFamiliar, a bot for GliitchWiitch's channel!

Here are some things it can do:

    !q                  Get a random quote
    !q <number>         Get a specific quote
    !q <word>           Get a quote with a certain word in it
    !addquote <quote>   Add a quote to the database (!q+ for short)
    !addcommand <command> <response>
        (also !command or !addcmd or !message or a bunch of other things)
        If you're a mod, this defines a custom ! command that responds with
        the response you give
    !cocoron            Start a Cocoron rando, giving you a level order and a character
    !cchar              Get a new character for Cocoron rando

An example of defining a command:
    <You> !addcommand game Kat is playing some retro nonsense, idk
    <bot> Added command !game.
    <You> !game
    <bot> Kat is playing some retro nonsense, idk

You can define a command again to replace what it says.

The bot can respond to up to 10 things in 30 seconds, and after that it'll be
quiet so it doesn't get rate-limited.
