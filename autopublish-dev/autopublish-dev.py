import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class AutoPublish(commands.Cog):
    """Auto Publish messages sent in announcement channels"""

    def __init__(self, bot):
        self.bot = bot
        self.coll = await bot.api.get_plugin_client(self)

    # Credit to codeinteger6 for this command's code
    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def publish(self, ctx, message_id: discord.Message):
        """Publish message sent in announcement channel.\n[Refer here](https://github.com/codeinteger6/modmail-plugins/blob/master/publish/README.md) for detailed guidance."""
        await message_id.publish()
        await ctx.send("Published message successfully.")

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def track(self, ctx, channel: discord.TextChannel):
        """Add announcement channels to track and auto publish announcements"""
        if not channel.is_news():
            return await ctx.send(
                f"{channel.mention} is not an announcement channel to track!"
            )
        doc = await self.coll.get(str(ctx.guild.id))
        if doc:
            channels = doc["channels"]
            if not channel.id in channels:
                channels.append(channel.id)
                await self.coll.set(str(ctx.guild.id),{"channels": channels})
            else:
                await ctx.send(f"Already tracking {channel.mention}!")
        else:
            channels = [channel.id]
            await self.coll.set(str(ctx.guild.id),{"channels": channels})
        return await ctx.send(
            f"Successfully added {channel.mention} to tracking list! All the messages sent there will now be auto published."
        )

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def remove(self, ctx, channel: discord.TextChannel):
        """Remove a channel from tracking"""
        doc = await self.coll.get(str(ctx.guild.id))
        if doc:
            channels = doc["channels"]
            if channel.id in channels:
                channels.remove(channel.id)
                await self.coll.set(str(ctx.guild.id),{"channels": channels})
                return await ctx.send(
                    f"Successfully removed {channel.mention} from tracking list! All the messages sent there will now not be auto published."
                )
            else:
                return await ctx.send(
                    f"{channel.mention} is not currently under tracking!"
                )
        else:
            return await ctx.send(
                f"Please atleast add one channel to tracking using `track` command before trying to remove."
            )

    @commands.command()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def listtracks(self, ctx):
        """List all the announcement channels that are being tracked for auto publishing"""
        doc = await self.coll.get(str(ctx.guild.id))
        if doc:
            channels = doc["channels"]
            if channels:
                msg = ""
                for channel in channels:
                    msg += f"<#{channel}>\n"
                embed = discord.Embed(
                    title="Tracking channels",
                    description=msg,
                    color=discord.Color.blue(),
                )
                return await ctx.send(embed=embed)
            else:
                return await ctx.send(
                    "Not tracking any announcement channels in this server!"
                )
        else:
            return await ctx.send(
                "Not tracking any announcement channels in this server!"
            )

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.channel.is_news():
            return  # Not an announcements channel
        guild_id = message.guild.id
        doc = await self.coll.get(str(guild_id))
        if not doc:
            return  # No tracking channels
        channels = doc["channels"]
        if not message.channel.id in channels:
            return  # Not tracking
        await message.publish()


def setup(bot):
    bot.add_cog(AutoPublish(bot))
