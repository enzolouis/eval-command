import typing
import asyncio
import io
import traceback
import aiohttp
import discord

from textwrap import indent
from contextlib import redirect_stdout
from discord.ext import commands

PREFIXES = ["/"] # you can specify more prefixes.
TOKEN = "" # bot's token

bot = commands.Bot(command_prefix=PREFIXES)


class Eval(commands.Cog):
    """
    Evaluate your code asynchronously with bot action like create channel, ...
    You can return an object, if this object is not None surely, you will have (with your output) 
    the return description with the object, his type, lenght, and dir
    """
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def py(text:str) -> str:
        """
        Format text to a python markdown
        """
        return f"```py\n{text}\n```"

    async def wait_until_react(self, ctx, msg:discord.Message) -> None:
        """
        Add reaction :boom: to the return value, if the author click on, the return will
        be deleted
        """
        await msg.add_reaction("\N{COLLISION SYMBOL}")

        def check(react, author):
            return author == ctx.author and str(react.emoji) == "\N{COLLISION SYMBOL}" and react.message.id == msg.id
        
        try:
            await self.bot.wait_for("reaction_add", check=check, timeout=60)
        except asyncio.TimeoutError:
            await msg.clear_reactions()
        else:
            await msg.delete()

    @commands.command(name="eval")
    async def eval_(self, ctx, *, code):
        """
        Try your python codes directly on discord
        `eval_` name to don't bloc `eval` builtin function
        If her name was `eval`, no consequence happen in !eval <code>... 
        but errors can happen in other code in that file
        """
        # :white_check_mark: and :x: in discord
        tick = "\N{WHITE HEAVY CHECK MARK}"
        error = "\N{CROSS MARK}"

        py = Eval.py # quickly

        env = {
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
            "bot":self.bot,
        }

        buffer = io.StringIO()

        # create asynchronous function environment to execute await instruction.
        async_code = f"async def func():\n{indent(code, '    ')}"
        # using textwrap :
        # async def func():
        #    code
        #    code
        # not using textwrap :
        # async def fucn():
        # code
        # code
        # INVALID SYNTAX

        try:
            with redirect_stdout(buffer): # OPTIONNAL IN A LOT OF CODE CASE | redirect only stdout and don't send in console, only in discord
                exec(async_code, env) # exec async code with env, in order to have an access to variable like ctx, bot, ... (see `env` var)

        except Exception as e: # here catch invalid syntax (not runtime error)
            msg = await ctx.send(py(f"{e.__class__.__name__}: {e}"))
            await ctx.message.add_reaction(error)
            return await self.wait_until_react(ctx, msg) # even if error happen, :boom: react must be here

        func = env['func'] # get func from env. func is in env at this line : exec(code, env)
        try:
            with redirect_stdout(buffer): # redirect only stdout and don't send in console, only in discord
                return_ = await func() # here catch runtime error
        except Exception as e:
            value = buffer.getvalue()
            msg = await ctx.send(py(f"{value}{traceback.format_exc()}")) # traceback.format_exc to retrace context exception
            await ctx.message.add_reaction(error)
            return await self.wait_until_react(ctx, msg) # even if error happen, :boom: react must be here
        
        # if 0 error :

        value = buffer.getvalue()

        if return_ is None and not value:
            return await ctx.message.add_reaction(tick)

        to_send = ""

        if value:
            to_send = value
        if return_ is not None:

            to_send = to_send + f"\n\n<Return>\n{return_}\n<Return type>\n{return_.__class__.__name__}\n\n<Return dir>\n{dir(return_)}"
        

        if len(to_send) < 1980: # 2000 -> discord messages length limit
            msg = await ctx.send(py(to_send))
            await ctx.message.add_reaction(tick)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.post("https://hastebin.com/documents", data=to_send) as response:
                    if response.status == 200: # 200 : check
                        code = (await response.json())["key"]
                        msg = await ctx.send(f":white_check_mark: <https://hastebin.com/{code}>")
                    else:
                        return await ctx.send("Problem with <https://hastebin.com/>...")
        
        await self.wait_until_react(ctx, msg)

class TokenError(Exception):
    pass

if __name__ == "__main__":
    bot.add_cog(Eval(bot))
    try:
        bot.run(TOKEN)
    except Exception as e:
        e = getattr(e, "original", e) # discord.py exception handler system..
        if isinstance(e, discord.errors.LoginFailure):
            # e.__class__ -> first `type` function form. But type(e).__name__ is not explicit
            raise TokenError(f"{e.__class__.__name__} - Your token can be the problem cause -> https://discordapp.com/developers/applications/YOUR_BOT_ID/bot \
             to find your bot token.") from e # not from None cause user can think token is the only one problem
