import time
import random

import discord
from discord.ext import commands
from discord.ext.commands.errors import MissingRequiredArgument

import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
TOKEN = os.environ.get('BOT_TOKEN')

#globals for tracking players
players = []
playerTurnCount = []
currentTurn = -1
hasGameStarted = False

finalPlayers = []
finalPlayerTurnCount = []

startTime = 0
endTime = 0

#BOT COMMANDS/INFO
activity = discord.Activity(type = discord.ActivityType.listening, name = "#help")
bot = commands.Bot(command_prefix = "#", activity = activity, status = discord.Status.online)
bot.remove_command("help")

@bot.command(name = "help")
async def help(ctx):
    await ctx.message.delete()

    message = discord.Embed(title = "Bot Commands", color = 0x00ff00)
    message.add_field(name = "#join", value = "join the current game session", inline = False)
    message.add_field(name = "#quit", value = "quit the current game session", inline = False)
    message.add_field(name = "#next", value = "advances game to the next turn", inline = False)
    message.add_field(name = "#randomstart", value = "chooses a player at random to start the game from", inline = False)
    message.add_field(name = "#random", value = "selects a random player from the current game session", inline = False)
    message.add_field(name = "#players", value = "lists all players in the current game session", inline = False)
    message.add_field(name = "#countdown", value = "triggers a countdown from 3", inline = False)
    message.add_field(name = "#endgame", value = "ends the game session and displays final stats", inline = False)

    await ctx.send(embed = message)

@bot.command(name = "join")
async def join(ctx):
    await ctx.message.delete()

    try:
        players.index(ctx.author.display_name)

        await ctx.send("`{} is already in the game!`".format(ctx.author.display_name), delete_after = 5.0)
    except:
        players.append(ctx.author.display_name)
        playerTurnCount.append(0)

        await ctx.send("`{} joined the game!`".format(ctx.author.display_name))

@bot.command(name = "quit")
async def quit(ctx):
    await ctx.message.delete()

    try:
        removedIndex = players.index(ctx.author.display_name)
        finalPlayers.append(players.pop(removedIndex))
        finalPlayerTurnCount.append(playerTurnCount.pop(removedIndex))

        await ctx.send("`{} quit the game!`".format(ctx.author.display_name))
    except:
        await ctx.send("`{} was not found in the current game session!`".format(ctx.author.display_name), delete_after = 5.0)

@bot.command(name = "removeplayer")
async def removeplayer(ctx, player):
    await ctx.message.delete()

    try:
        removedIndex = players.index(player)
        finalPlayers.append(players.pop(removedIndex))
        finalPlayerTurnCount.append(playerTurnCount.pop(removedIndex))

        await ctx.send("`{} was removed!`".format(player))
    except:
        await ctx.send("`{} was not found in the current game session!`".format(player), delete_after = 5.0)

@removeplayer.error
async def removeplayerError(ctx, error):
    if isinstance(error, MissingRequiredArgument):
        await ctx.send("`Missing argument in: #removeplayer [argument]`, {}".format(ctx.author.mention), delete_after = 5.0)

@bot.command(name = "next")
async def next(ctx):
    global currentTurn
    global startTime

    await ctx.message.delete()

    if startTime == 0:
        startTime = time.time()

    if(len(players) == 0):
        await ctx.send("No players in active game session!", delete_after = 5.0)
        return
    elif(len(players) == 1):
        await ctx.send("Are you *really* playing a drinking game ***alone***???", delete_after = 5.0)
        return

    if(currentTurn == len(players) - 1):
        currentTurn = -1

    currentTurn += 1
    playerTurnCount[currentTurn] += 1
    
    message = discord.Embed(title = "Turn Tracker", color = 0x00ff00)
    message.add_field(name = "Current Turn", value = players[currentTurn].capitalize(), inline = False)

    await ctx.send(embed = message, delete_after = 20.0)

