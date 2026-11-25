# SPDX-License-Identifier: AGPL-3.0-or-later
"""PostgreSQL connection-option helpers (pure, so they can be tested without settings)."""

TRGM_SETTING = "pg_trgm.word_similarity_threshold"
TRGM_THRESHOLD_OPTION = f"-c {TRGM_SETTING}=0.5"


def with_trgm_threshold(options: str) -> str:
    """Append the pg_trgm cut-off to libpq `options`, keeping any existing ones.

    A threshold already present in `options` is left untouched.
    """
    if TRGM_SETTING in options:
        return options.strip()
    return f"{options} {TRGM_THRESHOLD_OPTION}".strip()
