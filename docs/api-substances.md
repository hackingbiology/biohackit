# M03 substances API (TG-a)

Any signed-in user can read. Only staff can create or edit (Q114): a non-staff user gets `403` on a write, an anonymous user gets `401` or `403` on everything. Session (with CSRF) or token auth as in the labs API. Nothing is seeded and no bulk terminology file is stored (Q105, Q106).

A substance has `name` (required), `substance_class` (free text, may be empty; when set it needs `class_source` and `class_fetched_on`, same rules as a code, and an empty class clears both) and `codes`. A code is `{system, code, source, fetched_on, provisional}`:

- `system` is `rxcui`, `pubchem_cid`, `unii` or `atc`.
- `code` is kept as entered after a strip. There is no format check, because no cited format rule exists yet (Q116).
- `source` is required: a code with no source is `400`. It says where the code came from.
- `fetched_on` is required, `YYYY-MM-DD`, not in the future.
- `provisional` is always `true` and read-only: a request that sends it is `400`, until Q105, Q106 and Q116 are answered.

## `GET|POST /api/substances/`

`GET` lists substances with their codes. `POST` (staff) creates one from `name`, optional `substance_class` and an optional `codes` list; any invalid code refuses the whole request (`400`, nothing created). Returns `201`.

## `GET|PATCH /api/substances/<id>/`

`GET` returns one substance, `404` if unknown. `PATCH` (staff) changes `name` and `substance_class`; codes are changed through the code routes.

## `POST /api/substances/<id>/codes/`

Staff only. Adds one code (`201`). The same system and code twice on one substance is `400`.

## `PATCH /api/substances/<id>/codes/<code_id>/`

Staff only. Corrects a code. The result must still have a source and a fetch date, or it is `400`. Changing `code`, `system` or `source` needs a new `fetched_on` in the same request (`400` otherwise). The same goes for `substance_class` or `class_source` on `PATCH /api/substances/<id>/`, which need `class_fetched_on`. Text fields refuse NUL characters with `400`.

## Synonyms and name resolution (TG-b)

A synonym is `{id, substance, name, language, source, reviewer, reviewed_at}`. `language` is a BCP 47 tag kept as typed and `source` is required. Nothing is seeded and nothing is fetched from Wikidata or Evipedia (Q108). A name resolves only by exact match, after case-folding and whitespace collapsing, on a **reviewed** synonym of exactly one substance. Every other outcome is `ambiguous` and queued. Text fields refuse NUL characters and over-long values with `400`.

## `GET|POST /api/substances/synonyms/`

Staff only (`403` for others). `POST` takes `substance` (id), `name` (max 200), `language` (max 35) and `source` (max 300). `reviewer`, `reviewed_at` and `normalised_name` are set by the server: a request that sends one is `400`. The same name, language and substance twice is `400`. The new synonym is unreviewed.

## `POST /api/substances/synonyms/<id>/approve/`

Staff only. Sets `reviewer` to the requesting user and `reviewed_at` to now; a body is ignored. `400` if already reviewed.

## `GET /api/substances/review-queue/`

Staff only. Lists items with `status` `open` (default), `resolved` or `rejected` (`?status=`). An item has `submitted_name`, `language`, `reason` (`no_match`, `unreviewed_synonym`, `near_match`, `several_substances`, `no_code`: a reviewed synonym whose substance has no stored code), `candidate_substance_ids`, `status`, `resolved_by` and `resolved_substance`.

## `POST /api/substances/review-queue/<id>/resolve/` and `POST /api/substances/review-queue/<id>/reject/`

Staff only. `resolve` takes `{substance: <id>}` and closes an open item with that substance, recording who did it; it does not create a synonym. `reject` closes it without one. A closed item gives `400`.

## `POST /api/substances/resolve/`

Any signed-in user. Body `{name, language?}`. Returns `{status, reason, substance, codes, review_item_id, candidates}`. `status` is `resolved` (with `substance` and its stored `codes`) or `ambiguous` (`substance` is `null`, `codes` empty, and the open queue item id is returned). Repeating a request reuses the open item. Near-match candidates use stdlib `difflib` with cutoff 0.8 over reviewed names and are only listed, never attached (Q117). `candidates` is filled only for staff users; for everyone else it is `[]` and only `review_item_id` is returned, so an unreviewed link never reaches end users. `language` is stored on the queue item and does not filter the match (Q118).
