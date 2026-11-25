# SPDX-License-Identifier: AGPL-3.0-or-later
"""Optional AnswerList / LoincAnswerListLink import (M01 TG-LOINC D2).

All data comes from the synthetic fixture tree (invented SYN-000n and LL99999-n codes).
"""

import shutil
from io import StringIO
from pathlib import Path

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from terminology.models import (
    LoincAnswer,
    LoincAnswerList,
    LoincAnswerListLink,
    LoincTerm,
    Source,
)

FIXTURE = Path(__file__).parent / "fixtures" / "loinc_synthetic"
LIST_FILE = "AccessoryFiles/AnswerFile/AnswerList.csv"
LINK_FILE = "AccessoryFiles/AnswerFile/LoincAnswerListLink.csv"
MODELS = (LoincAnswerList, LoincAnswer, LoincAnswerListLink)


@pytest.fixture
def release(tmp_path: Path) -> Path:
    shutil.copytree(FIXTURE, tmp_path, dirs_exist_ok=True)
    return tmp_path


def run(directory: Path) -> str:
    out = StringIO()
    call_command("import_loinc", str(directory), release_version="TEST-1", stdout=out)
    return out.getvalue()


def snapshot() -> list[list[dict]]:
    return [list(m.objects.order_by("id").values()) for m in MODELS]


def append_line(path: Path, line: str) -> int:
    lines = path.read_text().splitlines()
    path.write_text("\n".join([*lines, line]) + "\n")
    return len(lines) + 1


def assert_nothing_written() -> None:
    assert LoincTerm.objects.count() == 0
    assert Source.objects.count() == 0
    assert all(m.objects.count() == 0 for m in MODELS)


# scenario: terminology-reference-data::loinc-answer-lists-imported
def test_answer_lists_and_answers_imported_and_idempotent(db, release):
    output = run(release)
    source = Source.objects.get(name="LOINC", version="TEST-1")
    lists = {a.answer_list_id: a for a in LoincAnswerList.objects.all()}
    assert set(lists) == {"LL99999-1", "LL99999-2", "LL99999-3"}
    assert lists["LL99999-1"].name == "SYNTHETIC list one"
    assert lists["LL99999-1"].oid == "9.9.9.1"
    answers = LoincAnswer.objects.order_by("answer_list__answer_list_id", "sequence")
    assert [(a.answer_list.answer_list_id, a.answer_code) for a in answers] == [
        ("LL99999-1", "LA99999-1"),
        ("LL99999-1", "LA99999-2"),
        ("LL99999-2", "LA99999-1"),
    ]
    assert answers[1].display_text == "synthetic answer two"
    assert answers[1].sequence == 2
    assert answers[1].local_answer_code == "2"
    stored = [*lists.values(), *answers]
    assert {o.source_id for o in stored} == {source.pk}
    assert "LoincAnswerList: created 3, updated 0" in output
    assert "LoincAnswer: created 3, updated 0" in output
    first = snapshot()
    again = run(release)
    assert "LoincAnswerList: created 0, updated 3" in again
    assert "LoincAnswer: created 0, updated 3" in again
    assert snapshot() == first


# scenario: terminology-reference-data::loinc-answer-list-links-imported
def test_answer_list_links_imported_and_not_duplicated(db, release):
    output = run(release)
    source = Source.objects.get(name="LOINC", version="TEST-1")
    links = LoincAnswerListLink.objects.order_by("id")
    assert [
        (k.term.loinc_num, k.answer_list.answer_list_id, k.link_type) for k in links
    ] == [
        ("SYN-0001", "LL99999-1", "NORMATIVE"),
        ("SYN-0002", "LL99999-1", "EXAMPLE"),
        ("SYN-0002", "LL99999-2", "NORMATIVE"),
    ]
    assert {k.source_id for k in links} == {source.pk}
    assert "LoincAnswerListLink: created 3, updated 0" in output
    first = snapshot()
    assert "LoincAnswerListLink: created 0, updated 3" in run(release)
    assert snapshot() == first


# scenario: terminology-reference-data::loinc-answer-list-links-imported
def test_removed_link_and_answer_are_deleted(db, release):
    run(release)
    link_path = release / LINK_FILE
    link_path.write_text("\n".join(link_path.read_text().splitlines()[:2]) + "\n")
    list_path = release / LIST_FILE
    list_path.write_text("\n".join(list_path.read_text().splitlines()[:2]) + "\n")
    run(release)
    assert LoincAnswerListLink.objects.count() == 1
    # LL99999-1 lost its second answer; LL99999-2 is not in the file any more, kept
    assert sorted(
        LoincAnswer.objects.values_list("answer_list__answer_list_id", "answer_code")
    ) == [
        ("LL99999-1", "LA99999-1"),
        ("LL99999-2", "LA99999-1"),
    ]
    assert LoincAnswerList.objects.count() == 3  # lists are never deleted


