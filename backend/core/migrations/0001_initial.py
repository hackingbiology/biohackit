# SPDX-License-Identifier: AGPL-3.0-or-later
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Intervention",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                (
                    "subtype",
                    models.CharField(
                        choices=[
                            ("substance", "Substance"),
                            ("exercise", "Exercise"),
                            ("device_therapy", "Device / therapy"),
                            ("procedure", "Procedure"),
                            ("hormonal", "Hormonal"),
                            ("nutrition_fasting", "Nutrition / fasting"),
                        ],
                        max_length=32,
                    ),
                ),
                ("cycle_schema", models.JSONField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Biomarker",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("loinc_code", models.CharField(blank=True, max_length=20, null=True)),
                ("name", models.CharField(max_length=200)),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("efficacy", "Efficacy"),
                            ("safety", "Safety"),
                            ("baseline", "Baseline"),
                        ],
                        max_length=16,
                    ),
                ),
                ("unit_ucum", models.CharField(blank=True, max_length=64, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="Measurement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("time", models.DateTimeField()),
                ("value", models.DecimalField(decimal_places=6, max_digits=20)),
                ("unit_ucum", models.CharField(max_length=64)),
                ("source", models.CharField(max_length=200)),
                ("laboratory", models.CharField(blank=True, max_length=200, null=True)),
                ("method", models.CharField(blank=True, max_length=200, null=True)),
                ("is_aggregation_eligible", models.BooleanField(default=False)),
                (
                    "biomarker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT, to="core.biomarker"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
