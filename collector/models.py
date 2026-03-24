from django.db import models


class CollectorCard(models.Model):
    """
    A collector tier (e.g. Bronze, Silver, Gold).
    Each tier is linked to a Special that gets applied to the awarded BallInstance on claim.
    Per-ball thresholds are defined separately in CollectorRequirement.
    """

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, help_text="Short description shown in embeds.")
    emoji = models.CharField(
        max_length=50,
        blank=True,
        help_text="Discord emoji (e.g. 🥉 or <:bronze:123456789>).",
    )
    special = models.ForeignKey(
        "bd_models.Special",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collector_tiers",
        help_text=(
            "The Special background applied to the BallInstance awarded on claim. "
            "Set tradeable=False on the Special to make collector cards untradeable."
        ),
    )
    enabled = models.BooleanField(
        default=True,
        help_text="Disabled tiers cannot be claimed or viewed by players.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Collector Tier"
        verbose_name_plural = "Collector Tiers"

    def __str__(self) -> str:
        return self.name


class CollectorRequirement(models.Model):
    """
    Per-ball threshold for a collector tier.
    e.g. Bronze for 'Jeff Buckley' = 300, Bronze for 'Taylor Swift' = 500.
    Each ball that should be claimable for a tier needs its own row here.
    """

    card = models.ForeignKey(
        CollectorCard,
        on_delete=models.CASCADE,
        related_name="requirements",
    )
    ball = models.ForeignKey(
        "bd_models.Ball",
        on_delete=models.CASCADE,
        related_name="collector_requirements",
        verbose_name="Collectible",
    )
    count = models.PositiveIntegerField(
        help_text="How many of this collectible the player must own to claim this tier.",
    )

    class Meta:
        unique_together = [("card", "ball")]
        ordering = ["ball__rarity"]
        verbose_name = "Collector Requirement"
        verbose_name_plural = "Collector Requirements"

    def __str__(self) -> str:
        return f"{self.card.name} — {self.ball} × {self.count:,}"


class PlayerCollectorCard(models.Model):
    """
    A record of a player claiming a collector tier for a specific ball.
    ball_instance holds the actual awarded card that appears in their collection.
    """

    player = models.ForeignKey(
        "bd_models.Player",
        on_delete=models.CASCADE,
        related_name="collector_cards",
    )
    card = models.ForeignKey(
        CollectorCard,
        on_delete=models.CASCADE,
        related_name="holders",
        verbose_name="Tier",
    )
    ball = models.ForeignKey(
        "bd_models.Ball",
        on_delete=models.CASCADE,
        related_name="collector_claims",
        verbose_name="Collectible",
    )
    ball_instance = models.OneToOneField(
        "bd_models.BallInstance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="collector_claim",
        help_text="The BallInstance awarded to the player on claim.",
    )
    claimed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("player", "card", "ball")]
        ordering = ["-claimed_at"]
        verbose_name = "Player Collector Card"
        verbose_name_plural = "Player Collector Cards"

    def __str__(self) -> str:
        return f"{self.player} — {self.card.name} ({self.ball})"
