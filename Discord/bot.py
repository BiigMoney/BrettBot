import discord
from discord.ext import commands, tasks
import os
from os import path
from xml.etree import ElementTree
import json
import glob
import re
from datetime import datetime
from datetime import timedelta
import challonge
import requests
from random import randrange

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix = '-', case_insensitive=True, intents=intents)
validKeyWords=["cmc","o","t","c","-o","power","toughness","type","-c","-t","-type","p","is"]
valueKeyWords = ["cmc"]
tournamentData = None

def updateJSON():
    global tournamentData
    with open('tournament.json', 'w') as file:
        json.dump({"data":tournamentData}, file)

@tasks.loop(minutes=1440.0)
async def called_once_a_day():
    clone()

@called_once_a_day.before_loop
async def before():
    await client.wait_until_ready()

async def checkToStartWeekly():
    global tournamentData
    tourney = tournamentData['weekly']
    weekday = datetime.today().weekday()
    hour = datetime.now().hour
    channel = client.get_channel(795075875611607060)
    if weekday == 4 and hour == 14:
        await channel.send("Don't forget, the weekly is starting in 4 hours! DM me '-registerweekly (decklist)' to sign up, replacing (decklist) with the decklist you want to use for the tournament.")
    elif weekday == 4 and hour == 18:
        if tourney != None:
            challongeTourney = challonge.tournaments.show(tourney['link'].rsplit('/', 1)[-1])
            if challongeTourney['started_at'] == None:
                if challongeTourney['participants_count'] < 2:
                    challonge.tournaments.destroy(challongeTourney['id'])
                    await channel.send("Tried to start a tournament with less than 2 people, tournament has been aborted.")
                    tournamentData['weekly'] = None
                    updateJSON()
                    return
                else:
                    try:
                        for player in tourney['players']:
                            body = decklistRequest((str(challongeTourney['start_at'])[0:10] + " Weekly Decklist"),
                                                      str(player['name']).split("#")[0], player['decklist']).__dict__
                            r = requests.post('https://us-central1-tumbledmtg-website.cloudfunctions.net/api/decklist', json=body)
                            if 'decklist' in r.json():
                                player['decklist'] = "https://tumbledmtg.com/decklist=" + str(r.json()['decklist']['id'])
                            else:
                                print(r.json())
                    except:
                        await channel.send("Something went wrong when uploading player decklists. Idk what to do, everything is broken, someone please help I can't do this on my own.")
                        return
                    updateJSON()
                    challonge.tournaments.update(challongeTourney['id'], description=json.dumps(tourney['players']))
                    challonge.participants.randomize(challongeTourney['id'])
                    challonge.tournaments.start(challongeTourney['id'])
                    await channel.send("The weekly tournament is starting! Decklists have been uploaded.")

