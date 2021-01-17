import discord
import os
import random
import requests
import json

from bot_token import BOT_TOKEN
from average_queue import AverageQueue
from analysis import *

POSITIVE_THRESHOLD = 0.5
NEGATIVE_THRESHOLD = -0.5
NEUTRAL_THRESHOLD = 0.25

# the number of recent messages used to analyse sentiment
NUMBER_OF_RECENT_MESSAGES_KEPT = 5

# the bot will wait for this many user messages until sending another messsage
BOT_SENTIMENT_MESSAGE_COUNT = 5

POSITIVE_MESSAGE = "happy!"
NEGATIVE_MESSAGE = "r u ok lol?"
NEUTRAL_MESSAGE = ""

discord_client = discord.Client()
azure_client = authenticate_client()

"""
main program
"""


class Attributes:
    def __init__(self):
        self.messages_count = 0
        self.recent_sentiment = AverageQueue(NUMBER_OF_RECENT_MESSAGES_KEPT)


# average_queue efficiently maintains a queue of the 5 most
# recent sentiment values

user_attributes = {}
# attributes = Attributes()
# attributes.recent_sentiment = AverageQueue(NUMBER_OF_RECENT_MESSAGES_KEPT)



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

    author = message.author
    print(message.author)

    if not author in user_attributes:
        user_attributes[author] = Attributes()

    if message.content.startswith('$inspire'):
        quote = get_quote()
        await message.channel.send(quote)

    # increment counter for the number of user messages since the last bot message
    user_attributes[author].messages_count += 1

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
    user_attributes[author].recent_sentiment.add(overall_score)

    print(sentiment)
    print(overall_score)


    user_sentiment = user_attributes[author].recent_sentiment.average()
    print(user_attributes[author].recent_sentiment.average())


    # for the bot to send a message, the bot must wait until BOT_SENTIMENT_MESSAGE_COUNT
    # number of messages have been sent by users since the last bot message, and that
    # the recent sentiment queue is filled (to have a more accurate evaluation of sentiment


    if user_attributes[author].messages_count >= BOT_SENTIMENT_MESSAGE_COUNT \
            and user_attributes[author].recent_sentiment.length == user_attributes[author].recent_sentiment.size:

        # 3 cases regarding the most recent messages. once the queue is filled.

        # negative case: the average sentiment of the recent messages surpass the NEGATIVE_THRESHOLD
        if user_sentiment < NEGATIVE_THRESHOLD:
            await message.channel.send(NEGATIVE_MESSAGE)
            user_attributes[author].messages_count = 0
            print("negative")
            # dm message.author

        # positive case
        elif user_sentiment > POSITIVE_THRESHOLD:
            await message.channel.send(POSITIVE_MESSAGE)
            user_attributes[author].messages_count = 0
            print("positive")

        # neutral case: absolute value of the average sentiment is below the NEUTRAL_THRESHOLD
        elif abs(user_sentiment) < NEUTRAL_THRESHOLD:
            await message.channel.send(NEGATIVE_MESSAGE)
            user_attributes[author].messages_count = 0
            print("neutral")



discord_client.run(BOT_TOKEN)

"""
Sentiment: positive
    Overall scores: positive=1.00; neutral=0.00; negative=0.00
"""
