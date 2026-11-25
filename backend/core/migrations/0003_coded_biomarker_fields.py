# SPDX-License-Identifier: AGPL-3.0-or-later
"""M01 TG3 step 1/3: add the nullable coding fields to Biomarker.

Split from the data step (0004) and the constraint step (0005) so each runs in its
own transaction: on PostgreSQL, ALTER TABLE fails with "pending trigger events" if it
follows FK updates in the same transaction.
"""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_measurement_hypertable"),
        ("terminology", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="biomarker",
            name="long_name",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="biomarker",
            name="system",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="biomarker",
            name="unit",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="terminology.unit",
            ),
        ),
        migrations.AddField(
            model_name="biomarker",
            name="source",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="terminology.source",
            ),
        ),
    ]
