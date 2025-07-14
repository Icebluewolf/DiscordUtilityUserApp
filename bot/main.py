#  Discord Utility User App
#  Copyright (c) 2025. Ice Wolfy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import asyncio
from os import environ

import discord as pycord
import discord.ui
from discord import ApplicationContext
from dotenv import load_dotenv

from modules.discord_help_center import load_new_articles
from utils import component_factory as cf
from utils.database import setup as database_setup

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
