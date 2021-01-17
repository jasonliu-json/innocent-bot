from keep_alive import keep_alive
import discord
import os
import random
import requests
import json

from bot_token import BOT_TOKEN
from average_queue import AverageQueue
from analysis import *

POSITIVE_THRESHOLD = 0.8
NEGATIVE_THRESHOLD = -0.8
NEUTRAL_THRESHOLD = 0.25

# the number of recent messages used to analyse sentiment
NUMBER_OF_RECENT_MESSAGES_KEPT = 10

# the bot will wait for this many user messages until sending another messsage
BOT_SENTIMENT_MESSAGE_COUNT = 10

POSITIVE_MESSAGE = "You seem like you're in a good mood!"
NEGATIVE_MESSAGE = "Feeling down? Want to talk about it?"
NEUTRAL_MESSAGE = ""

discord_client = discord.Client()
azure_client = authenticate_client()

"""
main program
"""



# just words test
sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]
starter_encouragements = [
  "You got this",
  "加油！",
  "Take a break, you truly deserve it!",
  'Hello friend, checking in! Stay strong, you matter! ❤️'
]

# intents dataset
with open('datasets/intents.json') as f:
  data = json.load(f)



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

    mention = message.author.mention
    msg_in = message.content.lower()
    msg_out = message.channel.send

    # remove later -- dm test
    if msg_in.startswith('$dm'):
        await msg_out('check your dm')
        await message.author.send('👋')

    # starter thing remove l8er/expand
    if msg_in.startswith('$enlighten me'):
        quote = get_quote()
        await msg_out(quote)

    for intent in data["intents"]:
        if any(word in msg_in for word in intent['patterns']):
            await msg_out(mention + " " + random.choice(intent['responses']))

    # starter
    # if any(word in msg_in for word in sad_words):
    #     await message.author.send(random.choice(starter_encouragements))

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
            await message.channel.send(mention + " " + NEGATIVE_MESSAGE)
            user_attributes[author].messages_count = 0
            random_message = random.choice(starter_encouragements)
            await message.author.send(random_message)
            print("negative")

        # positive case
        elif user_sentiment > POSITIVE_THRESHOLD:
            await message.channel.send(mention + " " + POSITIVE_MESSAGE)
            user_attributes[author].messages_count = 0
            print("positive")

        # neutral case: absolute value of the average sentiment is below the NEUTRAL_THRESHOLD
        elif abs(user_sentiment) < NEUTRAL_THRESHOLD:
            await message.channel.send(NEGATIVE_MESSAGE)
            user_attributes[author].messages_count = 0
            print("neutral")

keep_alive()
discord_client.run(BOT_TOKEN)

"""
Sentiment: positive
    Overall scores: positive=1.00; neutral=0.00; negative=0.00
"""
