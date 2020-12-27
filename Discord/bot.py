import discord
from discord.ext import commands, tasks
import os
from xml.etree import ElementTree
import json
import glob
import re

client = commands.Bot(command_prefix = '-', case_insensitive=True)
validKeyWords=["cmc","o","t","c","-o"]
valueKeyWords = ["cmc"]


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
    if message.author == client.user:
        return
    matches = re.findall('{\(.*?\)\}',message.content)
    if len(matches) >= 10:
        await message.channel.send("Relax.")
        return
    for x in matches:
        count = 0
        founds = ""
        cardname = x[2:-2]
        words = cardname.split()
        keywords = []
        values = []
        searchwords = []
        for word in words:
            if not ":" in word:
                searchwords.append(word)
            else:
                halfs = word.split(":")
                keywords.append(halfs[0])
                values.append(halfs[1])
        for keyword in keywords:
            if not keyword in validKeyWords:
                del values[keywords.index(keyword)]
                keywords.remove(keyword)
        for c in cards:
            lol = True
            title = c.find('name').text
            for word in searchwords:
                if word.lower() not in title.lower():
                    lol = False
            if not lol:
                continue
            for i in range(len(keywords)):
                if keywords[i] in valueKeyWords:
                    if values[i][0] == ">":
                        if not (c.find(keywords[i]).text > values[i][1:]):
                            lol = False
                            break
                    elif values[i][0] == "=":
                        if not (c.find(keywords[i]).text == values[i][1:]):
                            lol = False
                            break
                    elif values[i][0] == "<":
                        if not (c.find(keywords[i]).text < values[i][1:]):
                            lol = False
                            break
                    else:
                        if values[i].isnumeric():
                            if not (c.find(keywords[i]).text == values[i]):
                                lol = False
                                break
                        else:
                            lol = False
                            break
                else:
                    try:
                        if keywords[i] == "c":
                            colors = c.find('color').text.lower()
                            for letter in values[i].lower():
                                if not letter in colors:
                                    lol = False
                                    break
                            if not lol:
                                break
                        elif keywords[i] == "o":
                            text = c.find('text').text.lower()
                            if not values[i].lower() in text:
                                lol = False
                                break
                        elif keywords[i] == "-o":
                            text = c.find('text').text.lower()
                            if values[i].lower() in text:
                                lol = False
                                break
                        elif keywords[i] == "t":
                            type = c.find('type').text.lower()
                            if not values[i].lower() in type:
                                lol = False
                                break
                    except:
                        lol = False
                        break

            if not lol:
                continue
            founds += c.find('name').text + "\n"
            count+=1
            if count == 20:
                break
        if len(founds) > 0:
            await message.channel.send(founds)
        else:
            await message.channel.send("Could not find cards for search " + x)
    matches = re.findall('\(\(.*?\)\)', message.content)
    if matches > 5:
        await message.channel.send("Relax.")
        return
    for x in matches:
        lol = False
        cardname = x[2:-2]
        for c in cards:
            if cardname.lower() in c.find('name').text.lower():
                lol = True
                cardfile = "../../Brett stuff/TumbledMTG-Cockatrice/TumbledMTG/data/pics/CUSTOM/"
                cardfile += c.find('name').text
                cardfile += ".jpg"
                await message.channel.send(file=discord.File(cardfile))
                break
        if lol == False:
            await message.channel.send("Could not find card " + x)
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
    global dom
    dom = ElementTree.parse("../../Brett stuff/TumbledMTG-Cockatrice/TumbledMTG/data/customsets/tumbled-mtg-cards.xml")
    global cards
    cards = dom.find('cards')
    cards = cards.findall('card')


token = ""
with open('config.json', 'r') as file:
    data = file.read()
    file_dict = json.loads(data)
    token = file_dict["token"]
client.run(token)
