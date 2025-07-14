import aiosqlite
import discord
from discord import ApplicationContext, Option, OptionChoice, SlashCommandGroup

from utils.database import connect

trigger_text: dict = {
    "new_help_center_article": "Help Center Article Is Created",
    "updated_help_center_article": "Help Center Article Is Updated"
}
triggers = [OptionChoice(x[1], x[0]) for x in trigger_text.items()]
group = SlashCommandGroup("trigger", "Actions For Triggers")


async def get_triggers_urls(trigger: str):
    async with connect() as conn:
        conn.row_factory = aiosqlite.Row
        async with conn.cursor() as cur:
            await cur.execute("SELECT url FROM webhook_triggers WHERE trigger=?;", (trigger,))
            rows = await cur.fetchall()
    return [r["url"] for r in rows]


# This All Needs To Be In Setup Because It Uses The Bot Instance
def setup(bot):
    async def _remove_webhook(w: discord.Webhook | None):
        if w is not None:
            try:
                if w.is_partial():
                    w = await bot.fetch_webhook(w.id)
                await w.delete(reason="Trigger Disabled")
            except discord.NotFound:
                pass

    async def _db_add_trigger(url: str, trigger: str, owner: int):
        async with connect() as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.cursor() as cur:
                await cur.execute("INSERT INTO webhook_triggers (url, trigger, owner) VALUES (?, ?, ?);",
                                  (url, trigger, str(owner)))
                await conn.commit()

    async def _db_remove_trigger(url: str, trigger: str | None = None):
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

    @group.command(description="Creates A Webhook In The Current Channel For The Specified Trigger")
    async def set(
        ctx: ApplicationContext,
        trigger: Option(str, description="The Trigger To Set", choices=triggers),
        webhook: Option(str, description="The Webhook URL")
    ):
        await _db_add_trigger(webhook, trigger, ctx.user.id)
        await ctx.respond("Trigger Set", ephemeral=True)

    @group.command(description="Removes The Trigger For The Specified Webhook")
    async def unset(
        ctx: ApplicationContext, webhook: Option(str, "The URL Of The Webhook To Modify"), trigger: Option(str, "The Trigger To Remove. If Not Provided Delete The Webhook", choices=triggers, required=False, default=None)
    ):
        await _db_remove_trigger(webhook, trigger)
        if trigger is None:
            try:
                w = discord.Webhook.from_url(webhook, session=bot.http._HTTPClient__session)
            except discord.InvalidArgument:
                return ctx.respond("The Webhook URL Was Not Valid")
            await _remove_webhook(w)
        await ctx.respond("Trigger Removed", ephemeral=True)

    bot.add_application_command(group)
