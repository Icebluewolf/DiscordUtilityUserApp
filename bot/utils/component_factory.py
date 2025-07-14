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

import discord


async def error(traceback: str) -> discord.ui.Container:
    c = discord.ui.Container(color=0xFF0000)
    c.add_text("## Error\n-# Please Report This In The Support Server")
    c.add_separator()
    c.add_text(f"```\n{traceback}\n```")
    return c


async def input_error(message: str, errors: list[str]) -> discord.ui.Container:
    c = discord.ui.Container(color=0xD33033)
    c.add_text(f"## {message}")
    c.add_separator(divider=False)
    c.add_text("- " + "\n- ".join(errors))
    return c


async def fail(message: str, **kwargs) -> discord.ui.Container:
    c = discord.ui.Container(color=0xD33033)
    c.add_text("## You Can Not Do That")
    c.add_separator(divider=False)
    c.add_text(message)
    return c


async def success(message: str = None, **kwargs) -> discord.ui.Container:
    c = discord.ui.Container(color=0x00FF00)
    c.add_text("## Success!")
    c.add_separator(divider=False)
    if message:
        c.add_text(message)
    return c


async def general(message: str, title: str = None, **kwargs) -> discord.ui.Container:
    c = discord.ui.Container(color=0x30D3D0)
    if title:
        c.add_text(f"## {title}")
        c.add_separator(divider=False)
    if message:
        c.add_text(message)
    return c
