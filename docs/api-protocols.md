# M03 protocols API (TG-f part 1)

Owner-only. Session (with CSRF) or token auth as in the labs API. Another user's protocol, version or diff is `404`. Plain model, no new dependency (Q109). Nothing is seeded. Interventions are free text until the substance catalog exists (Q114).

Facets (all optional while the protocol is `draft`; unknown keys are a `400`):

- `interventions`: `[{name, amount, unit, schedule}]`. `name` is required; `amount` is a decimal string (`"6"`, `"0.5"`), never a number, kept exactly as typed; an amount needs a `unit`. `name` and `unit` are stored as entered (no catalog or UCUM lookup yet).
- `cycles`: `[{label, on_days, off_days}]` (whole days).
- `measures`: `[{loinc_code, purpose}]`, `purpose` is `efficacy`, `safety` or `baseline`. The code is stored as typed, not looked up yet.
- `goals`: `[text]`.

Other fields: `title`, `level` (`medical` or `research`, chosen by the user, never inferred), `state` (`draft`, `active`, `paused`, `completed`).

## `GET|POST /api/protocols/`

`GET` lists your protocols. `POST` creates a protocol in `draft` (`201`) from `title` plus any facets, `level`, `in_effect_since` (date), `history` (`analytic` default, or `synthesized`) and `lineage_note` (only with `history=synthesized`, else `400`). A draft response has `missing`: what is still absent in plain words (for example "No efficacy markers yet."); it never blocks the save. `origin` is `community` by default; `curated` is `403` unless the user is staff.

Already running: `already_running: true` needs `in_effect_since` (today or earlier) and `level`; it sets `tracked_since` to today, state `active`, and creates version 1 with reason "imported as already running" followed by your optional `reason` text. The response has `notes` saying that adding past measurements is invited, not required.

## `GET|PATCH /api/protocols/<id>/`

`GET` returns the protocol, `latest_version` (null in draft). `PATCH` while `draft` edits in place: no version, no reason, `in_effect_since`, `history` and `lineage_note` can change. Moving `state` to `active` leaves draft: it creates version 1 and needs a non-blank `reason` and a `level`, else `400` and the protocol stays `draft`. After that every change of `title`, `level`, `state` or a facet creates version N+1 with one change event per changed field, and a non-blank `reason` is mandatory (`400`, nothing created). A request that changes nothing is `400`. Allowed state moves: draft to active; active to paused or completed; paused to active or completed. The response has the protocol and, when one was created, `version`. Correcting the latest version is a new version, never an edit of it.

## `GET /api/protocols/<id>/versions/`

Every version, oldest first: `number`, `created_at`, `actor`, `reason`, `snapshot` (the tracked fields) and `events`: `[{field, old, new, timestamp, actor, reason}]`. `field` is a path such as `interventions[0].amount` or `state`.

## `GET /api/protocols/<id>/versions/<number>/`

One version. Read-only: there is no update or delete route, `PATCH`, `PUT` and `DELETE` return `405`, and the version stays as it was. In code, `save()` on an existing row, queryset `update()` and `delete()` raise.

## `GET /api/protocols/<id>/diff/?from=<n>&to=<m>`

Deterministic field-level diff of two versions (stdlib `difflib`, no AI). Returns `facets` (`interventions` = name and schedule, `doses` = amount and unit per intervention, `cycles`, `measures`), each `{changed, unified}` with unified diff lines over the canonical JSON, and `changes`: `[{field, old, new}]`, for example `{"field": "doses[0].amount", "old": "6", "new": "8"}`. Missing or non-numeric `from`/`to` is `400`; an unknown version is `404`.