async def checkToEndWeekly():
    global tournamentData
    channel = client.get_channel(795075875611607060)
    tourney = tournamentData['weekly']
    weekday = datetime.today().weekday()
    hour = datetime.now().hour
    if tourney != None:
        challongeTourney = challonge.tournaments.show(tourney['link'].rsplit('/', 1)[-1])
        if challongeTourney['progress_meter'] == 100:
            challonge.tournaments.finalize(challongeTourney['id'])
            participants = challonge.participants.index(challongeTourney['id'])
            if challongeTourney['participants_count'] < 5:
                try:
                    for participant in participants:
                        if participant['final_rank'] == 1:
                            name = participant['name']
                            for player in tourney['players']:
                                if player['name'] == name:
                                    r = requests.put("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/stars/" + player['decklist'].rsplit('/', 1)[-1].split("=")[1], json={"inc" : 1})
                                    if not 'success' in r.json():
                                        await channel.send("Unsuccessful star count update. 1")
                except:
                    await channel.send("Failed to update star count for tourney with 4 or less players.")
            elif challongeTourney['participants_count'] < 9:
                try:
                    for participant in participants:
                        if participant['final_rank'] == 1:
                            name = participant['name']
                            for player in tourney['players']:
                                if player['name'] == name:
                                    r = requests.put("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/stars/" + player['decklist'].rsplit('/', 1)[-1].split("=")[1], json={"inc" : 2})
                                    if not 'success' in r.json():
                                        await channel.send("Unsuccessful star count update. 2")
                        elif participant['final_rank'] == 2:
                            name = participant['name']
                            for player in tourney['players']:
                                if player['name'] == name:
                                    r = requests.put("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/stars/" + player['decklist'].rsplit('/', 1)[-1].split("=")[1], json={"inc": 1})
                                    if not 'success' in r.json():
                                        await channel.send("Unsuccessful star count update. 3")
                except:
                    await channel.send("Failed to update star count for tourney with 8 or less players.")
            else:
                try:
                    for participant in participants:
                        if participant['final_rank'] == 1:
                            name = participant['name']
                            for player in tourney['players']:
                                if player['name'] == name:
                                    r = requests.put("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/stars/" + player['decklist'].rsplit('/', 1)[-1].split("=")[1], json={"inc" : 3})
                                    if not 'success' in r.json():
                                        await channel.send("Unsuccessful star count update. 4")
                        elif participant['final_rank'] == 2:
                            name = participant['name']
                            for player in tourney['players']:
                                if player['name'] == name:
                                    r = requests.put("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/stars/" + player['decklist'].rsplit('/', 1)[-1].split("=")[1], json={"inc": 2})
                                    if not 'success' in r.json():
                                        await channel.send("Unsuccessful star count update. 5")
                        elif participant['final_rank'] == 3:
                            name = participant['name']
                            for player in tourney['players']:
                                if player['name'] == name:
                                    r = requests.put("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/stars/" + player['decklist'].rsplit('/', 1)[-1].split("=")[1], json={"inc": 1})
                                    if not 'success' in r.json():
                                        await channel.send("Unsuccessful star count update. 6")
                except:
                    await channel.send("Failed to update star count for tourney with 9 or more players.")

            await channel.send("The weekly has finished. You can see the results and decklists at https://tumbledmtg.com/tournament=" + str(challongeTourney['id']))
            tournamentData['weekly'] = None
            updateJSON()
        elif weekday == 2 and hour == 18:
            await channel.send("The current weekly is taking too long, all remaining matches and stars will have to be updated manually. You can check out the bracket at " + tourney['link'])
            tournamentData['weekly'] = None
            updateJSON()
    else:
        try:
            if weekday == 4 and hour == 2:
                newChallongeTourney = challonge.tournaments.create(url="tbldmtgweekly" + str(datetime.today().strftime("%d_%m_%Y"))+ str(randrange(10000)), start_at= datetime.today() + timedelta((4-datetime.today().weekday()) % 7), name="TumbledMTG Weekly " + str(datetime.today() + timedelta((4-datetime.today().weekday()) % 7))[0:10])
                tournamentData['weekly'] = Tournament(newChallongeTourney['full_challonge_url']).__dict__
                updateJSON()
                await channel.send("The next weekly has been created. DM me '-registerweekly (decklist)' before Friday at 6pm PST to sign up, replacing (decklist) with the decklist you want to use for the tournament. You can find the bracket at " + newChallongeTourney['full_challonge_url'])
        except:
            print("Challonge request failed")
