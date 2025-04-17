import discord
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('ETHERYA')

client = discord.Client(intents=discord.Intents.all())

client.run(token=token)
