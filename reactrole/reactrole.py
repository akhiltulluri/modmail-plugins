import typing
import emoji

import discord
from discord.ext import commands, tasks

class UnicodeEmoji(commands.Converter):
    async def convert(self, ctx, argument):
        if argument in emoji.UNICODE_EMOJI:
            return discord.PartialEmoji(name=argument, animated=False)
        raise commands.BadArgument('Unknown emoji')

Emoji = typing.Union[discord.PartialEmoji, UnicodeEmoji]

class ReactionRole(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
    
    
    @commands.group(invoke_without_command=True,aliases=['rr'])
    async def reactrole(self,ctx):
        await ctx.send_help(ctx.command)
        
    @reactrole.command(name="add",aliases=["+"])
    async def add_reactrole(self,ctx,message:discord.Message,emoji:Emoji,role:discord.Role):
        await self.db.insert_one({
        'guild_id':str(ctx.guild.id),
        'msg_id':str(message.id),
        'emoji':str(emoji),
        'role':str(role.id),
        'locked':False,
        'drop':False,
        'blacklist':[],
        'whitelist':[],
        'verify':False,
        'limit':None,
        'reversed':False,
        })
        await message.add_reaction(emoji)
        await ctx.send(f'{emoji}-{role} added to that message')
        
    
    @commands.Cog.listener('on_raw_reaction_add')
    @commands.Cog.listener('on_raw_reaction_remove')
    async def reactrole_handler(self, payload):
        if payload.guild_id is None:
            return
            
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member.bot:
            return
        data = await self.db.find_one(
        {
        'guild_id':str(payload.guild_id),
        'msg_id':str(payload.message_id),
        'emoji':str(payload.emoji)
        })
        if not data:
            return
        role_id = data["role"]
        role = guild.get_role(role_id)
        roles = member.roles
        blacklisted = False
        allowed = True if data['whitelisted'] == [] else False
        if not allowed:
            for role in roles:
                if role.id in data['whitelisted']:
                    allowed = True
                    return
        for role in roles:
            if role.id in data['blacklisted']:
                blacklisted = True
                return
        action = member.add_roles if payload.event_type == "REACTION_ADD" else member.remove_roles
        if data['locked']:
            action = None
        if blacklisted:
            action = None
        if allowed:
            action = None                
        if data['drop']:
            if action == member.add_roles or role not in roles:
                action = None
        if data['verify']:
            if action == member.remove_roles or role in roles:
                action = None
        linked_roles = []
        if data['limit'] != None:
            limit = int(data['limit'])
            cursor = await self.db.find({'message_id':str(payload.message_id)})
            async for doc in cursor:
                linked_roles.append(doc['role'])
            num = len(linked_roles)
            if limit > num:
                return
            else:
                common = 0
                for role in roles:
                    if str(role.id) in linked_roles:
                        common +=1
                if common > limit:
                    action=None
        if action != None:
            if reversed:
                action = member.remove_roles if action == member.add_roles else member.add_roles
            await action(role)
                        
                
            
        
        
            
                
                
            
               
def setup(bot):
    bot.add_cog(ReactionRole(bot))            
            
              
        
        
        
