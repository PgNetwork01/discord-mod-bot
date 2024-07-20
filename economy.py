import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
import random
import json

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_user(self, user_id):
        async with self.bot.db.execute("SELECT balance, bank, last_daily, inventory FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

    async def create_user(self, user_id):
        await self.bot.db.execute("INSERT OR IGNORE INTO users (user_id, balance, bank, last_daily, inventory) VALUES (?, ?, ?, ?, ?)",
                                  (user_id, 0, 0, None, json.dumps({"hunt": [], "dig": []})))
        await self.bot.db.commit()

    @commands.command(help="Claim your daily reward.")
    async def daily(self, ctx):
        await self.create_user(ctx.author.id)
        user = await self.get_user(ctx.author.id)
        last_daily = user[2]
        now = datetime.utcnow()
        if last_daily and (now - datetime.fromisoformat(last_daily)) < timedelta(days=1):
            await ctx.send("You have already claimed your daily reward. Try again later.")
        else:
            reward = random.randint(50, 100)
            await self.bot.db.execute("UPDATE users SET balance = balance + ?, last_daily = ? WHERE user_id = ?", (reward, now.isoformat(), ctx.author.id))
            await self.bot.db.commit()
            await ctx.send(f"You have received your daily reward of {reward} coins!")

    @app_commands.command(name="daily", description="Claim your daily reward.")
    async def daily_slash(self, interaction: discord.Interaction):
        await self.create_user(interaction.user.id)
        user = await self.get_user(interaction.user.id)
        last_daily = user[2]
        now = datetime.utcnow()
        if last_daily and (now - datetime.fromisoformat(last_daily)) < timedelta(days=1):
            await interaction.response.send_message("You have already claimed your daily reward. Try again later.")
        else:
            reward = random.randint(50, 100)
            await self.bot.db.execute("UPDATE users SET balance = balance + ?, last_daily = ? WHERE user_id = ?", (reward, now.isoformat(), interaction.user.id))
            await self.bot.db.commit()
            await interaction.response.send_message(f"You have received your daily reward of {reward} coins!")

    @commands.command(aliases=["bal"], help="Check your balance.")
    async def balance(self, ctx):
        await self.create_user(ctx.author.id)
        user = await self.get_user(ctx.author.id)
        await ctx.send(f"Balance: {user[0]} coins\nBank: {user[1]} coins")

    @app_commands.command(name="balance", description="Check your balance.")
    async def balance_slash(self, interaction: discord.Interaction):
        await self.create_user(interaction.user.id)
        user = await self.get_user(interaction.user.id)
        await interaction.response.send_message(f"Balance: {user[0]} coins\nBank: {user[1]} coins")

    @commands.command(aliases=["dep"], help="Deposit coins into your bank.")
    async def deposit(self, ctx, amount: int):
        await self.create_user(ctx.author.id)
        user = await self.get_user(ctx.author.id)
        if amount > user[0]:
            await ctx.send("You don't have enough coins to deposit.")
        else:
            await self.bot.db.execute("UPDATE users SET balance = balance - ?, bank = bank + ? WHERE user_id = ?", (amount, amount, ctx.author.id))
            await self.bot.db.commit()
            await ctx.send(f"Deposited {amount} coins into your bank.")

    @app_commands.command(name="deposit", description="Deposit coins into your bank.")
    @app_commands.describe(amount="The amount of coins to deposit.")
    async def deposit_slash(self, interaction: discord.Interaction, amount: int):
        await self.create_user(interaction.user.id)
        user = await self.get_user(interaction.user.id)
        if amount > user[0]:
            await interaction.response.send_message("You don't have enough coins to deposit.")
        else:
            await self.bot.db.execute("UPDATE users SET balance = balance - ?, bank = bank + ? WHERE user_id = ?", (amount, amount, interaction.user.id))
            await self.bot.db.commit()
            await interaction.response.send_message(f"Deposited {amount} coins into your bank.")

    @commands.command(aliases=["wit"], help="Withdraw coins from your bank.")
    async def withdraw(self, ctx, amount: int):
        await self.create_user(ctx.author.id)
        user = await self.get_user(ctx.author.id)
        if amount > user[1]:
            await ctx.send("You don't have enough coins in your bank to withdraw.")
        else:
            await self.bot.db.execute("UPDATE users SET balance = balance + ?, bank = bank - ? WHERE user_id = ?", (amount, amount, ctx.author.id))
            await self.bot.db.commit()
            await ctx.send(f"Withdrew {amount} coins from your bank.")

    @app_commands.command(name="withdraw", description="Withdraw coins from your bank.")
    @app_commands.describe(amount="The amount of coins to withdraw.")
    async def withdraw_slash(self, interaction: discord.Interaction, amount: int):
        await self.create_user(interaction.user.id)
        user = await self.get_user(interaction.user.id)
        if amount > user[1]:
            await interaction.response.send_message("You don't have enough coins in your bank to withdraw.")
        else:
            await self.bot.db.execute("UPDATE users SET balance = balance + ?, bank = bank - ? WHERE user_id = ?", (amount, amount, interaction.user.id))
            await self.bot.db.commit()
            await interaction.response.send_message(f"Withdrew {amount} coins from your bank.")

    @commands.command(help="Hunt for animals.")
    async def hunt(self, ctx):
        await self.create_user(ctx.author.id)
        animals = ["shunk", "rabbit", "snake", "horse", "duck"]
        found = random.choice(animals)
        user = await self.get_user(ctx.author.id)
        inventory = json.loads(user[3])
        inventory["hunt"].append(found)
        await self.bot.db.execute("UPDATE users SET inventory = ? WHERE user_id = ?", (json.dumps(inventory), ctx.author.id))
        await self.bot.db.commit()
        await ctx.send(f"You went hunting and found a {found}!")

    @app_commands.command(name="hunt", description="Hunt for animals.")
    async def hunt_slash(self, interaction: discord.Interaction):
        await self.create_user(interaction.user.id)
        animals = ["shunk", "rabbit", "snake", "horse", "duck"]
        found = random.choice(animals)
        user = await self.get_user(interaction.user.id)
        inventory = json.loads(user[3])
        inventory["hunt"].append(found)
        await self.bot.db.execute("UPDATE users SET inventory = ? WHERE user_id = ?", (json.dumps(inventory), interaction.user.id))
        await self.bot.db.commit()
        await interaction.response.send_message(f"You went hunting and found a {found}!")

    @commands.command(help="Search for items.")
    async def search(self, ctx):
        await self.create_user(ctx.author.id)
        places = ["forest", "river", "mountain", "cave"]
        place = random.choice(places)
        found = f"something interesting in the {place}"
        await ctx.send(f"You searched the {place} and found {found}!")

    @app_commands.command(name="search", description="Search for items.")
    async def search_slash(self, interaction: discord.Interaction):
        await self.create_user(interaction.user.id)
        places = ["forest", "river", "mountain", "cave"]
        place = random.choice(places)
        found = f"something interesting in the {place}"
        await interaction.response.send_message(f"You searched the {place} and found {found}!")

    @commands.command(help="View your inventory.")
    async def inventory(self, ctx):
        await self.create_user(ctx.author.id)
        user = await self.get_user(ctx.author.id)
        inventory = json.loads(user[3])
        hunt_items = ', '.join(inventory["hunt"]) if inventory["hunt"] else 'None'
        dig_items = ', '.join(inventory["dig"]) if inventory["dig"] else 'None'
        await ctx.send(f"Hunt items: {hunt_items}\nDig items: {dig_items}")

    @app_commands.command(name="inventory", description="View your inventory.")
    async def inventory_slash(self, interaction: discord.Interaction):
        await self.create_user(interaction.user.id)
        user = await self.get_user(interaction.user.id)
        inventory = json.loads(user[3])
        hunt_items = ', '.join(inventory["hunt"]) if inventory["hunt"] else 'None'
        dig_items = ', '.join(inventory["dig"]) if inventory["dig"] else 'None'
        await interaction.response.send_message(f"Hunt items: {hunt_items}\nDig items: {dig_items}")

    @commands.command(help="Dig for worms.")
    async def dig(self, ctx):
        await self.create_user(ctx.author.id)
        found = "worm"
        user = await self.get_user(ctx.author.id)
        inventory = json.loads(user[3])
        inventory["dig"].append(found)
        await self.bot.db.execute("UPDATE users SET inventory = ? WHERE user_id = ?", (json.dumps(inventory), ctx.author.id))
        await self.bot.db.commit()
        await ctx.send(f"You dug in the ground and found a {found}!")

    @app_commands.command(name="dig", description="Dig for worms.")
    async def dig_slash(self, interaction: discord.Interaction):
        await self.create_user(interaction.user.id)
        found = "worm"
        user = await self.get_user(interaction.user.id)
        inventory = json.loads(user[3])
        inventory["dig"].append(found)
        await self.bot.db.execute("UPDATE users SET inventory = ? WHERE user_id = ?", (json.dumps(inventory), interaction.user.id))
        await self.bot.db.commit()
        await interaction.response.send_message(f"You dug in the ground and found a {found}!")

    @commands.command(help="Give coins to another user.")
    async def give(self, ctx, member: discord.Member, amount: int):
        await self.create_user(ctx.author.id)
        await self.create_user(member.id)
        user = await self.get_user(ctx.author.id)
        if amount > user[0]:
            await ctx.send("You don't have enough coins to give.")
        else:
            await self.bot.db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, ctx.author.id))
            await self.bot.db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, member.id))
            await self.bot.db.commit()
            await ctx.send(f"Gave {amount} coins to {member.mention}")

    @app_commands.command(name="give", description="Give coins to another user.")
    @app_commands.describe(member="The user to give coins to", amount="The amount of coins to give")
    async def give_slash(self, interaction: discord.Interaction, member: discord.Member, amount: int):
        await self.create_user(interaction.user.id)
        await self.create_user(member.id)
        user = await self.get_user(interaction.user.id)
        if amount > user[0]:
            await interaction.response.send_message("You don't have enough coins to give.")
        else:
            await self.bot.db.execute("UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, interaction.user.id))
            await self.bot.db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, member.id))
            await self.bot.db.commit()
            await interaction.response.send_message(f"Gave {amount} coins to {member.mention}")

async def setup(bot):
    await bot.add_cog(Economy(bot))
