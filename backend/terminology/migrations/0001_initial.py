# SPDX-License-Identifier: AGPL-3.0-or-later
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("core", "0002_measurement_hypertable"),
    ]

    operations = [
        migrations.CreateModel(
            name="Source",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("version", models.CharField(blank=True, default="", max_length=64)),
                ("licence", models.CharField(max_length=200)),
                ("url", models.URLField(max_length=500)),
                ("retrieved_at", models.DateField()),
            ],
        ),
        migrations.AddConstraint(
            model_name="source",
            constraint=models.UniqueConstraint(fields=("name", "version"), name="uniq_source_name_version"),
        ),
        migrations.CreateModel(
            name="Unit",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("ucum_code", models.CharField(max_length=64, unique=True)),
                ("display", models.CharField(max_length=100)),
                ("source", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="terminology.source")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="UnitConversion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("factor", models.DecimalField(decimal_places=12, max_digits=30)),
                ("biomarker", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="core.biomarker")),
                ("from_unit", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="conversions_from", to="terminology.unit")),
                ("source", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="terminology.source")),
                ("to_unit", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="conversions_to", to="terminology.unit")),
            ],
            options={"abstract": False},
        ),
        migrations.AddConstraint(
            model_name="unitconversion",
            constraint=models.UniqueConstraint(fields=("from_unit", "to_unit", "biomarker"), name="uniq_conversion", nulls_distinct=False),
        ),
    ]
