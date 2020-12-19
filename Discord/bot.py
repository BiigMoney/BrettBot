import discord
from discord.ext import commands, tasks
import os
from xml.etree import ElementTree
import json

client = commands.Bot(command_prefix = '!', case_insensitive=True)

@client.event
async def on_ready():
    print('Bot is ready.')


@client.event
async def on_message(message):
    if message.content.startswith('==') and message.content.endswith('=='):
        cardname = message.content[2:-2]
        cards = dom.find('cards')
        cards = cards.findall('card')
        for c in cards:
            title = c.find('name').text
            if cardname.lower() in title.lower():
                cardfile = "CUSTOM/"
                cardfile += title
                cardfile += ".jpg"
                await message.channel.send(file=discord.File(cardfile))
                return
        await message.channel.send("Could not find card")

token = ""
with open('config.json', 'r') as file:
    data = file.read()
    file_dict = json.loads(data)
    token = file_dict["token"]
dom = ElementTree.parse("tumbled-mtg-cards.xml")
client.run(token)
