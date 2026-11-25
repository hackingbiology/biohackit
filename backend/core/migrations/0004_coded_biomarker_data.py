# SPDX-License-Identifier: AGPL-3.0-or-later
"""M01 TG3 step 2/3: map legacy Biomarker rows to Unit and Source FKs.

The data step never invents codes, units or sources: any legacy row that cannot be
mapped makes the migration fail, naming the row ids, so an operator fixes the data.
The Source is never inferred: on a non-empty table the operator must name it with the
BIOHACK_LEGACY_BIOMARKER_SOURCE environment variable (the exact name of one stored
terminology.Source). An empty table (fresh and staging databases) applies cleanly.
"""

import os

from django.db import migrations

SOURCE_ENV = "BIOHACK_LEGACY_BIOMARKER_SOURCE"


def map_units(apps, schema_editor):
    biomarker = apps.get_model("core", "Biomarker")
    unit_model = apps.get_model("terminology", "Unit")
    source_model = apps.get_model("terminology", "Source")
    rows = list(biomarker.objects.all())
    if not rows:
        return
    uncoded = [r.pk for r in rows if not r.loinc_code]
    units = {u.ucum_code: u for u in unit_model.objects.all()}
    no_unit = [r.pk for r in rows if r.unit_ucum not in units]
    problems = []
    if uncoded:
        problems.append(f"no loinc_code: ids {uncoded}")
    if no_unit:
        problems.append(f"unit_ucum has no stored terminology.Unit: ids {no_unit}")
    source_name = os.environ.get(SOURCE_ENV, "")
    sources = list(source_model.objects.filter(name=source_name)[:2])
    if len(sources) != 1:
        problems.append(
            f"set {SOURCE_ENV} to the exact name of exactly one stored "
            "terminology.Source (it is never inferred)"
        )
    if problems:
        raise RuntimeError(
            "core.Biomarker rows cannot be coded automatically ("
            + "; ".join(problems)
            + "). Fix the data (add the LOINC codes, Units and the Source) and re-run."
        )
    for r in rows:
        r.unit = units[r.unit_ucum]
        r.source = sources[0]
        r.save(update_fields=["unit", "source"])


class Migration(migrations.Migration):
    dependencies = [("core", "0003_coded_biomarker_fields")]

    operations = [migrations.RunPython(map_units, migrations.RunPython.noop)]
