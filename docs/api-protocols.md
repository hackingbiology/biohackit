# M03 protocols API (TG-f part 1)

Owner-only. Session (with CSRF) or token auth as in the labs API. Another user's protocol, version or diff is `404`. Plain model, no new dependency (Q109). Nothing is seeded. Interventions are free text until the substance catalog exists (Q114).

Facets (all optional while the protocol is `draft`; unknown keys are a `400`):

- `interventions`: `[{name, amount, unit, schedule, basis, provenance, provenance_source}]`. `name` is required; `amount` is a decimal string (`"6"`, `"0.5"`), never a number, kept exactly as typed; an amount needs a `unit`. `name` and `unit` are stored as entered (no catalog or UCUM lookup yet).
  - `basis` (optional): `absolute` (default) or `per_body_weight`. `provenance` (optional): `human-derived` or `animal-derived`; it needs `provenance_source` (text, same limits as `name`, never truncated), and a source needs a provenance. A bad value, or a `provenance` without a source, is `400` naming the path, for example `interventions[0].basis`. Items stored before these keys existed read as `absolute` with empty provenance; nothing was rewritten.
  - A `per_body_weight` item without a `provenance` is accepted in `draft` (the response `missing` list asks for the provenance and its source). Leaving `draft`, or any later edit that holds such an item, is `400` (`interventions`): it is not accepted as a dose.
  - The response returns `amount` and `unit` exactly as stored plus `basis`, `provenance`, `provenance_source`; every `per_body_weight` item also has `absolute_dose: null`. No body weight is read and no absolute dose is ever computed from a per-weight value.
  - Route, formulation and product (TG-e, all optional, stored only when set): `route` is one of `oral`, `sublingual`, `topical`, `intranasal`, `inhaled`, `subcutaneous`, `intramuscular`, `other` (plain labels, not codes; Q130). `formulation` is free text of at most 100 characters; a longer value is `400`, never cut. `product_id` is the id of one of your products (`/api/substances/products/`); another user's or an unknown id is `400` (`interventions[0].product_id`). `units_per_day` is a plain ASCII decimal string above zero and needs `product_id`. A bad value is `400` naming the path, for example `interventions[0].route`. Route and formulation never set or change `amount`, and the OMOP export puts the route in `route_source_value` only. The response always shows `route`, `formulation`, `product_id` and `units_per_day` (empty or null when unset).
- `cycles`: `[{label, on_days, off_days}]` (whole days).
- `measures`: `[{loinc_code, purpose}]`, `purpose` is `efficacy`, `safety` or `baseline`. The code is stored as typed, not looked up yet.
- `goals`: `[text]`.

Other fields: `title`, `level` (`medical` or `research`, chosen by the user, never inferred), `state` (`draft`, `active`, `paused`, `completed`).

## `GET|POST /api/protocols/`

`GET` lists your protocols. `POST` creates a protocol in `draft` (`201`) from `title` plus any facets, `level`, `in_effect_since` (date), `history` (`analytic` default, or `synthesized`) and `lineage_note` (only with `history=synthesized`, else `400`). A draft response has `missing`: what is still absent in plain words (for example "No efficacy markers yet."); it never blocks the save. `origin` is `community` by default; `curated` is `403` unless the user is staff.

Already running: `already_running: true` needs `in_effect_since` (today or earlier) and `level`; it sets `tracked_since` to today, state `active`, and creates version 1 with reason "imported as already running" followed by your optional `reason` text. The response has `notes` saying that adding past measurements is invited, not required.

## `GET|PATCH /api/protocols/<id>/`

`GET` returns the protocol, `latest_version` (null in draft). `PATCH` while `draft` edits in place: no version, no reason, `in_effect_since`, `history` and `lineage_note` can change. Moving `state` to `active` leaves draft: it creates version 1 and needs a non-blank `reason` and a `level`, else `400` and the protocol stays `draft`. After that every change of `title`, `level`, `state` or a facet creates version N+1 with one change event per changed field, and a non-blank `reason` is mandatory (`400`, nothing created). A request that changes nothing is `400`. Allowed state moves: draft to active; active to paused or completed; paused to active or completed. The response has the protocol and, when one was created, `version`. Correcting the latest version is a new version, never an edit of it.

