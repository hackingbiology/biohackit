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

Staff only. Corrects a code. The result must still have a source and a fetch date, or it is `400`.
