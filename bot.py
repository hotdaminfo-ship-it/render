import logging
import os

import aiohttp
import discord

logging.basicConfig(level=logging.INFO)

ZAPIER_WEBHOOK_URL = os.getenv("ZAPIER_WEBHOOK_URL", "NOT_SET")
CHANNEL_NAME = os.getenv("CHANNEL_NAME", "sme-room")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    logging.info("Bot connected as %s", client.user)


@client.event
async def on_message(message):
    if message.author.bot or message.guild is None:
        return

    if message.channel.name != CHANNEL_NAME:
        return

    if client.user not in message.mentions:
        return

    payload = {
        "message_content": message.content,
        "author": message.author.display_name,
        "channel": message.channel.name,
        "channel_id": str(message.channel.id),
        "message_id": str(message.id),
    }

    timeout = aiohttp.ClientTimeout(total=15)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(ZAPIER_WEBHOOK_URL, json=payload) as response:
                response.raise_for_status()
        logging.info("Forwarded message %s to Zapier", message.id)
    except Exception:
        logging.exception("Could not forward message to Zapier")


token = os.getenv("DISCORD_TOKEN", "").strip()

logging.info("Discord token variable exists: %s", bool(token))
logging.info("Discord token length: %s", len(token))
logging.info("Discord token has whitespace: %s", token != token.strip() if token else False)

if not token:
    raise RuntimeError("DISCORD_TOKEN is missing or empty!")

client.run(token)
