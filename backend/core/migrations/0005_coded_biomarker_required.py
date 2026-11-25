# SPDX-License-Identifier: AGPL-3.0-or-later
"""M01 TG3 step 3/3: drop free-text unit, make LOINC unique and the FKs required."""

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("core", "0004_coded_biomarker_data")]

    operations = [
        migrations.RemoveField(model_name="biomarker", name="unit_ucum"),
        migrations.AlterField(
            model_name="biomarker",
            name="loinc_code",
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name="biomarker",
            name="unit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="terminology.unit"
            ),
        ),
        migrations.AlterField(
            model_name="biomarker",
            name="source",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="terminology.source"
            ),
        ),
    ]
