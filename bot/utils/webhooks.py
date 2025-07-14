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
