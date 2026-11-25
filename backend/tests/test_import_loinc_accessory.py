# SPDX-License-Identifier: AGPL-3.0-or-later
"""Optional ConsumerName / LinguisticVariants import (M01 TG-LOINC C1).

All data below is synthetic test data written into tmp_path; none is stored or seeded.
"""

import shutil
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from terminology.models import (
    LoincConsumerName,
    LoincLinguisticVariant,
    LoincTerm,
    Source,
)

FIXTURE = Path(__file__).parent / "fixtures" / "loinc_synthetic"
VARIANT_HEADER = (
    '"LOINC_NUM","COMPONENT","PROPERTY","TIME_ASPCT","SYSTEM","SCALE_TYP",'
    '"METHOD_TYP","CLASS","SHORTNAME","LONG_COMMON_NAME","RELATEDNAMES2",'
    '"LinguisticVariantDisplayName"'
)


def variant_row(code: str, tag: str) -> str:
    cells = [code, f"Synthetic {tag} component", "p", "t", f"Synthetic {tag} system"]
    cells += ["s", "m", "c", f"Synthetic {tag} short", f"Synthetic {tag} long"]
    cells += ["synthetic related", f"Synthetic {tag} display"]
    return ",".join(f'"{c}"' for c in cells)


@pytest.fixture
def release(tmp_path: Path) -> Path:
    shutil.copy(FIXTURE / "Loinc.csv", tmp_path / "Loinc.csv")
    consumer = tmp_path / "AccessoryFiles" / "ConsumerName"
    consumer.mkdir(parents=True)
    (consumer / "ConsumerName.csv").write_text(
        '"LoincNumber","ConsumerName"\n'
        '"SYN-0001","Synthetic analyte"\n'
        '"SYN-0002","Synthetic analyte two"\n'
    )
    variants = tmp_path / "AccessoryFiles" / "LinguisticVariants"
    variants.mkdir(parents=True)
    for name, tag in (
        ("itIT1LinguisticVariant.csv", "it"),
        ("zhCN5LinguisticVariant.csv", "zh"),
        ("deAT24LinguisticVariant.csv", "de"),
    ):
        (variants / name).write_text(
            f"{VARIANT_HEADER}\n{variant_row('SYN-0001', tag)}\n"
        )
    return tmp_path


def run(directory: Path) -> str:
    out = StringIO()
    call_command("import_loinc", str(directory), release_version="TEST-1", stdout=out)
    return out.getvalue()


def snapshot() -> tuple[list[dict], list[dict], list[dict]]:
    return (
        list(LoincTerm.objects.order_by("loinc_num").values()),
        list(LoincConsumerName.objects.order_by("term__loinc_num").values()),
        list(LoincLinguisticVariant.objects.order_by("language").values()),
    )


# scenario: terminology-reference-data::loinc-consumer-names-imported
def test_consumer_names_imported_and_idempotent(db, release):
    output = run(release)
    source = Source.objects.get(name="LOINC", version="TEST-1")
    names = LoincConsumerName.objects.order_by("term__loinc_num")
    assert [(n.term.loinc_num, n.consumer_name) for n in names] == [
        ("SYN-0001", "Synthetic analyte"),
        ("SYN-0002", "Synthetic analyte two"),
    ]
    assert {n.source_id for n in names} == {source.pk}
    assert "LoincConsumerName: created 2, updated 0" in output
    first = snapshot()
    assert "LoincConsumerName: created 0, updated 2" in run(release)
    assert snapshot() == first


# scenario: terminology-reference-data::loinc-linguistic-variants-imported-for-it-it-and-zh-cn
def test_variants_imported_for_it_and_zh_only(db, release):
    output = run(release)
    source = Source.objects.get(name="LOINC", version="TEST-1")
    variants = {v.language: v for v in LoincLinguisticVariant.objects.all()}
    assert set(variants) == {"it-IT", "zh-CN"}
    assert variants["it-IT"].display_name == "Synthetic it display"
    assert variants["zh-CN"].long_common_name == "Synthetic zh long"
    assert variants["zh-CN"].term.loinc_num == "SYN-0001"
    assert {v.source_id for v in variants.values()} == {source.pk}
    assert "LoincLinguisticVariant: created 2, updated 0" in output
    assert "Skipped language de-AT: 1 file(s) not imported" in output
    first = snapshot()
    run(release)
    assert snapshot() == first


# scenario: terminology-reference-data::optional-loinc-accessory-files-absent
def test_only_core_table_succeeds_and_names_missing_files(db, tmp_path):
    shutil.copy(FIXTURE / "Loinc.csv", tmp_path / "Loinc.csv")
    output = run(tmp_path)
    assert LoincTerm.objects.count() == 3
    assert LoincConsumerName.objects.count() == 0
    assert LoincLinguisticVariant.objects.count() == 0
    assert "ConsumerName.csv" in output
    assert "it-IT" in output
    assert "zh-CN" in output


