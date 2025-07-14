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

import aiosqlite

from utils.database import connect

triggers: dict = {
    "new_help_center_article": "Help Center Article Is Created",
    "updated_help_center_article": "Help Center Article Is Updated"
}


async def add_trigger(url: str, trigger: str, owner: int):
    async with connect() as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.cursor() as cur:
            await cur.execute("INSERT INTO webhook_triggers (url, trigger, owner) VALUES (?, ?, ?);", (url, trigger, str(owner)))
            await conn.commit()


async def remove_trigger(url: str, trigger: str | None = None):
    """
    Removes A Webhook Trigger From The Database.
    If `trigger` is provided it will only remove that trigger.
    If no trigger is provided all triggers associated with the webhook will be removed.
    """
    async with connect() as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.cursor() as cur:
            if trigger is None:
                await cur.execute("DELETE FROM webhook_triggers WHERE url=?;", (url,))
            else:
                await cur.execute("DELETE FROM webhook_triggers WHERE url=? AND trigger=?;", (url, trigger))
            await conn.commit()