async def callMatches(tourney):
    if tourney != None:
        url = tourney['link'].rsplit('/', 1)[-1]
        challongeTourney = challonge.tournaments.show(url)
        matches = challonge.matches.index(challongeTourney['id'])
        for match in matches:
            if match['player1_id'] == None or match['player2_id'] == None:
                continue
            if match['underway_at'] == None:
                challonge.matches.mark_as_underway(challongeTourney['id'], match['id'])
                channel = client.get_channel(795075875611607060)
                guild = client.get_guild(455612893900308501)
                try:
                    player1 = str(challonge.participants.show(challongeTourney['id'],match['player1_id'])['name'])
                    player2 = str(challonge.participants.show(challongeTourney['id'],match['player2_id'])['name'])
                    await channel.send(guild.get_member_named(player1).mention + guild.get_member_named(player2).mention + " you two have a match!")
                except:
                    await channel.send("A match has started but one of the players was not found in this discord.")

@tasks.loop(minutes=5.0)
async def called_once_a_min():
    global tournamentData
    await checkToEndWeekly()
    await checkToStartWeekly()
    await callMatches(tournamentData['main'])
    await callMatches(tournamentData['weekly'])


@called_once_a_min.before_loop
async def before():
    await client.wait_until_ready()

@client.event
async def on_ready():
    if path.exists("tournament.json"):
        with open('tournament.json', 'r') as file:
            data = file.read()
            global tournamentData
            tournamentData = json.loads(data)['data']
            print(tournamentData)
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
                                if values[i][0] == "=":
                                    for letter in values[i].lower():
                                        if letter == "=":
                                            continue
                                        else:
                                            if not letter in colors:
                                                lol = False
                                                break
                                    if "h" in colors:
                                        break
                                    if not (len(colors) == len(values[i])) and not (colors.length == 1):
                                        lol = False
                                    break
                                for letter in values[i].lower():
                                    if not letter in colors:
                                        lol = False
                                        break
                                if not lol:
                                    break
                            elif keywords[i] == "o":
                                text = c.find('text').text.lower()
                                if "," in values[i]:
                                    thevalue = values[i].replace(","," ")
                                    if (thevalue.startswith("'") and thevalue.endswith("'")) or (thevalue.startswith('"') and thevalue.endswith('"')):
                                        thevalue = thevalue[2:-2]
                                        if not thevalue in text:
                                            lol = False
                                        break
                                    else:
                                        thevalue = values[i].replace(","," ").split(" ")
                                        for word in thevalue:
                                            if not word in text:
                                                lol = False
                                                break
                                        break
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

@client.command()
async def updatestars(ctx, decklist, stars):
    if str(ctx.author) != "Tumbles#3232":
        return
    try:
        decklistid = decklist.rsplit('/', 1)[-1].split("=")[1]
        r = requests.put("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/stars/" + decklistid, json={"inc": stars})
        if 'success' in r.json():
            await ctx.send("Successfully updated stars.")
        else:
            await ctx.send("Response returned errors.")
    except:
        await ctx.send("Error sending response.")

@client.command()
async def deletedecklist(ctx, decklist):
    if not (str(ctx.author) == "Tumbles#3232" or str(ctx.author) == "Big Money#7196"):
        return
    decklistid = decklist.rsplit('/', 1)[-1].split("=")[1]
    r = requests.delete("https://us-central1-tumbledmtg-website.cloudfunctions.net/api/deldecklist/" + decklistid)
    await ctx.send("Request sent.")
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
    global tournamentData
    if str(ctx.guild) == "TumbledMTG" and str(ctx.author) == "Tumbles#3232":
        if tournamentData['main'] == None:
            try:
                tournamentData['main'] = Tournament(arg).__dict__
                tourney = challonge.tournaments.show(tournamentData['main']['link'].rsplit('/', 1)[-1])
                updateJSON()
                await ctx.send("Tournament started with name " + tourney["name"] +", scheduled for " + str(tourney['start_at']))
            except Exception as e:
                print(e)
                tournamentData['main'] = None
                updateJSON()
                await ctx.send("Failed, likely a challonge error.")
        else:
            await ctx.send("Tournament already in progress")

