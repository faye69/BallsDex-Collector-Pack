from .cog import Collector
from .admin import collector as collector_admin_group

__all__ = ["Collector"]


async def setup(bot) -> None:
    cog = Collector(bot)
    await bot.add_cog(cog)
    admin_cog = bot.cogs.get("Admin")
    if admin_cog is not None and hasattr(admin_cog, "admin"):
        admin_cog.admin.add_command(collector_admin_group)


async def teardown(bot) -> None:
    admin_cog = bot.cogs.get("Admin")
    if admin_cog is not None and hasattr(admin_cog, "admin"):
        admin_cog.admin.remove_command("collector")
