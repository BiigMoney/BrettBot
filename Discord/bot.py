import discord
from discord.ext import commands, tasks
import os
from xml.etree import ElementTree
import json
import glob

client = commands.Bot(command_prefix = '-', case_insensitive=True)

@tasks.loop(minutes=1440.0)
async def called_once_a_min():
    clone()

@called_once_a_min.before_loop
async def before():
    await client.wait_until_ready()

@client.event
async def on_ready():
    called_once_a_min.start()
    print('Bot is ready.')


@client.event
async def on_message(message):
    if message.content.startswith('==') and message.content.endswith('=='):
        dom = ElementTree.parse("../../Brett stuff/TumbledMTG-Cockatrice/TumbledMTG/data/customsets/tumbled-mtg-cards.xml")
        cardname = message.content[2:-2]
        cards = dom.find('cards')
        cards = cards.findall('card')
        for c in cards:
            title = c.find('name').text
            if cardname.lower() in title.lower():
                cardfile = "../../Brett stuff/TumbledMTG-Cockatrice/TumbledMTG/data/pics/CUSTOM/"
                cardfile += title
                cardfile += ".jpg"
                await message.channel.send(file=discord.File(cardfile))
                return
        await message.channel.send("Could not find card.")
    await client.process_commands(message)

@client.command()
@commands.has_permissions(administrator=True)
async def update(ctx):
    clone()
    await ctx.send("Updated.")

def clone():
    dir = os.getcwd()
    os.chdir('../../Brett stuff/TumbledMTG-Cockatrice')
    os.system("git pull")
    os.chdir(dir)


token = ""
with open('config.json', 'r') as file:
    data = file.read()
    file_dict = json.loads(data)
    token = file_dict["token"]
client.run(token)