@client.command()
async def registertourney(ctx, *, args):
    decklist = args
    global tournamentData
    tourney = tournamentData['main']
    if tourney != None:
        try:
            challongeTourney = challonge.tournaments.show(tourney['link'].rsplit('/', 1)[-1])
        except:
            await ctx.send("Error getting challonge bracket, please try again.")
            return
        if challongeTourney['started_at'] == None:
            body = decklistRequest((str(challongeTourney['start_at'])[0:10] + " Weekly Decklist"),
                                              str(ctx.author).split("#")[0], decklist).__dict__
            print(body)
            r = requests.post('https://us-central1-tumbledmtg-website.cloudfunctions.net/api/testdecklist',
                              json=body)
            if 'errors' in r.json():
                print(r.json())
                await ctx.send("Invalid decklist: " +r.json()['errors'])
                return
            elif 'success' in r.json():
                await ctx.send("Decklist is valid!")
            else:
                await ctx.send("Server error, I think... you have not been registered, try again maybe? If this happens more than once then call for help.")
                print(r.json())
                return
            try:
                challonge.participants.create(challongeTourney['id'], str(ctx.author))
                tourney['players'].append(Player(str(ctx.author), decklist).__dict__)
                updateJSON()
                await ctx.send("Added you to the bracket!")
                channel = client.get_channel(795075875611607060)
                await channel.send(str(ctx.author) + " has registered for the tournament!")
            except:
                await ctx.send("There was an error, either you are already registered or challonge failed to respond.")
        else:
            await ctx.send("The tournament has already started.")
    else:
        await ctx.send("There is no tournament to register for!")

@client.command()
async def registerweekly(ctx, *, args):
    decklist = args
    global tournamentData
    tourney = tournamentData['weekly']
    if tourney != None:
        try:
            challongeTourney = challonge.tournaments.show(tourney['link'].rsplit('/', 1)[-1])
        except:
            await ctx.send("Error getting challonge bracket, please try again.")
        if challongeTourney['started_at'] == None:
            body = decklistRequest((str(challongeTourney['start_at'])[0:10] + " Weekly Decklist"),
                                   str(ctx.author).split("#")[0], decklist).__dict__
            r = requests.post('https://us-central1-tumbledmtg-website.cloudfunctions.net/api/testdecklist',
                              json=body)
            if 'errors' in r.json():
                print(r.json())
                await ctx.send("Invalid decklist: " + str(r.json()['errors']))
                return
            elif 'success' in r.json():
                await ctx.send("Decklist is valid!")
            else:
                await ctx.send("Server error, I think... you have not been registered, try again maybe? If this happens more than once then call for help.")
                print(r.json())
                return
            try:
                challonge.participants.create(challongeTourney['id'], str(ctx.author))
                tourney['players'].append(Player(str(ctx.author), decklist).__dict__)
                updateJSON()
                await ctx.send("Added you to the bracket!")
                channel = client.get_channel(795075875611607060)
                await channel.send(str(ctx.author) + " has registered for the weekly!")
            except:
                await ctx.send("There was an error, either you are already registered or challonge failed to respond. Maybe try again, and if it doesn't work then call for help.")
        else:
            await ctx.send("The tournament has already started.")
    else:
        await ctx.send("There is no tournament to register for!")

@client.command()
async def deletetourney(ctx):
    global tournamentData
    if str(ctx.guild) == "TumbledMTG" and str(ctx.author) == "Tumbles#3232":
        if tournamentData['main'] != None:
            tournamentData['main'] = None
            updateJSON()
            await ctx.send("No longer looking at active tourney")
        else:
            await ctx.send("There is no active tourney to delete")

