# SPDX-License-Identifier: AGPL-3.0-or-later
"""LOINC search: exact code, Postgres full-text and pg_trgm trigram similarity."""

from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramWordSimilarity,
)
from django.db.models import BooleanField, Case, F, Q, QuerySet, Value, When
from django.db.models.functions import Greatest

from .models import LoincTerm

# Trigram matching uses the index-supported word-similarity operator (`<%`, Django lookup
# `trigram_word_similar`); its cut-off is the pg_trgm.word_similarity_threshold setting,
# fixed to 0.5 in settings.DATABASES OPTIONS (algorithm parameter, not a data value).
# Word similarity compares the query with the best-matching words of a field, so a typo
# inside a multi-word long name still matches. TrigramWordSimilarity is used for ranking.

_NAME_FIELDS = ("long_common_name", "short_name", "component")


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
            _relevance=Greatest(SearchRank(F("_vector"), query), F("_similarity"))
        )
        .filter(
            Q(loinc_num__iexact=text)
            | Q(_vector=query)
            | Q(long_common_name__trigram_word_similar=text)
            | Q(short_name__trigram_word_similar=text)
            | Q(component__trigram_word_similar=text)
        )
        .order_by("-_exact", "-_relevance", "loinc_num")
    )
