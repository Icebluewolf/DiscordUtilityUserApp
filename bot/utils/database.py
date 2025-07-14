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

