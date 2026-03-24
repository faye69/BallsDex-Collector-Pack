from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("bd_models", "0014_alter_ball_options_alter_ballinstance_options_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="CollectorCard",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                (
                    "description",
                    models.TextField(
                        blank=True,
                        help_text="Short description shown in embeds.",
                    ),
                ),
                (
                    "emoji",
                    models.CharField(
                        blank=True,
                        max_length=50,
                        help_text="Discord emoji (e.g. 🥉 or <:bronze:123456789>).",
                    ),
                ),
                (
                    "special",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="collector_tiers",
                        to="bd_models.special",
                        help_text=(
                            "The Special background applied to the BallInstance awarded on claim. "
                            "Set tradeable=False on the Special to make collector cards untradeable."
                        ),
                    ),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=True,
                        help_text="Disabled tiers cannot be claimed or viewed by players.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Collector Tier",
                "verbose_name_plural": "Collector Tiers",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="CollectorRequirement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "card",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="requirements",
                        to="collector.collectorcard",
                    ),
                ),
                (
                    "ball",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="collector_requirements",
                        to="bd_models.ball",
                        verbose_name="Collectible",
                    ),
                ),
                (
                    "count",
                    models.PositiveIntegerField(
                        help_text=(
                            "How many of this collectible the player must own to claim this tier."
                        ),
                    ),
                ),
            ],
            options={
                "verbose_name": "Collector Requirement",
                "verbose_name_plural": "Collector Requirements",
                "ordering": ["ball__rarity"],
                "unique_together": {("card", "ball")},
            },
        ),
        migrations.CreateModel(
            name="PlayerCollectorCard",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "player",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="collector_cards",
                        to="bd_models.player",
                    ),
                ),
                (
                    "card",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="holders",
                        to="collector.collectorcard",
                        verbose_name="Tier",
                    ),
                ),
                (
                    "ball",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="collector_claims",
                        to="bd_models.ball",
                        verbose_name="Collectible",
                    ),
                ),
                (
                    "ball_instance",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="collector_claim",
                        to="bd_models.ballinstance",
                        help_text="The BallInstance awarded to the player on claim.",
                    ),
                ),
                ("claimed_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "Player Collector Card",
                "verbose_name_plural": "Player Collector Cards",
                "ordering": ["-claimed_at"],
                "unique_together": {("player", "card", "ball")},
            },
        ),
    ]
