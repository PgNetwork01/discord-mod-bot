import discord
from discord.ext import commands, tasks
from discord import app_commands
from datetime import datetime, timedelta
import asyncio
import random

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(help="Adds an emote to the server.")
    @commands.has_permissions(manage_emojis=True)
    async def addemote(self, ctx, name: str, image: str = None):
        if ctx.message.attachments:
            image = await ctx.message.attachments[0].read()
        elif image:
            async with self.bot.session.get(image) as resp:
                if resp.status != 200:
                    return await ctx.send("Could not download file.")
                image = await resp.read()
        else:
            return await ctx.send("You must provide an image link or attach an image.")

        emoji = await ctx.guild.create_custom_emoji(name=name, image=image)
        await ctx.send(f"Added emote: <:{emoji.name}:{emoji.id}>")

    @app_commands.command(name="addemote", description="Adds an emote to the server.")
    @app_commands.checks.has_permissions(manage_emojis=True)
    async def addemote_slash(self, interaction: discord.Interaction, name: str, image: str = None):
        if interaction.message.attachments:
            image = await interaction.message.attachments[0].read()
        elif image:
            async with self.bot.session.get(image) as resp:
                if resp.status != 200:
                    return await interaction.response.send_message("Could not download file.")
                image = await resp.read()
        else:
            return await interaction.response.send_message("You must provide an image link or attach an image.")

        emoji = await interaction.guild.create_custom_emoji(name=name, image=image)
        await interaction.response.send_message(f"Added emote: <:{emoji.name}:{emoji.id}>")

    @commands.command(help="Add a moderator role.")
    @commands.has_permissions(manage_roles=True)
    async def addmod(self, ctx, role: discord.Role):
        await ctx.send(f'Role {role.name} is now a moderator role.')

    @app_commands.command(name="addmod", description="Add a moderator role.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def addmod_slash(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f'Role {role.name} is now a moderator role.')

    @commands.command(help="Add a new server role, with optional color and hoist.")
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, name: str, color: str = None, hoist: bool = False):
        color = discord.Color(int(color.replace("#", ""), 16)) if color else discord.Color.default()
        role = await ctx.guild.create_role(name=name, color=color, hoist=hoist)
        await ctx.send(f'Created role {role.name}.')

    @app_commands.command(name="addrole", description="Add a new server role, with optional color and hoist.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def addrole_slash(self, interaction: discord.Interaction, name: str, color: str = None, hoist: bool = False):
        color = discord.Color(int(color.replace("#", ""), 16)) if color else discord.Color.default()
        role = await interaction.guild.create_role(name=name, color=color, hoist=hoist)
        await interaction.response.send_message(f'Created role {role.name}.')

    @commands.command(help="Send an announcement using the bot.")
    @commands.has_permissions(manage_channels=True)
    async def announce(self, ctx, channel: discord.TextChannel, *, message: str):
        await channel.send(message)
        await ctx.send(f'Announcement sent to {channel.mention}.')

    @app_commands.command(name="announce", description="Send an announcement using the bot.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def announce_slash(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        await channel.send(message)
        await interaction.response.send_message(f'Announcement sent to {channel.mention}.')

    @commands.command(help="Clear warnings from users.")
    @commands.has_permissions(manage_messages=True)
    async def clearwarn(self, ctx, member: discord.Member):
        await self.bot.db.execute("DELETE FROM warnings WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id))
        await self.bot.db.commit()
        await ctx.send(f'Cleared warnings for {member.mention}.')

    @app_commands.command(name="clearwarn", description="Clear warnings from users.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clearwarn_slash(self, interaction: discord.Interaction, member: discord.Member):
        await self.bot.db.execute("DELETE FROM warnings WHERE guild_id = ? AND user_id = ?", (interaction.guild.id, member.id))
        await self.bot.db.commit()
        await interaction.response.send_message(f'Cleared warnings for {member.mention}.')

    @commands.command(help="Enable or disable a command.")
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, command_name: str):
        command = self.bot.get_command(command_name)
        if command:
            command.enabled = not command.enabled
            status = "enabled" if command.enabled else "disabled"
            await ctx.send(f'Command {command_name} has been {status}.')
        else:
            await ctx.send(f'Command {command_name} not found.')

    @app_commands.command(name="command", description="Enable or disable a command.")
    @app_commands.checks.has_permissions(administrator=True)
    async def command_slash(self, interaction: discord.Interaction, command_name: str):
        command = self.bot.get_command(command_name)
        if command:
            command.enabled = not command.enabled
            status = "enabled" if command.enabled else "disabled"
            await interaction.response.send_message(f'Command {command_name} has been {status}.')
        else:
            await interaction.response.send_message(f'Command {command_name} not found.')

    @commands.command(help="List, show, enable or disable Custom Commands.")
    @commands.has_permissions(administrator=True)
    async def customs(self, ctx):
        await ctx.send('Custom Commands management is not implemented yet.')

    @app_commands.command(name="customs", description="List, show, enable or disable Custom Commands.")
    @app_commands.checks.has_permissions(administrator=True)
    async def customs_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message('Custom Commands management is not implemented yet.')

    @commands.command(help="Remove a moderator or moderator role.")
    @commands.has_permissions(manage_roles=True)
    async def delmod(self, ctx, role: discord.Role):
        await ctx.send(f'Role {role.name} is no longer a moderator role.')

    @app_commands.command(name="delmod", description="Remove a moderator or moderator role.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def delmod_slash(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f'Role {role.name} is no longer a moderator role.')

    @commands.command(help="Delete a server role.")
    @commands.has_permissions(manage_roles=True)
    async def delrole(self, ctx, role: discord.Role):
        await role.delete()
        await ctx.send(f'Deleted role {role.name}.')

    @app_commands.command(name="delrole", description="Delete a server role.")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def delrole_slash(self, interaction: discord.Interaction, role: discord.Role):
        await role.delete()
        await interaction.response.send_message(f'Deleted role {role.name}.')

    @commands.command(help="Make and manage giveaways.")
    @commands.has_permissions(manage_guild=True)
    async def giveaway(self, ctx):
        await ctx.send('Giveaway management is not implemented yet.')

    @app_commands.command(name="giveaway", description="Make and manage giveaways.")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def giveaway_slash(self, interaction: discord.Interaction):
        await interaction.response.send_message('Giveaway management is not implemented yet.')

    @commands.command(help="Toggles command usage for a channel. (Does not affect mods and managers)")
    @commands.has_permissions(manage_channels=True)
    async def ignorechannel(self, ctx, channel: discord.TextChannel):
        await ctx.send(f'Command usage toggled for {channel.mention}.')

    @app_commands.command(name="ignorechannel", description="Toggles command usage for a channel. (Does not affect mods and managers)")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def ignorechannel_slash(self, interaction: discord.Interaction, channel: discord.TextChannel):
        await interaction.response.send_message(f'Command usage toggled for {channel.mention}.')

    @commands.command(help="Toggles command usage for a role. (Does not affect mods and managers)")
    @commands.has_permissions(manage_roles=True)
    async def ignorerole(self, ctx, role: discord.Role):
        await ctx.send(f'Command usage toggled for role {role.name}.')

    @app_commands.command(name="ignorerole", description="Toggles command usage for a role. (Does not affect mods and managers)")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def ignorerole_slash(self, interaction: discord.Interaction, role: discord.Role):
        await interaction.response.send_message(f'Command usage toggled for role {role.name}.')

    @commands.command(help="Unban a user.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User):
        await ctx.guild.unban(user)
        await ctx.send(f'Unbanned {user.mention}.')

    @app_commands.command(name="unban", description="Unban a user.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def unban_slash(self, interaction: discord.Interaction, user: discord.User):
        await interaction.guild.unban(user)
        await interaction.response.send_message(f'Unbanned {user.mention}.')
        
    @commands.command(help="Kick a user.")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        try:
            if member.bot:
                await ctx.send(f"I cannot kick another bot: {member.mention}")
                return
            
            await member.kick(reason=reason)
            await ctx.send(f'Kicked {member.mention}')
        except discord.Forbidden:
            await ctx.send(f"I do not have permission to kick {member.mention}")
        except discord.HTTPException:
            await ctx.send(f"Failed to kick {member.mention}")

    @app_commands.command(name="kick", description="Kick a user.")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        try:
            if member.bot:
                await interaction.response.send_message(f"I cannot kick another bot: {member.mention}")
                return
            
            await member.kick(reason=reason)
            await interaction.response.send_message(f'Kicked {member.mention}')
        except discord.Forbidden:
            await interaction.response.send_message(f"I do not have permission to kick {member.mention}")
        except discord.HTTPException:
            await interaction.response.send_message(f"Failed to kick {member.mention}")

    @commands.command(help="Ban a user.")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        try:
            if member.bot:
                await ctx.send(f"I cannot ban another bot: {member.mention}")
                return
            
            await member.ban(reason=reason)
            await ctx.send(f'Banned {member.mention}')
        except discord.Forbidden:
            await ctx.send(f"I do not have permission to ban {member.mention}")
        except discord.HTTPException:
            await ctx.send(f"Failed to ban {member.mention}")

    @app_commands.command(name="ban", description="Ban a user.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban_slash(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        try:
            if member.bot:
                await interaction.response.send_message(f"I cannot ban another bot: {member.mention}")
                return
            
            await member.ban(reason=reason)
            await interaction.response.send_message(f'Banned {member.mention}')
        except discord.Forbidden:
            await interaction.response.send_message(f"I do not have permission to ban {member.mention}")
        except discord.HTTPException:
            await interaction.response.send_message(f"Failed to ban {member.mention}")

        
async def setup(bot):
    await bot.add_cog(Moderation(bot))