# scenario: terminology-reference-data::accessory-row-for-an-unknown-loinc-code-aborts-the-import
@pytest.mark.parametrize(
    "relative",
    [
        "AccessoryFiles/ConsumerName/ConsumerName.csv",
        "AccessoryFiles/LinguisticVariants/itIT1LinguisticVariant.csv",
    ],
)
def test_unknown_code_rolls_back_everything(db, release, relative):
    path = release / relative
    lines = path.read_text().splitlines()
    unknown = lines[-1].replace("SYN-0001", "SYN-9999").replace("SYN-0002", "SYN-9999")
    path.write_text("\n".join([*lines, unknown]) + "\n")
    with pytest.raises(CommandError) as err:
        run(release)
    assert f"{path.name} line {len(lines) + 1}:" in str(err.value)
    assert "SYN-9999" in str(err.value)
    assert LoincTerm.objects.count() == 0
    assert LoincConsumerName.objects.count() == 0
    assert LoincLinguisticVariant.objects.count() == 0
    assert Source.objects.count() == 0


# scenario: terminology-reference-data::accessory-row-for-an-unknown-loinc-code-aborts-the-import
def test_empty_accessory_key_and_missing_column_abort(db, release):
    consumer = release / "AccessoryFiles/ConsumerName/ConsumerName.csv"
    consumer.write_text('"LoincNumber","ConsumerName"\n,"Synthetic analyte"\n')
    with pytest.raises(CommandError, match=r"ConsumerName\.csv line 2: empty"):
        run(release)
    consumer.write_text('"LoincNumber"\n"SYN-0001"\n')
    with pytest.raises(CommandError, match=r"line 1: missing column"):
        run(release)
    assert LoincTerm.objects.count() == 0


# scenario: terminology-reference-data::accessory-row-for-an-unknown-loinc-code-aborts-the-import
def test_code_from_earlier_release_is_unknown_for_this_release(db, release, tmp_path):
    run(release)
    before = snapshot()
    second = tmp_path / "second"
    second.mkdir()
    lines = (FIXTURE / "Loinc.csv").read_text().splitlines()
    (second / "Loinc.csv").write_text(
        "\n".join(line for line in lines if "SYN-0002" not in line) + "\n"
    )
    consumer = second / "AccessoryFiles" / "ConsumerName"
    consumer.mkdir(parents=True)
    (consumer / "ConsumerName.csv").write_text(
        '"LoincNumber","ConsumerName"\n"SYN-0002","Synthetic analyte two"\n'
    )
    out = StringIO()
    with pytest.raises(CommandError, match="SYN-0002"):
        call_command("import_loinc", str(second), release_version="TEST-2", stdout=out)
    assert snapshot() == before
    assert not Source.objects.filter(version="TEST-2").exists()


# scenario: terminology-reference-data::loinc-linguistic-variants-imported-for-it-it-and-zh-cn
def test_variant_removed_from_file_is_deleted_only_for_that_language(db, release):
    variants = release / "AccessoryFiles" / "LinguisticVariants"
    (variants / "itIT1LinguisticVariant.csv").write_text(
        f"{VARIANT_HEADER}\n{variant_row('SYN-0001', 'it')}\n"
        f"{variant_row('SYN-0002', 'it')}\n"
    )
    run(release)
    assert LoincLinguisticVariant.objects.filter(language="it-IT").count() == 2
    (variants / "itIT1LinguisticVariant.csv").write_text(
        f"{VARIANT_HEADER}\n{variant_row('SYN-0002', 'it')}\n"
    )
    run(release)
    it = LoincLinguisticVariant.objects.filter(language="it-IT")
    assert [v.term.loinc_num for v in it] == ["SYN-0002"]
    assert LoincLinguisticVariant.objects.filter(language="zh-CN").count() == 1


# scenario: terminology-reference-data::loinc-consumer-names-imported
def test_renamed_consumer_name_replaces_old_one(db, release):
    run(release)
    path = release / "AccessoryFiles/ConsumerName/ConsumerName.csv"
    path.write_text(
        '"LoincNumber","ConsumerName"\n'
        '"SYN-0001","Synthetic renamed"\n'
        '"SYN-0002","Synthetic analyte two"\n'
    )
    run(release)
    names = LoincConsumerName.objects.order_by("term__loinc_num")
    assert [n.consumer_name for n in names] == [
        "Synthetic renamed",
        "Synthetic analyte two",
    ]
