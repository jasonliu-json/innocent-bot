import discord
import os
import requests
import json
import random

from bot_token import BOT_TOKEN
from average_queue import AverageQueue
from analysis import *

POSITIVE_THRESHOLD = 0.5
NEGATIVE_THRESHOLD = -0.5
NEUTRAL_THRESHOLD = 0.25
NUMBER_OF_RECENT_MESSAGES_KEPT = 10

# the bot will wait for this many user messages until sending another messsage
BOT_SENTIMENT_MESSAGE_COUNT = 10

POSITIVE_MESSAGE = "happy!"
NEGATIVE_MESSAGE = "r u ok lol?"
NEUTRAL_MESSAGE = ""

discord_client = discord.Client()
azure_client = authenticate_client()



"""
main program
"""

class Bot:

    def __init__(self):
        # average_queue efficiently maintains a queue of the 5 most
        # recent sentiment values
        self.recent_messages_sentiment = AverageQueue(NUMBER_OF_RECENT_MESSAGES_KEPT)
        self.messages_count = 0

    def get_quote(self):
        response = requests.get("https://zenquotes.io/api/random")
        json_data = json.loads(response.text)
        quote = json_data[0]['q'] + " -" + json_data[0]['a']
        return (quote)


    @discord_client.event
    async def on_ready(self):
        print('We have logged in as {0.user}'.format(discord_client))


    @discord_client.event
    async def on_message(self, message):
        if message.author == discord_client.user:
            return

        if message.content.startswith('$inspire'):
            quote = self.get_quote()
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
        self.recent_messages_sentiment.add(overall_score)

        print(sentiment)
        print(overall_score)

        print(self.recent_messages_sentiment.average())

        # 3 cases regarding the most recent messages. once the queue is filled.
        if self.recent_messages_sentiment.length == self.recent_messages_sentiment.size:

            # negative case: the average sentiment of the recent messages surpass the NEGATIVE_THRESHOLD
            if self.recent_messages_sentiment.average() < NEGATIVE_THRESHOLD:
                await message.channel.send(NEGATIVE_MESSAGE)
                print("negative")

            # positive case
            elif self.recent_messages_sentiment.average() > POSITIVE_THRESHOLD:
                await message.channel.send(POSITIVE_MESSAGE)
                print("positive")

            # neutral case: absolute value of the average sentiment is below the NEUTRAL_THRESHOLD
            elif abs(self.recent_messages_sentiment.average()) < NEUTRAL_THRESHOLD:
                await message.channel.send(NEGATIVE_MESSAGE)
                print("neutral")



    discord_client.run(BOT_TOKEN)


b = Bot()
"""
Sentiment: positive
    Overall scores: positive=1.00; neutral=0.00; negative=0.00
"""