@bot.command(name = "random")
async def randomPlayer(ctx):
    await ctx.message.delete()

    if(len(players) == 0):
        await ctx.send("No players to randomly pick from!", delete_after = 5.0)
    elif(len(players) == 1):
        await ctx.send("You really are playing a drinking game alone aren't you?", delete_after = 5.0)
    else:
        randomPlayer = random.randint(0, (len(players) - 1))

        message = discord.Embed(title = "Random Player Picker", color = 0x00ff00)
        message.add_field(name = "Player Picked", value = players[randomPlayer].capitalize(), inline = False)

        await ctx.send(embed = message, delete_after = 20.0)

@bot.command(name = "randomstart")
async def randomStart(ctx):
    global hasGameStarted
    global currentTurn
    global startTime

    await ctx.message.delete()
    startTime = time.time()

    if(len(players) == 0):
        await ctx.send("No players added to start game!", delete_after = 5.0)
    elif(len(players) == 1):
        await ctx.send("Seriously...you are playing a drinking game alone??", delete_after = 5.0)
    else:
        if(hasGameStarted == False):
            hasGameStarted = True
            randomStartIndex = random.randint(0, (len(players) - 1))
            currentTurn = randomStartIndex

            message = discord.Embed(title = "Random Start", color = 0x00ff00)
            message.add_field(name = "Player Picked", value = players[randomStartIndex].capitalize(), inline = False)

            await ctx.send(embed = message, delete_after = 20.0)
        else:
            await ctx.send("This command can only be used once per game session!", delete_after = 5.0)

@bot.command(name = "countdown")
async def countdown(ctx):
    await ctx.message.delete()

    time.sleep(0.5)
    await ctx.send("**3**", delete_after = 5.0)
    time.sleep(1)
    await ctx.send("**2**", delete_after = 5.0)
    time.sleep(1)
    await ctx.send("**1**", delete_after = 5.0)

@bot.command(name = "players")
async def listPlayers(ctx):
    currentPlayers = ""

    await ctx.message.delete()

    try:
        for eachPlayer in players:
            currentPlayers += eachPlayer.capitalize() + "\n"

        message = discord.Embed(title = "Current Players", color = 0x00ff00)
        message.add_field(name = "Players", value = currentPlayers, inline = False)

        await ctx.send(embed = message, delete_after = 30.0)
    except:
        await ctx.send("`No players in current game session`", delete_after = 5.0)

@bot.command(name = "endgame")
async def endgame(ctx):
    global hasGameStarted
    global currentTurn
    global startTime
    global endTime
    playerName = ""
    turnCount = ""

    await ctx.message.delete()
    endTime = time.time()
    timeLapsed = endTime - startTime

    def time_convert(seconds):
        minutes = seconds // 60
        seconds = seconds % 60
        hours = minutes // 60
        minutes = minutes % 60

        timeMessage = "{0} hour(s), {1} minute(s), {2} second(s)".format(int(hours), int(minutes), int(seconds))
        return timeMessage

    if(len(players) == 0 and (len(finalPlayers)) == 0):
        await ctx.send("No game session running right now! Start one with at least 2 players.", delete_after = 5.0)
        return

    for x, y in zip(players, playerTurnCount):
        finalPlayers.append(x)
        finalPlayerTurnCount.append(y)
    
    for x in range(len(finalPlayers)):
        playerName += finalPlayers[x] + "\n"
        turnCount += str(finalPlayerTurnCount[x]) + "\n"

    message = discord.Embed(title="Final Stats", color = 0x00ff00)
    message.add_field(name = "Player", value = playerName, inline = True)
    message.add_field(name = "Rounds Completed", value = turnCount, inline = True)

    if startTime != 0:
        message.add_field(name = "Time Lapsed", value = time_convert(timeLapsed), inline = False)
    else:
        message.add_field(name = "Time Lapsed", value = "0 hours, 0 minutes, 0 seconds \n (Game not started properly using #next or #randomstart)", inline = False)

    await ctx.send(embed = message)

    #resets all lists and counters to reset the game session
    players.clear()
    playerTurnCount.clear()
    currentTurn = -1
    finalPlayers.clear()
    finalPlayerTurnCount.clear()
    hasGameStarted = False
    startTime = 0
    endTime = 0

bot.run(TOKEN)