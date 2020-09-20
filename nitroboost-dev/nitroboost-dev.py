import discord
from discord.ext import commands,tasks
import string

from core import checks
from core.models import PermissionLevel

# Credit: https://github.com/fourjr/modmail-plugins/blob/master/welcomer/models.py
class SafeFormat(object):
    def __init__(self, **kw):
        self.__dict = kw

    def __getitem__(self, name):
        return self.__dict.get(name, SafeString('{%s}' % name))

class SafeString(str):
    def __getattr__(self, name):
        try:
            super().__getattr__(name)
        except AttributeError:
            return SafeString('%s.%s}' % (self[:-1], name))


def apply_vars(message, member):
    return string.Formatter().vformat(message, [], SafeFormat(
        booster=member
    ))


class NitroBoost(commands.Cog):
    """Plugin for sending custom announcement when a user boosts the server!"""

    def __init__(self, bot):
        self.bot = bot
        self.set_coll.start()

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def boosttoggle(self, ctx):
        """Turn on/off custom nitro boost message"""
        doc = await self.coll.get(str(ctx.guild.id))
        status = False
        channel = None
        message = "{booster.mention} has just boosted the server!"
        if doc:
            status = doc["on"]
            channel = doc["channel"]
            message = doc["message"]
        toSetStatus = not status
        message = "on" if toSetStatus else "off"
        await self.coll.set(str(ctx.guild.id),{"on": toSetStatus,"channel": channel,"message": message})
        await ctx.send(f"Successfully turned {message} custom nitro boost announcements for this server!")

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def boostmessage(self, ctx,*, message: str):
        """Set custom message for boost announcements."""
        doc = await self.coll.get(str(ctx.guild.id))
        status = False
        channel = None
        if doc:
            status = doc["on"]
            channel = doc["channel"]
        await self.coll.set(str(ctx.guild.id),{"on": status,"channel": channel, "message": message})
        await ctx.send(f"Successfully set {message} as custom nitro boost announcements message for this server!")

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def boostchannel(self, ctx,channel: discord.TextChannel):
        """Set a channel for recieving nitro boost announcements"""
        doc = await self.coll.get(str(ctx.guild.id))
        status = True
        message = "{booster.mention} has just boosted the server!"
        if doc:
            status = doc["on"]
            message = doc["message"]
        await self.coll.set(str(ctx.guild.id),{"on": status,"channel": channel.id,"message": message})
        await ctx.send(f"Successfully set boost announcements to <#{channel.id}>! Use `boosttoggle` command to turn these on/off!")


    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def boostconfig(self, ctx):
        """Get server configuration for boost announcements"""
        doc = await self.coll.get(str(ctx.guild.id))
        message = "{booster.mention} has just boosted the server!"
        status = False
        channel = None
        if doc:
            channel = doc["channel"]
            status = doc["on"]
            message = doc["message"]
        statusMsg = "On" if status else "Off"
        channelMsg = f"<#{channel}>" if channel else None
        embed = discord.Embed(title="Boost config", color = discord.Color.blue())
        embed.add_field(name="Toggle",value=statusMsg,inline=False)
        embed.add_field(name="Channel",value=channelMsg,inline=False)
        embed.add_field(name="Message",value=message)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.premium_since is None and after.premium_since is not None:
            await on_nitro_boost(after)

    async def on_nitro_boost(self,booster):
        doc = await self.coll.get(str(booster.guild.id))
        message = "{booster.mention} has just boosted the server!"
        status = False
        channel = None
        if doc:
            channel = doc["channel"]
            status = doc["on"]
            message = doc["message"]
        if status: # Toggled announcements
            if channel: # If channel is configured
                guild = self.bot.get_guild(booster.guild.id)
                textchannel = guild.get_channel(channel) # Get channel object 
                if textchannel: # If channel exists
                    message = apply_vars(message,booster)
                    embed = discord.Embed(description=message)
                    embed.set_author(name="🎉🎉 BOOSTER PARTY 🎉🎉",icon_url="https://media.discordapp.net/attachments/511385199612002304/757139558419923016/nitro.gif")
                    embed.set_thumbnail(url=booster.avatar_url)
                    footText= f"Server Boosted 🎉({booster.id})"
                    embed.set_footer(text=footText,icon_url="https://media.discordapp.net/attachments/511385199612002304/757139590246170665/heart.gif")
                    await textchannel.send(embed=embed)

    @tasks.loop(count=1)
    async def set_coll(self):
        self.coll = await self.bot.api.get_plugin_client(self)

    @set_coll.before_loop
    async def before_set_coll(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(NitroBoost(bot))
