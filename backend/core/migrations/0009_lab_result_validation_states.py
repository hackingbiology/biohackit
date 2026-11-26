from django.db import migrations, models

FORWARD = {"unreviewed": "entered", "reviewed": "user_confirmed"}
BACKWARD = {"entered": "unreviewed", "user_confirmed": "reviewed"}
ELIGIBLE_STATES = ("user_confirmed", "source_verified")


def map_states(apps, mapping):
    """Rename states in place."""
    LabResult = apps.get_model("core", "LabResult")
    for old, new in mapping.items():
        LabResult.objects.filter(validation_state=old).update(validation_state=new)


def recompute_eligibility(apps):
    """Same rule as LabResult.save: laboratory, method and a confirmed state."""
    LabResult = apps.get_model("core", "LabResult")
    for row in LabResult.objects.all().iterator():
        eligible = bool(
            row.laboratory and row.method and row.validation_state in ELIGIBLE_STATES
        )
        if row.aggregation_eligible != eligible:
            LabResult.objects.filter(pk=row.pk).update(aggregation_eligible=eligible)


def forwards(apps, schema_editor):
    map_states(apps, FORWARD)
    recompute_eligibility(apps)


def backwards(apps, schema_editor):
    LabResult = apps.get_model("core", "LabResult")
    unmappable = LabResult.objects.exclude(validation_state__in=BACKWARD).count()
    if unmappable:
        raise RuntimeError(
            f"Cannot reverse: {unmappable} lab result(s) are source_verified, "
            "disputed or retracted and have no earlier state to map back to."
        )
    map_states(apps, BACKWARD)
    # Old rule: eligible with laboratory and method alone.
    for row in LabResult.objects.all().iterator():
        eligible = bool(row.laboratory and row.method)
        if row.aggregation_eligible != eligible:
            LabResult.objects.filter(pk=row.pk).update(aggregation_eligible=eligible)


class Migration(migrations.Migration):
    dependencies = [("core", "0008_biomarker_category")]

    operations = [
        migrations.AlterField(
            model_name="labresult",
            name="validation_state",
            field=models.CharField(
                choices=[
                    ("entered", "Entered"),
                    ("user_confirmed", "Confirmed by the user"),
                    ("source_verified", "Verified against the source"),
                    ("disputed", "Disputed"),
                    ("retracted", "Retracted"),
                ],
                default="entered",
                max_length=16,
            ),
        ),
        migrations.RunPython(forwards, backwards),
    ]