@client.command()
async def weeklyreport(ctx, *args):
    if len(args) != 2:
        await ctx.send("Invalid report syntax.")
        return
    score = args[0]
    opponent = ctx.message.mentions[0]
    if opponent == None:
        await ctx.send("Invalid opponent.")
        return
    if len(score) != 3:
        await ctx.send("Invalid score syntax!")
        return
    playerscore = score[0]
    opponentscore = score[2]
    if not playerscore.isnumeric() or not opponentscore.isnumeric() or score[1] != "-":
        await ctx.send("Invalid score syntax.")
        return
    if playerscore == "0" and opponentscore == "0":
        await ctx.send("I'm not submitting this score and you can't make me.")
        return
    if playerscore == opponentscore:
        await ctx.send("Why are you submitting a tie, why why why why why why why why why why.")
        return
    opponent = opponent.name + "#" + str(opponent.discriminator)
    player = ctx.author.name + "#" + str(ctx.author.discriminator)
    global tournamentData
    tourney = tournamentData['weekly']
    try:
        challongeTourney = challonge.tournaments.show(tourney['link'].rsplit('/', 1)[-1])
        matches = challonge.matches.index(challongeTourney['id'])
        participants = challonge.participants.index(challongeTourney['id'])
    except:
        await ctx.send("Challonge failed to respond, please try again.")
        return
    playerid = ""
    opponentid = ""
    try:
        for participant in participants:
            if participant['name'] == player:
                playerid = participant['id']
            elif participant['name'] == opponent:
                opponentid = participant['id']
    except:
        await ctx.send("Error parsing tourney participants, most likely a challonge error, try again.")
        return
    lol = False
    try:
        for match in matches:
            if match['winner_id'] != None or match['state'] != "open":
                continue
            if match['player1_id'] == playerid and match['player2_id'] == opponentid:
                if playerscore > opponentscore:
                    challonge.matches.update(challongeTourney['id'], match['id'], scores_csv=score, winner_id=playerid)
                    lol = True
                    break
                else:
                    challonge.matches.update(challongeTourney['id'], match['id'], scores_csv=score, winner_id=opponentid)
                    lol = True
                    break
            elif match['player1_id'] == opponentid and match['player2_id'] == playerid:
                score = score[-1] + score[1:-1] + score[0]
                if playerscore > opponentscore:
                    challonge.matches.update(challongeTourney['id'], match['id'], scores_csv=score, winner_id=playerid)
                    lol = True
                    break
                else:
                    challonge.matches.update(challongeTourney['id'], match['id'], scores_csv=score, winner_id=opponentid)
                    lol = True
                    break
    except Exception as e:
        print(e)
        await ctx.send("Error updating scores, probably a challonge error as an actual error was thrown. Try again, and if it happens again, call for help.")
        return
    if not lol:
        await ctx.send("Error updating scores, could not find a match between these 2 players.")
        return
    await ctx.send("Scores have successfully been submitted!")

@client.command()
async def uploaddecklists(ctx):
    global tournamentData
    if str(ctx.guild) == "TumbledMTG" and str(ctx.author) == "Tumbles#3232":
        tourney = tournamentData['main']
        try:
            challongeTourney = challonge.tournaments.show(tourney['link'].rsplit('/', 1)[-1])
        except:
            await ctx.send("Challonge server error, please try again.")
            return
        try:
            for player in tourney['players']:
                body = decklistRequest("Tourney Decklist",
                                       str(player['name']).split("#")[0], player['decklist']).__dict__
                r = requests.post('https://us-central1-tumbledmtg-website.cloudfunctions.net/api/decklist', json=body)
                if 'decklist' in r.json():
                    player['decklist'] = "https://tumbledmtg.com/decklist=" + str(r.json()['decklist']['id'])
                else:
                    print(r.json())
        except:
            await ctx.send("Something went wrong when uploading player decklists. Idk what to do, everything is broken, someone please help I can't do this on my own.")
            return
        updateJSON()
        try:
            challonge.tournaments.update(challongeTourney['id'], description=json.dumps(tourney['players']))
        except:
            await ctx.send("Challonge server error when updating description, everything else worked I think, but descrition will have to be updated manually.")
            return
        await ctx.send("Decklists have been uploaded!")

