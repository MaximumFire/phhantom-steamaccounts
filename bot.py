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
lineCount = None

#Events
@client.event
async def on_ready():
    global lineCount
    global con
    global cur
    print("Bot is online.")
    await client.change_presence(activity=discord.Game(name="Type .help for help"))
    cur.execute("select * from variables")
    tableData = cur.fetchall()
    for row in tableData:
        lineCount = row[1]
    print("lineCount has been set to: " + str(lineCount))
    cur.execute("drop table if exists steamAccounts")
    cur.execute("create table steamAccounts (id int, username varchar(50), password varchar(50))")
    with open('steam_accounts.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            cur.execute(
            "insert into steamAccounts values (%s, %s, %s)",
            row)
    print("steam accounts imported")
    

#Commands
@client.command()
async def help(ctx):
    await ctx.send("Use the '.getSteamAcc @yourNameHere' to get an account")

@client.command()
async def setLineCount(ctx, *, number):
    global lineCount
    global con
    global cur
    cur.execute("select * from variables")
    newLineCount = number
    cur.execute("update variables set value = %s where variable = 'lineCount'", [newLineCount])
    cur.execute("select * from variables")
    tableData = cur.fetchall()
    for row in tableData:
        lineCount = row[1]
    await ctx.send("lineCount has been updated to: " + lineCount)
    print("lineCount is: " + lineCount)
    else:
        await ctx.send("This command is only availiable for Owners.")

@client.command()
async def checkLineCount(ctx):
    global line_count
    print("line_count is: " + str(lineCount))
    await ctx.send("lineCount is: " + str(lineCount))
    
client.run(os.environ['discord_token'])
cur.close()
con.close()
