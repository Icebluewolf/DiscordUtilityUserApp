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

import json

import aiosqlite
import discord.ui
from discord import Bot, slash_command, ApplicationContext, Option, SlashCommandGroup, Interaction, AutocompleteContext

from utils import component_factory as cf
from utils.database import connect

tag_cache: dict[int, dict[str, str]] = {}
aliases: dict[int, dict[str, str]] = {}


async def load_tags(user_id: int):
    if tag_cache.get(user_id) is not None:
        return

    async with connect() as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.cursor() as cur:
            await cur.execute("SELECT name, value, alias FROM tags WHERE user_id=?;", (str(user_id),))
            rows = await cur.fetchall()

    tag_cache[user_id] = {}
    aliases[user_id] = {}
    for row in rows:
        tag_cache[user_id][row["name"]] = row["value"]
        for name in json.loads(row["alias"]):
            # tag_cache[user_id][name] = row["value"]
            aliases[user_id][name] = row["name"]


async def get_tag(user_id: int, tag_name: str) -> str | None:
    await load_tags(user_id)
    if (rtn := tag_cache[user_id].get(tag_name)) is not None:
        return rtn
    if (rtn := aliases[user_id].get(tag_name)) is not None:
        return tag_cache[user_id][rtn]
    return None


async def tag_autocomplete(ctx: AutocompleteContext):
    await load_tags(ctx.interaction.user.id)
    startswith = []
    contains = []

    v = ctx.value.lower()
    for tag in tag_cache[ctx.interaction.user.id].keys():
        if tag.startswith(v):
            startswith.append(tag)
        elif v in tag:
            contains.append(tag)

        if len(startswith) == 25:
            break
    startswith.extend(contains)
    return startswith[:min(25, len(startswith))]

group = SlashCommandGroup("tag-manage")


@group.command(description="Create A Personal Tag")
async def create(ctx: ApplicationContext,
                 name: Option(str, description="The Reference String Of The Tag - Case Insensitive")):
    name = name.lower()
    if await get_tag(ctx.user.id, name) is not None:
        return await ctx.respond(view=discord.ui.View(await cf.fail("A Tag With That Name Already Exists")),
                                 ephemeral=True)

    await ctx.response.send_modal(TagValue(name))


@group.command(description="Edit A Personal Tag")
async def edit(ctx: ApplicationContext,
               name: Option(str, description="The Reference String Of The Tag - Case Insensitive", autocomplete=tag_autocomplete)):
    name = name.lower()
    if (r := await get_tag(ctx.user.id, name)) is None:
        return await ctx.respond(view=discord.ui.View(await cf.fail("No Tag With That Name Exists")), ephemeral=True)

    await ctx.response.send_modal(TagValue(name, r))


@group.command(description="Create An Alias For A Personal Tag")
async def alias(ctx: ApplicationContext,
                tag: Option(str, description="The Reference String Of The Tag - Case Insensitive", autocomplete=tag_autocomplete),
                alias: Option(str, description="The Alias To Apply - Case Insensitive")):
    tag = tag.lower()
    alias = alias.lower()
    if await get_tag(ctx.user.id, tag) is None:
        return await ctx.respond(
            view=discord.ui.View(await cf.fail("No Tag With That Name Exists To Apply An Alias To")), ephemeral=True)
    if await get_tag(ctx.user.id, alias) is not None:
        return await ctx.respond(
            view=discord.ui.View(await cf.fail("Cannot Apply Alias: A Tag With That Name Already Exists")),
            ephemeral=True)
    tag = aliases[ctx.user.id].get(tag) or tag
    async with connect() as conn:
        r = await conn.execute("SELECT alias FROM tags WHERE user_id = ? AND name = ?;",
                               (str(ctx.user.id),
                                tag,))
        async with r as cur:
            row = await cur.fetchone()
        db_alias = json.loads(row[0])
        db_alias.append(alias)
        await conn.execute("UPDATE tags SET alias = ? WHERE user_id = ? AND name = ?;",
                           (json.dumps(db_alias),
                            str(ctx.user.id),
                            tag,))
        await conn.commit()
    aliases[ctx.user.id][alias] = tag
    await ctx.respond(view=discord.ui.View(await cf.success("Alias Created")), ephemeral=True)


