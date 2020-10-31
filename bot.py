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
    con.commit()
    

#Commands
@client.command()
async def help(ctx):
    await ctx.send("Use the '.getSteamAcc @yourNameHere' to get an account")

@client.command()
@cooldown(1, 3600, BucketType.user)
async def getSteamAcc(ctx, author):
    global lineCount
    global con
    global cur
    if "verified" in [i.name.lower() for i in ctx.author.roles]:
        lineCount = lineCount + 1
        print("lineCount is now: " + str(lineCount))
        cur.execute("select * from steamAccounts")
        tableData = cur.fetchall()
        loop = 0
        for row in tableData:
            loop = loop + 1
            if loop == lineCount:
                if row[1] == "":
                    await ctx.send("There are no more accounts availiable. Contact @MaximumFire for help.")
                else:
                    await ctx.author.send("Your username is: " + row[1])
                    await ctx.author.send("Your password is: " + row[2])
        cur.execute("select * from variables")
        newLineCount = lineCount
        cur.execute("update variables set value = %s where variable = 'lineCount'", [newLineCount])
        cur.execute("select * from variables")
        tableData = cur.fetchall()
        for row in tableData:
            lineCount = row[1]
        await ctx.send("lineCount has been updated to: " + str(lineCount))
        print("lineCount is: " + str(lineCount))
        con.commit()
    else:
        await ctx.send("This Command is only availiable for @verified")

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
async def clearCooldown(ctx):
    if "owner" in [i.name.lower() for i in ctx.author.roles]:
        getSteamAcc.reset_cooldown(ctx)
        await ctx.send("Cooldown reset.")
    else:
        await ctx.send("This command is only for owner.")
        
@client.command()
async def setLineCount(ctx, *, number):
    if "owner" in [i.name.lower() for i in ctx.author.roles]:
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
        await ctx.send("lineCount has been updated to: " + str(lineCount))
        print("lineCount is: " + str(lineCount))
        con.commit()
    else:
        await ctx.send("This command is only for owner.")

@client.command()
async def checkLineCount(ctx):
    if "owner" in [i.name.lower() for i in ctx.author.roles]:
        global line_count
        print("line_count is: " + str(lineCount))
        await ctx.send("lineCount is: " + str(lineCount))
    else:
        await ctx.send("This command is only for owner.")
    
client.run(os.environ['discord_token'])
con.commit()
cur.close()
con.close()
