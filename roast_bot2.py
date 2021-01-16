import discord
import os
import requests
import json
import random
import requests
import json

from bot_token import BOT_TOKEN
from analysis import *


discord_client = discord.Client()
azure_client = authenticate_client()


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return (quote)


@discord_client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(discord_client))


@discord_client.event
async def on_message(message):
    if message.author == discord_client.user:
        return

    if message.content.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    await message.channel.send(message.content)

    sentiment = sentiment_analysis(azure_client, message.content)

    await message.channel.send(sentiment)

discord_client.run(BOT_TOKEN)