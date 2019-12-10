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
        
    
    
    @commands.Cog.listener('on_raw_reaction_remove')
    async def remove_reactrole_handler(self, payload):
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
        role_id = int(data["role"])
        role = guild.get_role(role_id)
        roles = member.roles
        blacklisted = False
        allowed = True if data['whitelist'] == [] else False
        if not allowed:
            for rol in roles:
                if rol.id in data['whitelist']:
                    allowed = True
                    return
        for rol in roles:
            if rol.id in data['blacklist']:
                blacklisted = True
                return
        action = member.remove_roles
        if data['locked']:
            action = None
        if blacklisted:
            action = None
        if not allowed:
            action = None                
        if data['drop']:
            if role not in roles:
                action = None
        if data['verify']:            
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
                for rol in roles:
                    if str(rol.id) in linked_roles:
                        common +=1
                if common > limit:
                    action=None
        if action != None:
            if data['reversed']:
                action = member.add_roles
            await action(role)
            print(role)
                        
    @commands.Cog.listener('on_raw_reaction_add')                
    async def add_reactrole_handler(self, payload):
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
        role_id = int(data["role"])
        role = guild.get_role(role_id)
        print(role)
        roles = member.roles
        blacklisted = False
        allowed = True if data['whitelist'] == [] else False
        if not allowed:
            for rol in roles:
                if rol.id in data['whitelist']:
                    allowed = True
                    return
        for rol in roles:
            if rol.id in data['blacklist']:
                blacklisted = True
                return
        action = member.add_roles 
        if data['locked']:
            action = None
            print('Locked is True')
        if blacklisted:
            action = None
            print('Blacklisted is True')
        if not allowed:
            action = None
            print('Allowed is True')                
        if data['drop']:            
            action = None
            print('Drop is true')
        if data['verify']:
            if role in roles:
                action = None
                print('Verify is true')
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
                for rol in roles:
                    if str(rol.id) in linked_roles:
                        common +=1
                if common > limit:
                    action=None
                    print('Common > Limit')
        if action != None:
            if data['reversed']:
                action = member.remove_roles
            await action(role)  
            print(role)       
        else:
            print('Action is None')
        
            
                
                
            
               
def setup(bot):
    bot.add_cog(ReactionRole(bot))            
            
              
        
        
        
