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

import aiohttp
import aiosqlite
import discord

from commands.triggers import get_triggers_urls
from utils.database import connect
from datetime import datetime


async def _paginate(url: str, page_size: int = 15, params: dict = None):
    combined_params = {"page[size]": page_size}
    if params is not None:
        combined_params.update(params)

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=combined_params, headers={"Accept": "application/json"}) as response:
            json = await response.json()
            if not json["articles"]:
                return
            for article in json["articles"]:
                yield article
        while json["meta"]["has_more"]:
            url = json["links"]["next"]
            async with session.get(url) as response:
                json = await response.json()
                for article in json["articles"]:
                    yield article


async def load_new_articles():
    async with connect() as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.cursor() as cur:
            await cur.execute("SELECT last_updated FROM discord_help_center;")
            rows = await cur.fetchall()

    times = {r["last_updated"] for r in rows}
    # In case there are no times default to 0
    times.add(0)
    last_updated = max(times)
    base_url = "https://support.discord.com/"
    async with connect() as conn:
        async for article in _paginate(base_url + "api/v2/help_center/en-us/articles",
                                       params={"sort_by": "edited_at", "sort_order": "desc"}, page_size=3):
            # If The Article Is Older Than The Last Time The Bot Was Refreshed
            if datetime.fromisoformat(article["edited_at"]).timestamp() <= last_updated:
                break
            await conn.execute("INSERT OR REPLACE INTO discord_help_center (id, title, url, aliases, last_updated) "
                               "VALUES (?, ?, ?, ?, ?);",
                               (article["id"], article["title"], article["html_url"], "",
                                datetime.fromisoformat(article["edited_at"]).timestamp()))
            await post_article_to_webhook(datetime.fromisoformat(article["created_at"]).timestamp() > last_updated,
                                          article)
        await conn.commit()


async def post_article_to_webhook(new: bool, article: dict):
    if new:
        urls = await get_triggers_urls("new_help_center_article")
        title = "A New Article Was Posted"
    else:
        urls = await get_triggers_urls("updated_help_center_article")
        title = "An Article Was Updated"
    print(article["title"])
    async with aiohttp.ClientSession() as session:
        for url in urls:
            webhook = discord.Webhook.from_url(url, session=session)

            v = discord.ui.View(discord.ui.Container(discord.ui.TextDisplay(f"## {title}"), discord.ui.TextDisplay(
                f"[{article["title"]}]({article["html_url"]})")))
            await webhook.send(view=v, username="New Help Center Article" if new else "Updated Help Center Article")
