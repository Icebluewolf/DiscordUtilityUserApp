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

from dataclasses import dataclass
from datetime import datetime

import aiosqlite
import discord.ui
from discord import SlashCommandGroup, ApplicationContext, Option, AutocompleteContext, OptionChoice, Member, \
    AllowedMentions, Bot
from discord.ext import tasks

from utils.component_factory import fail
from utils.database import connect

group = SlashCommandGroup("help_center", description="Utilities For The Discord Help Center Articles")

@dataclass
class HelpCenterArticle:
    article_id: int
    title: str
    url: str
    aliases: list[str]
    last_updated: datetime

article_cache: dict[int, HelpCenterArticle] = {}
aliases: dict[int, HelpCenterArticle] = {}


async def load_articles():
    if len(article_cache) != 0:
        return
    async with connect() as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.cursor() as cur:
            await cur.execute("SELECT * FROM discord_help_center;")
            rows = await cur.fetchall()

    for row in rows:
        db_aliases = row["aliases"].split("╞")
        article_cache[row["id"]] = HelpCenterArticle(row["id"], row["title"], row["url"], db_aliases, datetime.fromtimestamp(row["last_updated"]))
        for name in db_aliases:
            aliases[name] = row["id"]


async def get_article(article_id: int) -> HelpCenterArticle | None:
    await load_articles()
    if (rtn := article_cache.get(article_id)) is not None:
        return rtn
    if (rtn := aliases.get(article_id)) is not None:
        return rtn
    return None


async def article_autocomplete(ctx: AutocompleteContext):
    await load_articles()
    startswith = []
    contains = []

    v = ctx.value.lower()
    for article in article_cache.values():
        t = article.title.lower()
        if t.startswith(v):
            startswith.append(article)
        elif v in t:
            contains.append(article)

        if len(startswith) == 25:
            break
    startswith.extend(contains)
    startswith = startswith[:min(25, len(startswith))]
    startswith = [OptionChoice(x.title, str(x.article_id)) for x in startswith]
    return startswith


@group.command(description="Sends A Message Containing Info About The Specified Help Center Article")
async def link(ctx: ApplicationContext, article: Option(str, description="The Article To Send", autocomplete=article_autocomplete), ping: Option(Member, description="The User To Ping", required=False)):
    if not article.isdigit() or (article := await get_article(int(article))) is None:
        return ctx.respond(view=discord.ui.View(await fail("There Is Not Article Of This Name")))

    c = discord.ui.Container()
    if ping is not None:
        c.add_text(f"Hey {ping.mention} This Article May Help You Out")
        c.add_separator()

    c.add_text(f"## [{article.title}]({article.url})\n-# Last Updated {discord.utils.format_dt(article.last_updated, "R")}")
    c.add_item(discord.ui.Button(url=article.url, label="Read More"))
    await ctx.respond(view=discord.ui.View(c), allowed_mentions=AllowedMentions(users=[] if ping is None else [discord.Object(id=ping.id)]))


@tasks.loop(hours=1)
async def refresh_articles():
    article_cache = {} # TODO: Make Globals Or Something
    aliases = {}
    await load_articles()

def setup(bot: Bot):
    bot.add_application_command(group)
