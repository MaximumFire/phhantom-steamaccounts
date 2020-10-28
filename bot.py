import discord
from discord.ext import commands
import random
import os
import csv
from discord.ext.commands import BucketType
from discord.ext.commands import cooldown
import psycopg2

intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '.', intents = intents)
client.remove_command('help')
DATABASE_URL = os.environ['DATABASE_URL']
con = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = con.cursor()

#Variables
fileOne = None
lineCount = None

#Events
@client.event
async def on_ready():
    global fileOne
    global lineCount
    global con
    global cur
    print("Bot is online.")
    fileOne = open("lineCount.txt","r+")
    print("File Opened")
    await client.change_presence(activity=discord.Game(name="Type .help for help"))

#Commands
@client.command()
async def help(ctx):
    await ctx.send("Use the '.getSteamAcc @yourNameHere' to get an account")

@client.command()
async def setLineCount(ctx, *, number):
    global lineCount
    global fileOne
    if "owner" in [i.name.lower() for i in ctx.author.roles]:
        fileOne.truncate(0)
        fileOne.seek(0)
        fileOne.write(number)
        fileOne.close()
        fileOne = open("lineCount.txt","r+")
        lineCount = fileOne.read()
    else:
        await ctx.send("This command is only availiable for Owners.")
        
@client.command()
@cooldown(1, 3600, BucketType.user)
async def getSteamAcc(ctx, author):
    global lineCount
    global fileOne
    if "verified" in [i.name.lower() for i in ctx.author.roles]:
        with open('steam_accounts.csv', mode='r') as csv_file:
            fileOne.seek(0)
            fileContents = fileOne.read()
            print("fileContents is: " + fileContents)
            lineCount = int(fileContents) + 1
            print("lineCount is: " + str(lineCount))
            csv_reader = csv.DictReader(csv_file)
            loop = 0
            for row in csv_reader:
                loop = loop + 1
                if loop == lineCount:
                    if row["Username"] == "":
                        await ctx.send("There are no more accounts availiable. Contact @MaximumFire for help.")
                    else:
                        await ctx.author.send("Your username is: " + row["Username"])
                        await ctx.author.send("Your password is: " + row["Password"])
            fileOne.truncate(0)
            fileOne.seek(0)
            fileOne.write(str(lineCount))
            fileOne.close()
            fileOne = open("lineCount.txt","r+")
            lineCount = fileOne.read()
            channel = client.get_channel(770424797205102643)
            await channel.send("lineCount is: " + str(lineCount))
    else:
        await ctx.send("This command is only availiable for @verified")

@getSteamAcc.error
async def getSteamAcc_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        msg = 'This command has a cooldown, please try again in {:.2f}s'.format(error.retry_after)
        await ctx.send(msg)
    elif isinstance(error, commands.MissingRequiredArgument):
        if error.param.name == 'author':
            await ctx.send("Please @ yourself after the command. For example: '.getSteamAcc @MaximumFire'")
            getSteamAcc.reset_cooldown(ctx)
    else:
        raise error
        getSteamAcc.reset_cooldown(ctx)

@client.command()
async def checkLineCount(ctx):
    global line_count
    print("line_count is: " + str(lineCount))
    await ctx.send("lineCount is: " + str(lineCount))

@client.command()
async def getTableData(ctx):
    global con
    global cur
    cur.execute("select variable, value from variables")
    rows = cur.fetchall()
    for r in rows:
        dataTwo = r[1]
        await ctx.send("dataTwo is " + str(dataTwo))
        
client.run(os.environ['discord_token'])
cur.close()
con.close()
