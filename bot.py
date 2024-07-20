import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os
from dotenv import load_dotenv
import aiohttp
import sqlite3
import aiosqlite

load_dotenv()  # Load environment variables from .env file

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True

bot = commands.Bot(command_prefix=".", intents=intents)

async def load_extensions():
    extensions = ['moderation', 'ticketSystem', 'economy']  # Add other extensions as needed
    for extension in extensions:
        await bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await sync_commands(bot)
    botactivity = discord.Activity(type=discord.ActivityType.watching, name="Devs | .help")
    await bot.change_presence(activity=botactivity, status=discord.Status.do_not_disturb)

async def sync_commands(bot):
    await bot.tree.sync()
    print('Global slash commands synced.')
    
async def db_setup():
    bot.session = aiohttp.ClientSession()
    # Set up your database connection (example using SQLite)
    bot.db = sqlite3.connect('bot_database.db')
    bot.db = await aiosqlite.connect('economy.db')
    await bot.db.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        balance INTEGER,
        bank INTEGER,
        last_daily TIMESTAMP,
        inventory TEXT
    )''')
    await bot.db.commit()

bot.remove_command('help')

@commands.command(help="Displays this help message")
async def help(ctx):
    embed = discord.Embed(title="Help", description="List of available commands", color=0x00ff00)
    for command in bot.commands:
        embed.add_field(name=f'.{command.name}', value=command.help or "No description", inline=False)
    await ctx.send(embed=embed)

@app_commands.command(name="help", description="Displays this help message")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(title="Help", description="List of available commands", color=0x00ff00)
    for command in bot.commands:
        embed.add_field(name=f'/{command.name}', value=command.help or "No description", inline=False)
    await interaction.response.send_message(embed=embed)

async def main():
    async with bot:
        await db_setup()
        await load_extensions()
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))

if __name__ == "__main__":
    asyncio.run(main())