# scenario: terminology-reference-data::loinc-answer-list-links-imported
def test_links_resolve_against_lists_already_in_database(db, release):
    run(release)
    (release / LIST_FILE).unlink()
    output = run(release)
    assert LIST_FILE in output
    assert LoincAnswerListLink.objects.count() == 3


# scenario: terminology-reference-data::panel-or-answer-list-row-referencing-an-unknown-term-or-list-aborts-the-import
def test_link_to_unknown_answer_list_rolls_back_everything(db, release):
    path = release / LINK_FILE
    row = '"SYN-0001","x","LL99999-9","x","NORMATIVE",'
    number = append_line(path, row)
    with pytest.raises(CommandError) as err:
        run(release)
    assert f"LoincAnswerListLink.csv line {number}:" in str(err.value)
    assert "LL99999-9" in str(err.value)
    assert_nothing_written()


# scenario: terminology-reference-data::panel-or-answer-list-row-referencing-an-unknown-term-or-list-aborts-the-import
@pytest.mark.parametrize(
    ("name", "row", "code"),
    [
        (LINK_FILE, '"SYN-7777","x","LL99999-1","x","NORMATIVE",', "SYN-7777"),
    ],
)
def test_unknown_loinc_code_rolls_back_everything(db, release, name, row, code):
    number = append_line(release / name, row)
    with pytest.raises(CommandError) as err:
        run(release)
    assert f"{Path(name).name} line {number}:" in str(err.value)
    assert code in str(err.value)
    assert_nothing_written()


# scenario: terminology-reference-data::panel-or-answer-list-row-referencing-an-unknown-term-or-list-aborts-the-import
@pytest.mark.parametrize(
    ("name", "row", "text"),
    [
        (
            LIST_FILE,
            '"LL99999-4","n","o","N",,,"LA99999-4","1",,"x","t",,,,,,,,',
            "not a whole number",
        ),
    ],
)
def test_bad_sequence_aborts(db, release, name, row, text):
    number = append_line(release / name, row)
    with pytest.raises(CommandError, match=f"line {number}:.*{text}"):
        run(release)
    assert_nothing_written()


# scenario: terminology-reference-data::panel-or-answer-list-row-referencing-an-unknown-term-or-list-aborts-the-import
def test_overlong_answer_list_name_aborts(db, release):
    row = f'"LL99999-4","{"n" * 1001}","o","N",,,,,,,,,,,,,,,'
    number = append_line(release / LIST_FILE, row)
    with pytest.raises(CommandError, match=f"line {number}: name is 1001"):
        run(release)
    assert_nothing_written()


# scenario: terminology-reference-data::panel-or-answer-list-row-referencing-an-unknown-term-or-list-aborts-the-import
def test_overlong_answer_text_aborts(db, release):
    row = f'"LL99999-4","n","o","N",,,"LA99999-4","1",,1,"{"t" * 1001}",,,,,,,,'
    number = append_line(release / LIST_FILE, row)
    with pytest.raises(CommandError, match=f"line {number}: display_text is 1001"):
        run(release)
    assert_nothing_written()


# scenario: terminology-reference-data::panel-or-answer-list-row-referencing-an-unknown-term-or-list-aborts-the-import
def test_conflicting_list_fields_abort(db, release):
    row = '"LL99999-1","other name","9.9.9.1","N",,,,,,,,,,,,,,,'
    number = append_line(release / LIST_FILE, row)
    with pytest.raises(CommandError, match=f"line {number}:.*differs"):
        run(release)
    assert_nothing_written()


# scenario: terminology-reference-data::panel-or-answer-list-row-referencing-an-unknown-term-or-list-aborts-the-import
def test_repeated_answer_in_list_aborts(db, release):
    row = '"LL99999-1","SYNTHETIC list one","9.9.9.1","N",,,"LA99999-1","1",,5,"again",,,,,,,,'
    number = append_line(release / LIST_FILE, row)
    with pytest.raises(CommandError, match=f"line {number}:.*repeated"):
        run(release)
    assert_nothing_written()


# scenario: terminology-reference-data::optional-loinc-accessory-files-absent
def test_release_imports_without_answer_files(db, tmp_path):
    shutil.copy(FIXTURE / "Loinc.csv", tmp_path / "Loinc.csv")
    output = run(tmp_path)
    assert LoincTerm.objects.count() == 3
    assert all(m.objects.count() == 0 for m in MODELS)
    for name in (LIST_FILE, LINK_FILE):
        assert name in output
