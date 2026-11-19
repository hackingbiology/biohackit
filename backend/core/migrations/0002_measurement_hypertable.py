# SPDX-License-Identifier: AGPL-3.0-or-later
"""Turn core_measurement into a TimescaleDB hypertable (M00 Q4: done now, table is empty).

Hypertable unique indexes must contain the partition column, so the primary key
becomes (id, time). Django still addresses rows by `id`, which stays unique in practice
because it comes from a single sequence.
"""

from django.db import migrations

FORWARD = """
ALTER TABLE core_measurement DROP CONSTRAINT core_measurement_pkey;
ALTER TABLE core_measurement ADD PRIMARY KEY (id, time);
SELECT create_hypertable('core_measurement', 'time', migrate_data => true);
"""


class Migration(migrations.Migration):
    dependencies = [("core", "0001_initial")]

    operations = [
        migrations.RunSQL(FORWARD, reverse_sql=migrations.RunSQL.noop),
    ]
