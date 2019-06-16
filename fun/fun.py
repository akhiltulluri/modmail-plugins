import logging
from enum import Enum
from random import randint,choice
import discord
from discord.ext import commands
from dadjokes import Dadjoke
from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, "Cog", object)

logger = logging.getLogger("Modmail")


def escape(text: str, *, mass_mentions: bool = False, formatting: bool = False) -> str:
    """Get text with all mass mentions or markdown escaped.

    Parameters
    ----------
    text : str
        The text to be escaped.
    mass_mentions : `bool`, optional
        Set to :code:`True` to escape mass mentions in the text.
    formatting : `bool`, optional
        Set to :code:`True` to escpae any markdown formatting in the text.

    Returns
    -------
    str
        The escaped text.

    """
    if mass_mentions:
        text = text.replace("@everyone", "@\u200beveryone")
        text = text.replace("@here", "@\u200bhere")
    if formatting:
        text = text.replace("`", "\\`").replace("*", "\\*").replace("_", "\\_").replace("~", "\\~")
    return text

class RPS(Enum):
    rock = "\N{MOYAI}"
    paper = "\N{PAGE FACING UP}"
    scissors = "\N{BLACK SCISSORS}"

class RPSParser:
    def __init__(self, argument):
        argument = argument.lower()
        if argument == "rock":
            self.choice = RPS.rock
        elif argument == "paper":
            self.choice = RPS.paper
        elif argument == "scissors":
            self.choice = RPS.scissors
        else:
            self.choice = None
class Fun(Cog):
  
    ball = [
        "As I see it, yes",
        "It is certain",
        "It is decidedly so",
        "Most likely",
        "Outlook good",
        "Signs point to yes",
        "Without a doubt",
        "Yes",
        "Yes – definitely",
        "You may rely on it",
        "Reply hazy, try again",
        "Ask again later",
        "Better not tell you now",
        "Cannot predict now",
        "Concentrate and ask again",
        "Don't count on it",
        "My reply is no",
        "My sources say no",
        "Outlook not so good",
        "Very doubtful"
    ]
    def __init__(self,bot):
        super().__init__()
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        
    @commands.command()
    async def choose(self, ctx, *choices):
        """Choose between multiple options.

        To denote options which include whitespace, you should use
        double quotes.
        """
        choices = [escape(c, mass_mentions=True) for c in choices]
        if len(choices) < 2:
            await ctx.send(_("Not enough options to pick from."))
        else:
            await ctx.send(choice(choices))
            
    @commands.command()
    async def roll(self, ctx, number: int = 100):
        """Roll a random number.

        The result will be between 1 and `<number>`.

        `<number>` defaults to 100.
        """
        author = ctx.author
        if number > 1:
            n = randint(1, number)
            await ctx.send("{author.mention} :game_die: {n} :game_die:".format(author=author, n=n))
        else:
            await ctx.send(_("{author.mention} Maybe higher than 1? ;P").format(author=author))
            
    @commands.command()
    async def flip(self,ctx):
        """Flip a coin"""
        choice = choice["HEADS!*","TAILS!*"]
        await ctx.send(f"*Flips a coin and...{choice}")
        
    @commands.command()
    async def rps(self,ctx,your_choice:RPSParser):
        """Play Rock,Paper,Scissors"""
        author = ctx.author
        player_choice = your_choice.choice
        if not player_choice:
            return await ctx.send("This isn't a valid option. Try rock, paper, or scissors.")
        bot_choice = choice((RPS.rock, RPS.paper, RPS.scissors))
        cond = {
            (RPS.rock, RPS.paper): False,
            (RPS.rock, RPS.scissors): True,
            (RPS.paper, RPS.rock): True,
            (RPS.paper, RPS.scissors): False,
            (RPS.scissors, RPS.rock): False,
            (RPS.scissors, RPS.paper): True,
        }
        if bot_choice == player_choice:
            outcome = None  # Tie
        else:
            outcome = cond[(player_choice, red_choice)]
        if outcome is True:
            await ctx.send(f"{bot_choice} You win {author.mention}!")
        elif outcome is False:
            await ctx.send(f"{bot_choice} You lose {author.mention}!")
        else:
            await ctx.send(f"{bot_choice} We're square {author.mention}!")
    @commands.command(name="8")
    async def 8ball(self, ctx, *, question: str):
        """Ask 8 ball a question.

        Question must end with a question mark.
        """
        if question.endswith("?") and question != "?":
            await ctx.send((choice(self.ball)))
        else:
            await ctx.send("That doesn't look like a question.")

    @commands.command(aliases=["badjoke"])
    async def dadjoke(self,ctx):
        joke = Dadjoke()
        await ctx.send(joke)
        
    @commands.command()
    async def google(self, ctx, *, search_terms: str):
        """Create a lmgtfy link."""
        search_terms = escape(
            search_terms.replace("+", "%2B").replace(" ", "+"), mass_mentions=True
        )
        await ctx.send("https://lmgtfy.com/?q={}".format(search_terms))

def setup(bot):
    bot.add_cog(Fun(bot))    





        
    
    

    
    