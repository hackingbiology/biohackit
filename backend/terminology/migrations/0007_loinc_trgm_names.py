# SPDX-License-Identifier: AGPL-3.0-or-later
import django.contrib.postgres.indexes
from django.db import migrations


def _trgm(model: str, field: str, name: str) -> migrations.AddIndex:
    return migrations.AddIndex(
        model_name=model,
        index=django.contrib.postgres.indexes.GinIndex(
            fields=[field], name=name, opclasses=["gin_trgm_ops"]
        ),
    )


class Migration(migrations.Migration):
    dependencies = [
        ("terminology", "0006_loinc_consumer_names_variants"),
    ]

    operations = [
        _trgm("loincconsumername", "consumer_name", "loinc_trgm_cn_idx"),
        _trgm("loinclinguisticvariant", "long_common_name", "loinc_trgm_lv_long_idx"),
        _trgm("loinclinguisticvariant", "short_name", "loinc_trgm_lv_short_idx"),
        _trgm("loinclinguisticvariant", "component", "loinc_trgm_lv_comp_idx"),
        _trgm("loinclinguisticvariant", "display_name", "loinc_trgm_lv_disp_idx"),
    ]
