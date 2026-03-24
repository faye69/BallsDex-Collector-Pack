from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from ballsdex.core.utils import checks
from bd_models.models import Ball, BallInstance, Player
from collector.models import CollectorCard, PlayerCollectorCard

if TYPE_CHECKING:
    from ballsdex.core.bot import BallsDexBot
    from collector.collector.cog import Collector

log = logging.getLogger("ballsdex.packages.admin.collector")


# ── Converters ────────────────────────────────────────────────────────────────

class CollectorCardConverter(commands.Converter):
    """Resolve a collector tier by ID or name (exact then partial match)."""

    async def convert(self, ctx: commands.Context, value: str) -> CollectorCard:
        card: CollectorCard | None = None
        try:
            card = await CollectorCard.objects.aget(pk=int(value))
        except (CollectorCard.DoesNotExist, ValueError):
            try:
                card = await CollectorCard.objects.aget(name__iexact=value)
            except CollectorCard.DoesNotExist:
                card = await CollectorCard.objects.filter(name__icontains=value).afirst()
        if card is None:
            raise commands.BadArgument(f'Collector tier "{value}" not found.')
        return card


class BallConverter(commands.Converter):
    """Resolve a collectible by ID or country name (exact then partial match)."""

    async def convert(self, ctx: commands.Context, value: str) -> Ball:
        ball: Ball | None = None
        try:
            ball = await Ball.objects.aget(pk=int(value))
        except (Ball.DoesNotExist, ValueError):
            try:
                ball = await Ball.objects.aget(country__iexact=value)
            except Ball.DoesNotExist:
                ball = await Ball.objects.filter(country__icontains=value).afirst()
        if ball is None:
            raise commands.BadArgument(f'Collectible "{value}" not found.')
        return ball


# ── Command group ─────────────────────────────────────────────────────────────

@commands.hybrid_group()
@checks.is_staff()
async def collector(ctx: commands.Context["BallsDexBot"]):
    """Collector card management tools."""
    await ctx.send_help(ctx.command)


@collector.command(name="give")
@checks.is_staff()
async def collector_give(
    ctx: commands.Context["BallsDexBot"],
    user: discord.User,
    card: CollectorCardConverter,
    ball: BallConverter,
):
    """
    Give a player a collector card for a specific collectible, bypassing requirements.

    Parameters
    ----------
    user: discord.User
        The player to give the card to.
    card: CollectorCardConverter
        Name or ID of the collector tier (e.g. Bronze).
    ball: BallConverter
        Name or ID of the collectible.
    """
    tier_em = f"{card.emoji} " if card.emoji else ""

    if not card.special_id:
        await ctx.send(
            f"**{tier_em}{card.name}** doesn't have a special background configured — "
            f"set one in the admin panel first.",
            ephemeral=True,
        )
        return

    player, _ = await Player.objects.aget_or_create(discord_id=user.id)

    already = await PlayerCollectorCard.objects.filter(
        player=player, card=card, ball=ball
    ).aexists()
    if already:
        await ctx.send(
            f"{user.mention} already has **{tier_em}{card.name}** for **{ball.country}**.",
            ephemeral=True,
        )
        return

    new_instance = await BallInstance.objects.acreate(
        player=player,
        ball=ball,
        special_id=card.special_id,
        attack_bonus=0,
        health_bonus=0,
        tradeable=False,
    )
    await PlayerCollectorCard.objects.acreate(
        player=player,
        card=card,
        ball=ball,
        ball_instance=new_instance,
    )

    await ctx.send(
        f"✅ Gave **{tier_em}{card.name}** ({ball.country}) to {user.mention}.",
        ephemeral=True,
    )
    log.info(
        f"{ctx.author} ({ctx.author.id}) gave '{card.name}' collector card "
        f"for '{ball.country}' to {user} ({user.id})",
        extra={"webhook": True},
    )


@collector.command(name="remove")
@checks.is_staff()
async def collector_remove(
    ctx: commands.Context["BallsDexBot"],
    user: discord.User,
    card: CollectorCardConverter,
    ball: BallConverter,
):
    """
    Remove a collector card from a player for a specific collectible.

    Parameters
    ----------
    user: discord.User
        The player to remove the card from.
    card: CollectorCardConverter
        Name or ID of the collector tier (e.g. Bronze).
    ball: BallConverter
        Name or ID of the collectible.
    """
    tier_em = f"{card.emoji} " if card.emoji else ""

    try:
        player = await Player.objects.aget(discord_id=user.id)
        holder = await PlayerCollectorCard.objects.aget(
            player=player, card=card, ball=ball
        )
    except (Player.DoesNotExist, PlayerCollectorCard.DoesNotExist):
        await ctx.send(
            f"{user.mention} doesn't have **{tier_em}{card.name}** for **{ball.country}**.",
            ephemeral=True,
        )
        return

    if holder.ball_instance_id:
        try:
            inst = await BallInstance.objects.aget(pk=holder.ball_instance_id)
            inst.deleted = True
            await inst.asave(update_fields=["deleted"])
        except BallInstance.DoesNotExist:
            pass

    await holder.adelete()

    await ctx.send(
        f"✅ Removed **{tier_em}{card.name}** ({ball.country}) from {user.mention}.",
        ephemeral=True,
    )
    log.info(
        f"{ctx.author} ({ctx.author.id}) removed '{card.name}' collector card "
        f"for '{ball.country}' from {user} ({user.id})",
        extra={"webhook": True},
    )


@collector.command(name="check")
@checks.is_staff()
async def collector_check(
    ctx: commands.Context["BallsDexBot"],
    user: discord.User,
):
    """
    List all collector cards a player currently owns.

    Parameters
    ----------
    user: discord.User
        The player to inspect.
    """
    try:
        player = await Player.objects.aget(discord_id=user.id)
    except Player.DoesNotExist:
        await ctx.send(f"{user.mention} has no bot data yet.", ephemeral=True)
        return

    owned = [
        h async for h in (
            PlayerCollectorCard.objects
            .filter(player=player)
            .select_related("card", "ball")
            .order_by("ball__rarity", "card__name")
            .aiterator()
        )
    ]
    if not owned:
        await ctx.send(f"{user.mention} owns no collector cards.", ephemeral=True)
        return

    lines = [
        f"{h.card.emoji + ' ' if h.card.emoji else ''}**{h.card.name}** — "
        f"{h.ball.country} (claimed <t:{int(h.claimed_at.timestamp())}:R>)"
        for h in owned
    ]
    await ctx.send(
        f"**{user.display_name}'s collector cards ({len(owned)}):**\n" + "\n".join(lines),
        ephemeral=True,
    )


@collector.command(name="refresh")
@checks.is_staff()
async def collector_refresh(ctx: commands.Context["BallsDexBot"]):
    """Manually trigger the collector revoke check for all holders right now."""
    cog: "Collector | None" = ctx.bot.cogs.get("collector")  # type: ignore[assignment]
    if cog is None:
        await ctx.send("Collector cog is not loaded.", ephemeral=True)
        return

    await ctx.defer(ephemeral=True)
    await cog._check_and_revoke_all()
    await ctx.send("✅ Revoke check complete.", ephemeral=True)
