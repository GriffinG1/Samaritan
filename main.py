import discord
import os
import json
import config
import datetime
import traceback
from discord.ext import commands

description = "A bot written in Python by GriffinG1 for keeping a to-do list."

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

prefix = config.prefix
token = config.token

if not token:
    exit('Bot shut down: no token given in config.py')
elif not prefix or not len(prefix[0]) > 0:
    exit('Bot shut down: No prefixes given in config.py')

bot = commands.Bot(command_prefix=prefix, description=description)

if not os.path.exists('saves'):
    os.mkdir('saves')


# mostly taken from https://github.com/Rapptz/discord.py/blob/async/discord/ext/commands/bot.py
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.errors.CommandNotFound):
        pass  # ...don't need to know if commands don't exist
    elif isinstance(error, discord.ext.commands.errors.MissingRequiredArgument):
        await ctx.send("You are missing required arguments.")
        await ctx.send_help(ctx.command)
    elif isinstance(error, discord.ext.commands.errors.BadArgument):
        await ctx.send("A bad argument was provided, please try again.")
    else:
        if ctx.command:
            await ctx.send("An error occurred while processing the `{}` command.".format(ctx.command.name))
        print('Ignoring exception in command {0.command} in {0.message.channel}'.format(ctx))
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        error_trace = "".join(tb)
        print(error_trace)


@bot.event
async def on_error(event_method, *args, **kwargs):
    print(args[0])
    if isinstance(args[0], commands.errors.CommandNotFound):
        return
    print("Ignoring exception in {}".format(event_method))
    tb = traceback.format_exc()
    error_trace = "".join(tb)
    print(error_trace)


@bot.event
async def on_ready():
    bot.creator = await bot.fetch_user(177939404243992578)
    for guild in bot.guilds:
        try:
            bot.guild = guild
            if not os.path.exists('saves/{}.json'.format(str(guild.id))):
                with open('saves/{}.json'.format(str(guild.id)), 'w') as f:
                    f.write('{}')
            with open('saves/{}.json'.format(str(guild.id)), 'r') as f:
                bot.todo_dict = json.load(f)
            print(f"Initialized on {guild.name}.")
        except Exception as e:
            print(f"Failed to initialize on {guild.name}.\n{type(e).__name__}: {e}")

try:
    bot.load_extension('todo')
except Exception as e:
    print(f'Failed to load todo.py.\n{type(e).__name__}: {e}')
    exit('Bot shut down: todo not loaded')


@bot.command()
async def reload(ctx):
    """Reloads todo.py"""
    if not ctx.author == ctx.guild.owner and not ctx.author == bot.creator:
        return await ctx.send("This command is restricted to the guild owner and bot creator!")
    try:
        bot.reload_extension('todo')
    except Exception as e:
        return await ctx.send(f"Failed to reload `todo.py`. Raised error: ```{type(e).__name__}: {e}```")
    await ctx.send("Successfully reloaded `todo.py`!")


@bot.command(hidden=True)  # taken from https://github.com/appu1232/Discord-Selfbot/blob/873a2500d2c518e0d25ca5a6f67828de60fbda99/cogs/misc.py#L626
async def ping(ctx):
    """Get response time"""
    msgtime = ctx.message.created_at.now()
    await (await bot.ws.ping())
    now = datetime.datetime.now()
    ping = now - msgtime
    await ctx.send('🏓 Response time is {} milliseconds.'.format(str(ping.microseconds / 1000.0)))


# Execute
print('Bot directory: ', dir_path)
bot.run(token)
