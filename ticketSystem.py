import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ticket_category = None  # Will store the category where tickets will be created
        self.support_role_id = None  # ID of the role to be mentioned for support

    @commands.Cog.listener()
    async def on_ready(self):
        # Load ticket category and support role from config or database
        guild = self.bot.guilds[0]  # Assuming the bot is in only one guild
        self.ticket_category = discord.utils.get(guild.categories, name="Tickets")
        self.support_role_id = ...  # Set this to the ID of your support role

    @commands.command(help="Open a new ticket.")
    async def ticket(self, ctx, *, reason: str):
        await self.create_ticket(ctx.author, ctx.guild, reason)

    @app_commands.command(name="ticket", description="Open a new ticket")
    @app_commands.describe(reason="Reason for opening the ticket")
    async def ticket_slash(self, interaction: discord.Interaction, reason: str):
        await interaction.response.send_message("Creating ticket...", ephemeral=True)
        await self.create_ticket(interaction.user, interaction.guild, reason)
        
    async def create_ticket(self, user, guild, reason):
        if not self.ticket_category:
            self.ticket_category = await guild.create_category("Tickets")
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        if self.support_role_id:
            support_role = guild.get_role(self.support_role_id)
            overwrites[support_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{user.name}-{user.discriminator}",
            category=self.ticket_category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="New Ticket",
            description=f"User: {user.mention}\nReason: {reason}",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )

        await ticket_channel.send(embed=embed)
        await ticket_channel.send(f"{user.mention}, your ticket has been created.")
        
        if self.support_role_id:
            support_role = guild.get_role(self.support_role_id)
            await ticket_channel.send(f"{support_role.mention}, a new ticket has been opened.")
        
    @commands.command(help="Close the current ticket.")
    async def close(self, ctx):
        if ctx.channel.category != self.ticket_category:
            await ctx.send("This command can only be used in a ticket channel.")
            return
        
        await ctx.send("Closing ticket...")
        await ctx.channel.delete()

    @app_commands.command(name="close", description="Close the current ticket")
    async def close_slash(self, interaction: discord.Interaction):
        if interaction.channel.category != self.ticket_category:
            await interaction.response.send_message("This command can only be used in a ticket channel.", ephemeral=True)
            return
        
        await interaction.response.send_message("Closing ticket...", ephemeral=True)
        await interaction.channel.delete()

    @commands.command(help="Set the ticket category.")
    @commands.has_permissions(administrator=True)
    async def setcategory(self, ctx, *, category: discord.CategoryChannel):
        self.ticket_category = category
        await ctx.send(f"Ticket category set to {category.name}")

    @app_commands.command(name="setcategory", description="Set the ticket category")
    @commands.has_permissions(administrator=True)
    @app_commands.describe(category="The category for tickets")
    async def setcategory_slash(self, interaction: discord.Interaction, category: discord.CategoryChannel):
        self.ticket_category = category
        await interaction.response.send_message(f"Ticket category set to {category.name}", ephemeral=True)

    @commands.command(help="Set the support role.")
    @commands.has_permissions(administrator=True)
    async def setrole(self, ctx, role: discord.Role):
        self.support_role_id = role.id
        await ctx.send(f"Support role set to {role.name}")

    @app_commands.command(name="setrole", description="Set the support role")
    @commands.has_permissions(administrator=True)
    @app_commands.describe(role="The support role")
    async def setrole_slash(self, interaction: discord.Interaction, role: discord.Role):
        self.support_role_id = role.id
        await interaction.response.send_message(f"Support role set to {role.name}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
