import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, "Cog", object)

class Suggestions(Cog):
    def __init__(self,bot):
        self.bot = bot
        self.coll = bot.plugin_db.get_partition(self)
        
    @commands.group(invoke_without_command=True,aliases=["ss"])
    @commands.guild_only()        @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def suggestionset(self,ctx: commands.Context):
        """Set up Suggestion Box for the server"""
        await ctx.send_help(ctx.command)
        
    @suggestionset.command()
    @commands.guild_only()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def output(self,ctx,channel: discord.TextChannel):
        """Set a channel for sending approved/denied suggestions. 
        
        Defaults to editing the suggestion embed"""
        guild = ctx.guild.id
        
        data = await self.coll.find_one({"_id":str(guild)})
        
        if data is None:                        
            await ctx.send("There's no channel configured for sending suggestion.Kindly set up a suggestion channel before setting up the output channel.To set up a suggestion channel use ```[p]suggestionset channel <channel>``` where [p] is your prefix")
        elif data["outcome_channel"] is not None:
            data.update({"$set":{"outcome_channel":str(channel.id)}})
            await ctx.send(f"Successfully updated outcome channel to <#{channel.id}>")
        elif data["outcome_channel"] is None:
            data.update({"$set":{"outcome_channel":str(channel.id)}})
            await ctx.send(f"Successfully set outcome channel to <#{channel.id}>")
            
                        
    @suggestionset.command()
    @commands.guild_only()
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def channel(self,ctx,channel:discord.TextChannel):
        """Set a channel for sending suggestions"""        
        guild = ctx.guild.id
        
        data = await self.coll.find_one({"_id":str(guild)})
        
        if data is None:
            
            await self.coll.insert_one({"_id":str(guild),"suggestion_channel":str(channel.id),"outcome_channel":None})
            await ctx.send(f"Successfully set suggestions channel to <#{channel.id}>")
        else:
            data.update({"$set":{"suggestion_channel":str(channel.id)}})
            await ctx.send(f"Successfully updated suggestions channel to <#{channel.id}>")

    @suggestionset.command()
    
        

    
    
    