@group.command(description="Deletes A Tag Or Alias")
async def delete(ctx: ApplicationContext, name: Option(str, description="The Tag Or Alias To Delete - Case Insensitive")):
    await load_tags(ctx.user.id)
    name = name.lower()
    if (n := aliases[ctx.user.id].get(name)) is not None:
        async with connect() as conn:
            r = await conn.execute("SELECT alias FROM tags WHERE user_id = ? AND name = ?;",
                                   (str(ctx.user.id),
                                    n,))
            async with r as cur:
                row = await cur.fetchone()
            db_alias = json.loads(row[0])
            db_alias.remove(name)
            await conn.execute("UPDATE tags SET alias = ? WHERE user_id = ? AND name = ?;",
                               (json.dumps(db_alias),
                                str(ctx.user.id),
                                n,))
            await conn.commit()
        aliases[ctx.user.id].pop(name)
    elif tag_cache[ctx.user.id].get(name) is not None:
        async with connect() as conn:
            await conn.execute("DELETE FROM tags WHERE user_id = ? AND name = ?;",
                               (str(ctx.user.id),
                                name,))
            await conn.commit()
        remove = [k for k, v in aliases[ctx.user.id].items() if v == name]
        for i in remove:
            aliases[ctx.user.id].pop(i)
        tag_cache[ctx.user.id].pop(name)
    else:
        return await ctx.respond(view=discord.ui.View(await cf.fail("No Tag Or Alias With That Name Exists")),
                                 ephemeral=True)

    return await ctx.respond(view=discord.ui.View(await cf.success("The Tag Or Alias Was Removed")), ephemeral=True)


@slash_command(description="Display A Personal Tag")
async def tag(ctx: ApplicationContext,
              name: Option(str, description="The Tag To Display - Case Insensitive", autocomplete=tag_autocomplete),
              hidden: Option(bool, description="If The Tag Should Be Posted Publicly", required=False, default=False),
              mention: Option(discord.User, description="The User To Mention", required=False)):
    name = name.lower()
    if (r := await get_tag(ctx.user.id, name)) is None:
        return await ctx.respond(view=discord.ui.View(await cf.fail("No Tag With That Name Exists")), ephemeral=True)

    c = await cf.general(r)
    if mention is not None:
        c.add_text(f"Hey {mention.mention} This Information Would Be Useful For You")
    await ctx.respond(view=discord.ui.View(c), ephemeral=hidden)


class TagValue(discord.ui.Modal):
    def __init__(self, name: str, value: str = None):
        super().__init__(title="Enter A Value For The Tag", timeout=1800)
        self.name = name
        # If value is provided an update needs to occur instead of an insert
        self.update: bool = value is not None
        self.add_item(discord.ui.InputText(style=discord.InputTextStyle.long, label="The Value Of The Tag", value=value,
                                           min_length=1))

    async def callback(self, interaction: Interaction):
        tag = aliases[interaction.user.id].get(self.name) or self.name
        async with connect() as conn:
            if not self.update:
                await conn.execute("INSERT INTO tags (user_id, name, value) VALUES (?, ?, ?)",
                                   (str(interaction.user.id), self.name, self.children[0].value))
            else:
                await conn.execute("UPDATE tags SET value = ? WHERE user_id = ? AND name = ?;",
                                   (self.children[0].value,
                                    str(interaction.user.id),
                                    tag,))
            await conn.commit()
        if not self.update:
            tag_cache.setdefault(interaction.user.id, {})[self.name] = self.children[0].value
            await interaction.respond(view=discord.ui.View(await cf.success(f"The `{self.name}` Tag Was Created")),
                                      ephemeral=True)
        else:
            tag_cache[interaction.user.id][tag] = self.children[0].value
            await interaction.respond(view=discord.ui.View(await cf.success(f"The `{self.name}` Tag Was Updated")),
                                      ephemeral=True)


def setup(bot: Bot):
    bot.add_application_command(group)
    bot.add_application_command(tag)
