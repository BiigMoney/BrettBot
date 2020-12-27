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
    matches = re.findall('\(\(.*?\)\)',message.content)
    dom = ElementTree.parse("../../Brett stuff/TumbledMTG-Cockatrice/TumbledMTG/data/customsets/tumbled-mtg-cards.xml")
    cards = dom.find('cards')
    cards = cards.findall('card')
    if len(matches) == 0:
        return
    if len(matches) >= 10:
        await message.channel.send("Relax.")
        return
    for x in matches:
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
        lol = True
        for c in cards:
            title = c.find('name').text
            for word in searchwords:
                if not word.lower() in title.lower():
                    lol = False
            if not lol:
                continue
            for i in range(keywords.length):
                if keywords[i] in valueKeyWords:
                    if values[i][0] == ">":
                        if not (c.find(keywords[i]).text > values[i][1:]):
                            print("keyword in valueKeyWords values[i][0] == " + values[i] + " not greater than " + c.find(keywords[i]).text)
                            lol = False
                            break
                    elif values[i][0] == "=":
                        if not (c.find(keywords[i]).text == values[i][1:]):
                            print("keyword in valueKeyWords values[i][0] == " + values[
                                i] + " not equal to " + c.find(keywords[i]).text)
                            lol = False
                            break
                    elif values[i][0] == "<":
                        if not (c.find(keywords[i]).text < values[i][1:]):
                            print("keyword in valueKeyWords values[i][0] == " + values[
                                i] + " not less than " + c.find(keywords[i]).text)
                            lol = False
                            break
                    else:
                        if values[i].isnumeric():
                            if not (c.find(keywords[i]).text == values[i]):
                                print("keyword in valueKeyWords values[i][0] == " + values[
                                    i] + " not equal to " + c.find(keywords[i]).text)
                                lol = False
                                break
                        else:
                            print("keyword in valueKeyWords values[i][0] == " + values[
                                i] + " not valid or numeric")
                            lol = False
                            break
                else:
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
            if not lol:
                 continue
            founds += c.find('name').text + "\n"
        if len(founds) > 0:
            await message.channel.send(founds)
        else:
            await message.channel.send("Could not find cards for search " + x)
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
