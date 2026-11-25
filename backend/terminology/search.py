# SPDX-License-Identifier: AGPL-3.0-or-later
"""LOINC search: exact code, Postgres full-text and pg_trgm trigram similarity."""

from typing import Any

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramWordSimilarity,
)
from django.db.models import (
    BooleanField,
    Case,
    F,
    FloatField,
    Manager,
    Max,
    OuterRef,
    Q,
    QuerySet,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce, Greatest

from .models import LoincConsumerName, LoincLinguisticVariant, LoincTerm

# Trigram matching uses the index-supported word-similarity operator (`<%`, Django lookup
# `trigram_word_similar`); its cut-off is the pg_trgm.word_similarity_threshold setting,
# fixed to 0.5 in settings.DATABASES OPTIONS (algorithm parameter, not a data value).
# Word similarity compares the query with the best-matching words of a field, so a typo
# inside a multi-word long name still matches. TrigramWordSimilarity is used for ranking.
#
# Consumer names and it-IT/zh-CN variant names are matched in their own index-friendly
# queries whose term ids are UNIONed (never joined), so a term is returned once however
# many names match, and each arm can still use its trigram/full-text index.
# Variant fields also match by case-insensitive substring, so CJK text matches whatever
# pg_trgm does with multibyte characters. related_names is not searched.

_NAME_FIELDS = ("long_common_name", "short_name", "component")
_VARIANT_FIELDS = (*_NAME_FIELDS, "display_name")


def _core_ids(text: str, query: SearchQuery) -> QuerySet[LoincTerm, Any]:
    rows = LoincTerm.objects.annotate(
        _v=SearchVector(*_NAME_FIELDS, config="simple")
    ).filter(
        Q(loinc_num__iexact=text)
        | Q(_v=query)
        | Q(long_common_name__trigram_word_similar=text)
        | Q(short_name__trigram_word_similar=text)
        | Q(component__trigram_word_similar=text)
    )
    return rows.values("pk")


def _consumer_ids(text: str, query: SearchQuery) -> QuerySet[LoincConsumerName, Any]:
    rows = LoincConsumerName.objects.annotate(
        _v=SearchVector("consumer_name", config="simple")
    ).filter(Q(consumer_name__trigram_word_similar=text) | Q(_v=query))
    return rows.values("term_id")


def _variant_ids(text: str) -> QuerySet[LoincLinguisticVariant, Any]:
    match = Q()
    for field in _VARIANT_FIELDS:
        match |= Q(**{f"{field}__trigram_word_similar": text})
        match |= Q(**{f"{field}__icontains": text})
    return LoincLinguisticVariant.objects.filter(match).values("term_id")


def _best_similarity(
    rows: Manager[Any], text: str, fields: tuple[str, ...]
) -> Coalesce:
    """Highest word similarity over a term's rows and `fields`; 0 when it has none."""
    scores = [TrigramWordSimilarity(text, field) for field in fields]
    best = (
        rows.filter(term=OuterRef("pk"))
        .values("term")
        .annotate(_best=Max(Greatest(*scores, Value(0.0))))
        .values("_best")
    )
    return Coalesce(Subquery(best, output_field=FloatField()), Value(0.0))


def search_loinc(q: str) -> QuerySet[LoincTerm]:
    """Terms matching `q`, ordered: exact code first, relevance desc, loinc_num asc."""
    text = q.strip()
    vector = SearchVector(*_NAME_FIELDS, config="simple")
    query = SearchQuery(text, search_type="websearch", config="simple")
    similarities = [TrigramWordSimilarity(text, field) for field in _NAME_FIELDS]
    return (
        LoincTerm.objects.select_related("source")
        .annotate(
            _vector=vector,
            _similarity=Greatest(*similarities),
            _exact=Case(
                When(loinc_num__iexact=text, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
        )
        .annotate(
            _relevance=Greatest(
                SearchRank(F("_vector"), query),
                F("_similarity"),
                _best_similarity(LoincConsumerName.objects, text, ("consumer_name",)),
                _best_similarity(LoincLinguisticVariant.objects, text, _VARIANT_FIELDS),
            )
        )
        .filter(
            pk__in=_core_ids(text, query).union(
                _consumer_ids(text, query), _variant_ids(text)
            )
        )
        .order_by("-_exact", "-_relevance", "loinc_num")
    )
