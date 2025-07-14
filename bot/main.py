import asyncio
from os import environ

import discord as pycord
import discord.ui
from discord import ApplicationContext
from dotenv import load_dotenv
from utils.database import setup as database_setup
from utils import component_factory as cf
from modules.discord_help_center import load_new_articles

load_dotenv()

intents = pycord.Intents.none()
bot = pycord.Bot(intents=intents, default_command_integration_types={pycord.IntegrationType.user_install})


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print("Loaded Commands:")
    for i in bot.walk_application_commands():
        print(f"\t{i.name}")

@bot.command(description="Provides A Short Summery Of The Bot")
async def info(ctx: ApplicationContext):
    await ctx.respond(view=discord.ui.View(await cf.general(title="Silly Wolf Info", message="Source: [Github](<>)")))

# loop = asyncio.get_event_loop()
# db.set_loop(loop)
# loop.run_until_complete(db.setup())
asyncio.run(database_setup())
asyncio.run(load_new_articles())

bot.load_extension("commands.converters")
bot.load_extension("commands.discord_utils")
bot.load_extension("commands.tags")
bot.load_extension("commands.color")
bot.load_extension("commands.triggers")
bot.load_extension("commands.help_center")
# try:
#     loop.run_until_complete(bot.start(environ['DISCORD_BOT_TOKEN']))
# except KeyboardInterrupt:
#     loop.run_until_complete(bot.close())
#     # cancel all tasks lingering
# finally:
#     loop.close()
bot.run(environ['DISCORD_BOT_TOKEN'])