@client.command()
async def tourneyreport(ctx, *args):
    if len(args) != 2:
        await ctx.send("Invalid report syntax.")
        return
    score = args[0]
    opponent = ctx.message.mentions[0]
    if opponent == None:
        await ctx.send("Invalid opponent.")
        return
    if len(score) != 3:
        await ctx.send("Invalid score syntax!")
        return
    playerscore = score[0]
    opponentscore = score[2]
    if not playerscore.isnumeric() or not opponentscore.isnumeric() or score[1] != "-":
        await ctx.send("Invalid score syntax.")
        return
    if playerscore == "0" and opponentscore == "0":
        await ctx.send("I'm not submitting this score and you can't make me.")
        return
    if playerscore == opponentscore:
        await ctx.send("Why are you submitting a tie, why why why why why why why why why why.")
        return
    opponent = opponent.name + "#" + str(opponent.discriminator)
    player = ctx.author.name + "#" + str(ctx.author.discriminator)
    global tournamentData
    tourney = tournamentData['main']
    try:
        challongeTourney = challonge.tournaments.show(tourney['link'].rsplit('/', 1)[-1])
        matches = challonge.matches.index(challongeTourney['id'])
        participants = challonge.participants.index(challongeTourney['id'])
    except:
        await ctx.send("Challonge failed to respond, please try again.")
        return
    playerid = ""
    opponentid = ""
    try:
        for participant in participants:
            if participant['name'] == player:
                playerid = participant['id']
            elif participant['name'] == opponent:
                opponentid = participant['id']
    except:
        await ctx.send("Error parsing tourney participants, most likely a challonge error, try again.")
        return
    lol = False
    try:
        for match in matches:
            if match['winner_id'] != None or match['state'] != "open":
                continue
            if match['player1_id'] == playerid and match['player2_id'] == opponentid:
                if playerscore > opponentscore:
                    challonge.matches.update(challongeTourney['id'], match['id'], scores_csv=score, winner_id=playerid)
                    lol = True
                    break
                else:
                    challonge.matches.update(challongeTourney['id'], match['id'], scores_csv=score, winner_id=opponentid)
                    lol = True
                    break
            elif match['player1_id'] == opponentid and match['player2_id'] == playerid:
                score = score[-1] + score[1:-1] + score[0]
                if playerscore > opponentscore:
                    challonge.matches.update(challongeTourney['id'], match['id'], scores_csv=score, winner_id=playerid)
                    lol = True
                    break
                else:
                    challonge.matches.update(challongeTourney['id'], match['id'], scores_csv=score, winner_id=opponentid)
                    lol = True
                    break
    except Exception as e:
        print(e)
        await ctx.send("Error updating scores, probably a challonge error as an actual error was thrown. Try again, and if it happens again, call for help.")
        return
    if not lol:
        await ctx.send("Error updating scores, could not find a match between these 2 players.")
        return
    await ctx.send("Scores have successfully been submitted!")



@client.command()
async def keywords(ctx):
    await ctx.send("c:(colors) for colors\no:(word) for oracle text\ncmc:(sign)(value) for cmc\nt:(type) for type\npower:(sign)(value) for power\ntoughness:(sign)(value) for toughness\ncan also use - before c, o, and t to search for opposite\nany other words without a colon are searched for in card title")

class Tournament:
    def __init__(self, link):
        self.link = link
        self.players = []

class Player:
    def __init__(self, name, decklist):
        self.name = name
        self.decklist = decklist

class decklistRequest:
    def __init__(self, title, author, body):
        self.title = title
        self.author = author
        self.body = body
        self.description = "This decklist was automatically generated by the discord bot."

token = ""
apikey = ""
with open('config.json', 'r') as file:
    data = file.read()
    file_dict = json.loads(data)
    token = file_dict["token"]
    apikey = file_dict["challongeAPIKey"]
challonge.set_credentials("TumbledMTG", apikey)
client.run(token)