Heightened acknowledgment: moving to `active` (from `draft`, from `paused`, or through `already_running` on `POST`) is `400` (`acknowledge`, nothing created) when the protocol `level` is `research` or any item has `provenance: animal-derived`, unless the body has `acknowledge: true` (any other value is `400`). The error text includes the statement. With it, one append-only `ActivationAcknowledgment` is written in the same transaction (protocol, version, actor, time, level, the animal-derived item names, the statement shown). Resuming from `paused` asks again. On an already `active` protocol, an edit that newly makes it `research` or adds an animal-derived item name needs the same `acknowledge: true` (otherwise `400`) and logs one row; edits that add no new reason ask for nothing.

## `GET /api/protocols/<id>/versions/`

Every version, oldest first: `number`, `created_at`, `actor`, `reason`, `snapshot` (the tracked fields) and `events`: `[{field, old, new, timestamp, actor, reason}]`. `field` is a path such as `interventions[0].amount` or `state`.

## `GET /api/protocols/<id>/versions/<number>/`

One version. Read-only: there is no update or delete route, `PATCH`, `PUT` and `DELETE` return `405`, and the version stays as it was. In code, `save()` on an existing row, queryset `update()` and `delete()` raise.

## `GET /api/protocols/<id>/ingredient-totals/`

Owner-only. For the protocol as it stands now (Draft, or the latest version), the per-day total of **label contents** per substance. For each item with a `product_id` and `units_per_day`, each ingredient with a declared amount adds `amount_per_unit x units_per_day`, computed with `Decimal`, and only ingredients with exactly the same unit string are added together; different units are listed as separate totals and never converted (Q131). Response: `{protocol, kind: "label-contents-total", note, substances, items_without_units_per_day}`. Each substance has `totals` (`{unit, amount, contributions}`; a contribution has the product, its `label_source`, the ingredient's `ingredient_label_source`, `amount_per_unit`, `units_per_day`, `per_day`) and `without_amount`: ingredients whose label gives no amount, listed with `amount: null`, never summed and never estimated. Items with a product but no `units_per_day` are listed and contribute nothing. The response has no posology or dose field: it is a total of what the labels declare, not a recommendation. Totals follow the product's current label data. Left out: the intake schedule, the restock projection and the dose sanity check on the sum (no cited thresholds, Q126).

## `GET /api/protocols/<id>/diff/?from=<n>&to=<m>`

Deterministic field-level diff of two versions (stdlib `difflib`, no AI). Returns `facets` (`interventions` = name and schedule, `doses` = amount and unit per intervention, `cycles`, `measures`), each `{changed, unified}` with unified diff lines over the canonical JSON, and `changes`: `[{field, old, new}]`, for example `{"field": "doses[0].amount", "old": "6", "new": "8"}`. Missing or non-numeric `from`/`to` is `400`; an unknown version is `404`.

## `POST /api/protocols/<id>/publish/` and `POST /api/protocols/<id>/unpublish/`

Owner-only (another user's protocol is `404`). Body `{withheld_items, reason}` for publish, `{reason}` for unpublish; `reason` is mandatory (`400`). A protocol in `draft` is private and cannot be published (`400`). Publishing pins the latest version and is public by default: `withheld_items` (optional) lists item keys to keep out, in the form `interventions[0]` or `measures[1]` (position in the pinned version; an unknown key is `400`). Publishing again pins the then-latest version. If `withheld_items` is omitted, earlier withholds are kept when each withheld item is unchanged at its position, otherwise the request is `400`; an explicit `[]` clears them; until then the public view keeps showing the previously pinned version. Each publish, unpublish or withhold change writes a `ChangeEvent` (`field: publication`, old and new state, reason) on the pinned version; no version is ever edited. Unpublishing a protocol that is not published is `400`. Interventions and measures may carry `genomic: true`; a genomic item is never public, whatever `withheld_items` says, because no genomics heightened consent exists yet (Q134). Withholding is per item only (Q135). Nothing is seeded (Q133).

Every owner serializer (list, detail, version list, version detail) carries `origin` (`curated` or `community`; only staff can create `curated`) and `level`; the protocol also carries `published`.

## `GET /api/public/protocols/` and `GET /api/public/protocols/<id>/`

Anonymous, read-only, throttled (scope `public_protocols`, `PUBLIC_PROTOCOLS_THROTTLE_RATE`, default `60/min`, `429` over it). Only published protocols appear; a draft, an unpublished or another user's private protocol is `404` on detail and absent from the list. Each protocol is `{id, title, origin, level, state, published_version, cycles, goals, interventions, measures}` built from the pinned version (content), with `state` and `origin` read live (a paused protocol shows as paused): withheld and genomic items are absent (not masked), an intervention has no `product_id` or `units_per_day`, and there is no owner id or email.
