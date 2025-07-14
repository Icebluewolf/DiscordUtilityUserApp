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

from datetime import datetime, timedelta, timezone

from discord import Bot, slash_command, ApplicationContext, Option, OptionChoice
from discord.utils import snowflake_time, format_dt


@slash_command(description="Get The Timestamp From A Discord Snowflake")
async def snowflake_info(ctx: ApplicationContext, snowflake: Option(str, description="The SnowFlake To View Info Of")):
    try:
        b = snowflake_time(int(snowflake))
    except ValueError:
        return await ctx.respond(f"Could Not Interpret `{snowflake}` As A Snowflake")

    await ctx.respond(f"Snowflake Created On {format_dt(b, "F")} {format_dt(b, "R")}")


@slash_command(description="Create A Discord Timestamp From A Given Time")
async def timestamp(
        ctx: ApplicationContext,
        display_format: Option(str, name="format", choices=[
            OptionChoice(name="Short Time", value="t"),
            OptionChoice(name="Long Time", value="T"),
            OptionChoice(name="Short Date", value="d"),
            OptionChoice(name="Long Date", value="D"),
            OptionChoice(name="Short DateTime", value="f"),
            OptionChoice(name="Long DateTime", value="F"),
            OptionChoice(name="Relative", value="R"),
        ]),
        hour: Option(int, min_value=0, max_value=24, required=False, description="The Hour Of The Time"),
        minute: Option(int, min_value=0, max_value=59, required=False, description="The Minute Of The Time"),
        day: Option(int, min_value=0, max_value=31, required=False, description="The Day Of The Time"),
        month: Option(int, required=False, description="The Month Of The Time", choices=[
            OptionChoice(name="January", value=1),
            OptionChoice(name="February", value=2),
            OptionChoice(name="March", value=3),
            OptionChoice(name="April", value=4),
            OptionChoice(name="May", value=5),
            OptionChoice(name="June", value=6),
            OptionChoice(name="July", value=7),
            OptionChoice(name="August", value=8),
            OptionChoice(name="September", value=9),
            OptionChoice(name="October", value=10),
            OptionChoice(name="November", value=11),
            OptionChoice(name="December", value=12),
        ]),
        year: Option(int, min_value=0, max_value=9999, required=False, description="The Year Of The Time"),
        second: Option(int, min_value=0, max_value=60, required=False, description="The Day Of The Time"),
        utc_offset: Option(float, required=False, description="The UTC Offset To Apply", default=0)
        ):
    dt = datetime.now()
    dt.replace(tzinfo=timezone(timedelta(hours=utc_offset)))
    if year:
        dt = dt.replace(year=year)
    if month:
        dt = dt.replace(month=month)
    if day:
        dt = dt.replace(day=day)
    if hour:
        dt = dt.replace(hour=hour)
    if minute:
        dt = dt.replace(minute=minute)
    if second:
        dt = dt.replace(second=second)
    await ctx.respond(format_dt(dt, display_format))

def setup(bot: Bot):
    bot.add_application_command(snowflake_info)
    bot.add_application_command(timestamp)
