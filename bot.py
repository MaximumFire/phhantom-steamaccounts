import discord
from discord.ext import commands
import random
import os
import csv
from discord.ext.commands import BucketType
from discord.ext.commands import cooldown

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '.', intents = intents)

#Variables
fileOne = None
lineCount = None

#Events
@client.event
async def on_ready():
    global fileOne
    print("Bot is online.")
    fileOne = open("lineCount.txt","r+")
    print("File Opened")
    await client.change_presence(activity=discord.Game(name="Type .help for help"))

@client.event
async def on_message(message):
    await client.process_commands(message)
    if message.channel.id == 749246836237271160:
        await message.delete()

#Commands
@client.command()
async def openFile(ctx):
    global fileOne
    if "dev" in [i.name.lower() for i in ctx.author.roles]:
        fileOne = open("lineCount.txt","r+")
        print("File Opened")
    else:
        await ctx.send("This command is only availiable for devs.")

@client.command()
async def readFile(ctx):
    global fileOne
    global lineCount
    if "dev" in [i.name.lower() for i in ctx.author.roles]:
        line_count = fileOne.read()
        print("File read. contents are: " + str(lineCount))
    else:
        await ctx.send("This command is only availiable for devs.")

@client.command()
async def setLineCount(ctx, *, number):
    global line_count
    global fileOne
    if "dev" in [i.name.lower() for i in ctx.author.roles]:
        fileOne.truncate(0)
        fileOne.seek(0)
        fileOne.write(number)
        fileOne.close()
        fileOne = open("lineCount.txt","r+")
    else:
        await ctx.send("This command is only availiable for devs.")
        
@client.command()
async def getSteamAccount(ctx, author):
    global lineCount
    global fileOne
    if "dev" in [i.name.lower() for i in ctx.author.roles]:
        with open('steam_accounts.csv', mode='r') as csv_file:
            fileOne.seek(0)
            fileContents = fileOne.read(2)
            print("fileContents is: " + fileContents)
            lineCount = int(fileContents) + 1
            print("lineCount is: " + str(lineCount))
            csv_reader = csv.DictReader(csv_file)
            loop = 0
            for row in csv_reader:
                loop = loop + 1
                if loop == lineCount:
                    await ctx.author.send("Your username is: " + row["Username"])
                    await ctx.author.send("Your password is: " + row["Password"])
            fileOne.truncate(0)
            fileOne.seek(0)
            fileOne.write(str(lineCount))
            fileOne.close()
            fileOne = open("lineCount.txt","r+")
    else:
        await ctx.send("This command is only availiable for devs.")

@getSteamAccount.error
async def getSteamAccount_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'This command has a cooldown, please try again in {:.2f}s'.format(error.retry_after)
        await ctx.send(msg)
    elif isinstance(error, commands.MissingRequiredArgument):
        if error.param.name == 'author':
            await ctx.send("Please @ yourself after the command. For example: '.getSteamAccount @MaximumFire'")
    else:
        raise error

@client.command()
async def checkLineCount(ctx):
    global line_count
    print("line_count is: " + str(lineCount))

@client.command()
async def closeFile(ctx):
    global fileOne
    if "dev" in [i.name.lower() for i in ctx.author.roles]:
        fileOne.close()
        print("File Closed")
    else:
        await ctx.send("This command is only availiable for devs.")
client.run(os.environ['discord_token'])
