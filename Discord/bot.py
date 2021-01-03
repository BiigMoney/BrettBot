import discord
from discord.ext import commands, tasks
import os
from os import path
from xml.etree import ElementTree
import json
import glob
import re
from datetime import datetime
import challonge

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '-', case_insensitive=True, intents=intents)
validKeyWords=["cmc","o","t","c","-o","power","toughness","type","-c","-t","-type","p","is"]
valueKeyWords = ["cmc"]
currentTourney = None
currentChallongeTourney = None

@tasks.loop(minutes=1440.0)
async def called_once_a_day():
    clone()

@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()

@tasks.loop(minutes=1.0)
async def called_once_a_min():
    global currentTourney
    global currentChallongeTourney
    if currentTourney != None:
        url = currentTourney['link'].rsplit('/', 1)[-1]
        currentChallongeTourney = challonge.tournaments.show(url)
        matches = challonge.matches.index(currentChallongeTourney['id'])
        for match in matches:
            if match['underway_at'] == None:
                challonge.matches.mark_as_underway(currentChallongeTourney['id'], match['id'])
                channel = client.get_channel(795075875611607060)
                guild = client.get_guild(455612893900308501)
                player1 = str(challonge.participants.show(currentChallongeTourney['id'],match['player1_id'])['name'])
                player2 = str(challonge.participants.show(currentChallongeTourney['id'],match['player2_id'])['name'])

                await channel.send(guild.get_member_named(player1).mention + guild.get_member_named(player2).mention + " you two have a match!")
                print("done")

@called_once_a_min.before_loop
async def before():
    await client.wait_until_ready()

@client.event
async def on_ready():
    if path.exists("tournament.json"):
        with open('tournament.json', 'r') as file:
            data = file.read()
            global currentTourney
            currentTourney = json.loads(data)
            url = currentTourney['link'].rsplit('/', 1)[-1]
            global currentChallongeTourney
            currentChallongeTourney = challonge.tournaments.show(url)
            print(str(currentChallongeTourney))
    called_once_a_day.start()
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
                founds+=keyword+" is not a valid keyword, type -keywords for a list of valid keywords\n"
                del values[keywords.index(keyword)]
                keywords.remove(keyword)
        if len(keywords) > 0 or len(searchwords) > 0:
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
                            if keywords[i] == "-c":
                                colors = c.find('color').text.lower()
                                for letter in values[i].lower():
                                    if letter in colors:
                                        lol = False
                                        break
                                if not lol:
                                    break
                            elif keywords[i] == "c":
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
                            elif keywords[i] == "t" or keywords[i] == "type":
                                type = c.find('type').text.lower()
                                if not values[i].lower() in type:
                                    lol = False
                                    break
                            elif keywords[i] == "-t" or keywords[i] == "-type":
                                type = c.find('type').text.lower()
                                if values[i].lower() in type:
                                    lol = False
                                    break
                            elif keywords[i] == "power" or keywords[i] == "p":
                                power = c.find('pt').text
                                power = power[0]
                                if values[i][0] == ">":
                                    if not (power > values[i][1:]):
                                        lol = False
                                        break
                                elif values[i][0] == "=":
                                    if not (power == values[i][1:]):
                                        lol = False
                                        break
                                elif values[i][0] == "<":
                                    if not (power < values[i][1:]):
                                        lol = False
                                        break
                                else:
                                    if values[i].isnumeric():
                                        if not (power == values[i]):
                                            lol = False
                                            break
                                    else:
                                        lol = False
                                        break
                            elif keywords[i] == "toughness":
                                toughness = c.find('pt').text
                                toughness = toughness[2]
                                if values[i][0] == ">":
                                    if not (toughness > values[i][1:]):
                                        lol = False
                                        break
                                elif values[i][0] == "=":
                                    if not (toughness == values[i][1:]):
                                        lol = False
                                        break
                                elif values[i][0] == "<":
                                    if not (toughness < values[i][1:]):
                                        lol = False
                                        break
                                else:
                                    if values[i].isnumeric():
                                        if not (toughness == values[i]):
                                            lol = False
                                            break
                                    else:
                                        lol = False
                                        break
                            elif keywords[i] == "is":
                                if values[i] == "new":
                                    new = c.find('new').text
                                    if not new == "TRUE":
                                        lol = False
                                else:
                                    lol = False
                        except:
                            lol = False
                            break

                if not lol:
                    continue
                founds += c.find('name').text + "\n"
                count+=1
                if count == 20:
                    founds+="And more!\n"
                    break
        if len(founds) > 0:
            await message.channel.send(founds)
        else:
            await message.channel.send("Could not find cards for search " + x[2:-2] +", note that most searches need a colon (ex. cmc:>3 rather than cmc>3)")
    matches = re.findall('\(\(.*?\)\)', message.content)
    if len(matches) > 5:
        await message.channel.send("Relax.")
        return
    for x in matches:
        lol = False
        cardname = x[2:-2]
        for c in cards:
            if cardname.lower() in c.find('name').text.lower():
                lol = True
                cardfile = "../../Brett stuff/TumbledMTG-Cockatrice/data/pics/CUSTOM/"
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
    dom = ElementTree.parse("../../Brett stuff/TumbledMTG-Cockatrice/data/customsets/tumbled-mtg-cards.xml")
    global cards
    cards = dom.find('cards')
    cards = cards.findall('card')

@client.command()
async def newtournament(ctx, arg):
    global currentTourney
    global currentChallongeTourney
    if str(ctx.guild) == "atw" and str(ctx.author) == "Big Money#7196":
        if currentTourney == None:
            try:
                currentTourney = Tournament(arg)
                url = currentTourney['link'].rsplit('/', 1)[-1]
                currentChallongeTourney = challonge.tournaments.show(url)
                await ctx.send("Tournament started with name " + challonge.tournaments.show(currentTourney.link.rsplit('/', 1)[-1])["name"])
            except:
                currentChallongeTourney = None
                currentTourney = None
                await ctx.send("Failed, there was an error, there's nothing I can do about it but I thought you should know.")
        else:
            await ctx.send("Tournament already in progress")

@client.command()
async def register(ctx):
    global currentTourney
    global currentChallongeTourney
    if currentTourney != None:
        try:
            challonge.participants.create(currentChallongeTourney['id'], str(ctx.author))
            await ctx.send("Added you to the bracket!")
        except:
            await ctx.send("There was an error, I think you have already registered.")
    else:
            await ctx.send("There is no tournament to register for!")


@client.command()
async def deletetourney(ctx):
    global currentTourney
    global currentChallongeTourney
    if str(ctx.guild) == "atw" and str(ctx.author) == "Big Money#7196":
        if currentTourney != None:
            currentTourney = None
            currentChallongeTourney = None
            os.remove("tournament.json")
            await ctx.send("No longer looking at active tourney")
        else:
            await ctx.send("There is no active tourney to delete")


@client.command()
async def keywords(ctx):
    await ctx.send("c:(colors) for colors\no:(word) for oracle text\ncmc:(sign)(value) for cmc\nt:(type) for type\npower:(sign)(value) for power\ntoughness:(sign)(value) for toughness\ncan also use - before c, o, and t to search for opposite\nany other words without a colon are searched for in card title")

class Tournament:
    def __init__(self, link):
        self.link = link
        with open('tournament.json', 'w') as file:
            json.dump({"link": link},file)

token = ""
apikey = ""
with open('config.json', 'r') as file:
    data = file.read()
    file_dict = json.loads(data)
    token = file_dict["token"]
    apikey = file_dict["challongeAPIKey"]
challonge.set_credentials("TumbledMTG", apikey)
client.run(token)
