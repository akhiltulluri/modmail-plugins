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

    @reactrole.command(name="list")
    async def list_rr(self,ctx,message:discord.Message):
        cursor =  self.db.find({"msg_id":str(message.id)})
        role_list = []
        emoji_list = []
        async for doc in cursor:
            role_list.append(doc["role"])
            emoji_list.append(doc["emoji"])
            
        description = f"Message: [Click here]({message.jump_url}) to see the message."                    
        for role in role_list:
            ind = role_list.index(role)
            rol = ctx.guild.get_role(int(role))
            related_emoji = emoji_list[ind]         
            try:              
                emoji = self.bot.get_emoji(int(related_emoji))
            except ValueError:
                emoji = related_emoji
            description += f"\n{rol}  \U000027a1  {emoji}\n"
        embed = discord.Embed(title=f"Reaction roles mapping",description=description)
        await ctx.send(embed=embed)  
                        
    @reactrole.command(name="blacklist",aliases=["bl"])
    async def blacklist_roles(self,ctx,message:discord.Message,add:bool,roles:commands.Greedy[discord.Role]):
        if add:
            role_ids = []        
            reply = ""
            for role in roles:
                reply += f' {role}'
                role_ids.append(str(role.id))     
            await self.db.update_many({'msg_id':str(message.id)},{"$set":{"blacklist":role_ids}})
            
            await ctx.send(f"Successfully Blacklisted{reply} role(s)!!")
        if not add:
            current_blacklisted = (await self.db.find_one({'msg_id':str(message.id)}))['blacklist']
            reply1=""
            common_roles = []
            for rol in roles:
                if str(rol.id) in current_blacklisted:
                    common_roles.append(str(rol.id))
                    reply1 += f' {rol}'
                   
            if not common_roles:
                return await ctx.send("The roles provided are not blacklisted!")
            new_blacklist = []
        
            for rol1 in current_blacklisted:
                if rol1 not in common_roles:
                    new_blacklist.append(rol1)
            await self.db.update_many({'msg_id':str(message.id)},{"$set":{"blacklist":new_blacklist}})
            await ctx.send(f"Succefully removed{reply1} from Blacklist!")
        
                
        
        
        
        
        
    @reactrole.command(name="remove",aliases=["-"])
    async def remove_reactrole(self,ctx,message:discord.Message,emoji:Emoji,role:discord.Role):
        member = ctx.guild.get_member(self.bot.user.id)
        emote = str(emoji) if emoji.id is None else str(emoji.id)
        await self.db.delete_one(
        {
        'guild_id':str(ctx.guild.id),
        'msg_id':str(message.id),
        'emoji':emote
        })
        await message.remove_reaction(emoji,member)  
        await ctx.send(f'Removed {emoji} for role {role}')    
         
    @reactrole.command(name="add",aliases=["+"])
    async def add_reactrole(self,ctx,message:discord.Message,emoji:Emoji,role:discord.Role):
        emote = str(emoji) if emoji.id is None else str(emoji.id)
        await self.db.insert_one({
        'guild_id':str(ctx.guild.id),
        'msg_id':str(message.id),
        'emoji':emote,
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
        await ctx.send(f'Added {emoji} for the role {role}')
        
    
    
    @commands.Cog.listener('on_raw_reaction_remove')
    async def remove_reactrole_handler(self, payload):
        print("reaction removed")
        if payload.guild_id is None:
            return
            
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        
        if member.bot:
            return
        emoji = str(payload.emoji) if payload.emoji.id is None else str(payload.emoji.id)
        data = await self.db.find_one(
        {
        'guild_id':str(payload.guild_id),
        'msg_id':str(payload.message_id),
        'emoji':emoji
        })
        print(data)
        if not data:
            return
        role_id = int(data["role"])
        role = guild.get_role(role_id)
        roles = member.roles
        blacklisted = False
        allowed = True if data['whitelist'] == [] else False
        if not allowed:
            for rol in roles:
                if str(rol.id) in data['whitelist']:
                    allowed = True
                    return
        for rol1 in roles:
            if str(rol1.id) in data['blacklist']:
                blacklisted = True
                return
        action = member.remove_roles
        if data['locked']:
            action = None
            print("Locked")
        if blacklisted:
            action = None
            print("Blacklisted")
        if not allowed:
            action = None 
            print("Not allowed")               
        if data['drop']:
            if role not in roles:
                action = None
                print("Drop")
        if data['verify']:            
            action = None
            print("Verify")
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
                for rol2 in roles:
                    if str(rol2.id) in linked_roles:
                        common +=1
                if common > limit:
                    action=None
                    print("limit")
        if action != None:
            if data['reversed']:
                action = member.add_roles
            await action(role)
            #print(role)
            print(action)
        else:
            print("Action none")
                        
    @commands.Cog.listener('on_raw_reaction_add')                
    async def add_reactrole_handler(self, payload):
        if payload.guild_id is None:
            return
            
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member.bot:
            return
        emoji = str(payload.emoji) if payload.emoji.id is None else str(payload.emoji.id)
        data = await self.db.find_one(
        {
        'guild_id':str(payload.guild_id),
        'msg_id':str(payload.message_id),
        'emoji':emoji
        })
        print(f'{payload.emoji}')
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
                if str(rol.id) in data['whitelist']:
                    allowed = True
                    return
        for rol1 in roles:
            if str(rol1.id) in data['blacklist']:
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
                for rol2 in roles:
                    if str(rol2.id) in linked_roles:
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
            
              
        
        
        
