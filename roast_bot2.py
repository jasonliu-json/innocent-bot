import discord
import os
import requests
import json
import random
import requests
import json

from bot_token import BOT_TOKEN
from average_queue import AverageQueue
from analysis import *

POSITIVE_THRESHOLD = 0.5
NEGATIVE_THRESHOLD = -0.5
NEUTRAL_THRESHOLD = 0.25
NUMBER_OF_RECENT_MESSAGES_KEPT = 5

discord_client = discord.Client()
azure_client = authenticate_client()

# average_queue efficiently maintains a queue of the 5 most
# recent sentiment values
recent_messages_sentiment = AverageQueue(NUMBER_OF_RECENT_MESSAGES_KEPT)


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

    # await message.channel.send(message.content)

    print(message.content)

    # call sentiment analysis API to retrieve information.
    # sentiment: string summary
    # positive score: confidence level from 0 to 1 on the text having positive sentiment.
    # neutral score: similar
    # negative score: similar
    sentiment, positive_score, neutral_score, negative_score = sentiment_analysis(azure_client, message.content)

    # for now the way we calculate score is just positive score minus negative score. idk maybe there's a
    # better algorithm later lol.

    overall_score = positive_score - negative_score

    # average_sentiment is a queue that efficiently maintains the average sentiment of the 5 most recent messages.
    recent_messages_sentiment.add(overall_score)

    print(sentiment)
    print(overall_score)

    print(recent_messages_sentiment.average())

    # 3 cases regarding the most recent messages. once the queue is filled.
    if recent_messages_sentiment.length == recent_messages_sentiment.size:

        # negative case: the average sentiment of the recent messages surpass the NEGATIVE_THRESHOLD
        if recent_messages_sentiment.average() < NEGATIVE_THRESHOLD:

            print("negative")

        # positive case
        elif recent_messages_sentiment.average() > POSITIVE_THRESHOLD:
            print("positive")

        # neutral case: absolute value of the average sentiment is below the NEUTRAL_THRESHOLD
        elif abs(recent_messages_sentiment.average()) < NEUTRAL_THRESHOLD:
            print("neutral")




discord_client.run(BOT_TOKEN)


"""
Sentiment: positive
    Overall scores: positive=1.00; neutral=0.00; negative=0.00
"""