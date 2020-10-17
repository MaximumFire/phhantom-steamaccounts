import discord
from discord.ext import commands
import csv

class SteamAccount(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("SteamAccount cog is loaded.")

def setup(client):
    client.add_cog(SteamAccount(client))
