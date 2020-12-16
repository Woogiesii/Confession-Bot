# Confession-Bot


### How to Run

You will need to setup a bot on your server before continuing, follow the directions [here](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token). Following this, you should have your bot appearing in your server and you should have the Discord bot token. Finally, go to the `Bot` settings in your App's Developer Portal (in the same page where you copied your Bot Token) and enable the `Server Members Intent`.

Create a new file `.env` by copying from `.env_template`.

```bash
cp .env_template .env
```

Fill in appropriate variables in new `.env` file.

#### .env Variables

- **DISCORD_TOKEN**: The Discord Bot Token for your bot.
- **TENOR_API_KEY**: Your Tenor API key. Get one from [here](https://tenor.com/developer/keyregistration)

To run the bot:

```bash
python bot.py
```
