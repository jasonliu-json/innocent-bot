import discord
import requests
import json
import random

# import nltk
# from nltk.stem.lancaster import LancasterStemmer
# stemmer = LancasterStemmer()

# import numpy
# import tflearn
# import tensorflow

from bot_token import BOT_TOKEN

client = discord.Client()

# just words
sad_words = ["sad", "depressed", "unhappy", "angry", "miserable"]
starter_encouragements = [
  "You got this",
  "加油！",
  "Take a break, you truly deserve it!"
]

# intents dataset
with open('datasets/intents.json') as f:
  data = json.load(f)

### --------------------------------------------- nvm

# words = []
# labels = []
# docs_x = []
# docs_y = []

# # get root of word
# for intent in data["intents"]:
#     for pattern in intent['patterns']:
#         wrds = nltk.word_tokenize(pattern)
#         words.extend(wrds)
#         docs_x.append(pattern)
#         docs_x.append(intent["tag"])

#         if intent["tag"] not in labels:
#             labels.append(intent["tag"])

# words = [stemmer.stem(w.lower()) for w in words]
# words = sorted(List(set(words)))

# labels = sorted(labels)

# training = []
# output = []

# out_empty = [0 for _ in range(len(classes))]

# for x, doc in enumerate(docs_x):
#     bag = []
#     wrds = [stemmer.stem(w) for w in doc]
#     for w in words:
#         if w in wrds:
#             bag.append(1)
#         else:
#             bag.append(0)

# output_row = out_empty[:]
# output_row[labels.index(docs_y[x]) = 1

### ---------------------------------------------

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

@client.event
async def on_ready():
    print('The SUPER {0.user} is online'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    mention = message.author.mention
    msg_in = message.content.lower()
    msg_out = message.channel.send

    # remove later -- dm test
    if msg_in.startswith('$dm'):
        await message.author.send('👋')  
    
    # starter thing remove l8er/expand
    if msg_in.startswith('$enlighten me'):
        quote = get_quote()
        await msg_out(quote)
    
    for intent in data["intents"]:
        if any(word in msg_in for word in intent['patterns']):
            await msg_out(mention + " " + random.choice(intent['responses']))

    # if any(word in msg for word in sad_words):
    #     await message.channel.send(random.choice(starter_encouragements))

client.run(BOT_TOKEN)