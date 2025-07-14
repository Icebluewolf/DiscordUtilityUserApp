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


def connect() -> aiosqlite.Connection:
    return aiosqlite.connect("database/tags.db")


async def setup():
    async with connect() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
            CREATE TABLE IF NOT EXISTS tags 
            (user_id TEXT NOT NULL, name TEXT NOT NULL, value TEXT NOT NULL, alias JSON NOT NULL DEFAULT '[]');
            """)

            await cur.execute("""
            CREATE TABLE IF NOT EXISTS discord_help_center
            (
                id           INTEGER NOT NULL
                    CONSTRAINT discord_help_center_pk
                        PRIMARY KEY,
                title        TEXT    NOT NULL,
                url          TEXT    NOT NULL,
                aliases      TEXT,
                last_updated INTEGER NOT NULL
            );
            """)

            await cur.execute("""
            CREATE TABLE IF NOT EXISTS webhook_triggers
            (
                url     TEXT NOT NULL,
                trigger TEXT NOT NULL,
                owner   TEXT NOT NULL
            );
            """)
        await conn.commit()

