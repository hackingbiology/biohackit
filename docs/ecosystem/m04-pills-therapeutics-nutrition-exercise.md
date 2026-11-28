# Ecosystem scan — M04 Pills, therapeutics, nutrition and exercise

Method, decision categories and licence table: [README.md](README.md). Capabilities: `pills-management`, `therapeutics-management`, `nutrition-management`, `exercise-reporting` (`openspec/specs/*/spec.md`) plus the s01 requirements "Reminders for intake, due tests and restock" and "Protocol cost is tracked and shown" (`openspec/changes/s01-spec-discovery/tasks.md`). No OpenSpec change for M04 exists yet; this scan precedes it. Facts were fetched on 2026-11-28 (GitHub API `pushed_at` as "Last activity", PyPI JSON, and the pages named in each entry). Our own assessments (not fetched facts) are marked "assessment". This scan adds no dependency, downloads no dataset into the repo and seeds no data row.

**About the `Verified` field.** As in the M03 scan, `backend/tests/test_ecosystem_docs.py` accepts only a fixed list of source hosts. An entry whose only source is a web page (USDA, Open Food Facts, the Compendium of Physical Activities, Ciqual) therefore has `Verified: unknown`, and the page fetched, with its date and what it said, is in the `Licence note`. Q107 already asks whether official pages should be accepted.

## Capability needs that an external project, schema or dataset could cover

| Need (spec) | Covered by section |
|---|---|
| Constraint-based daily slot allocation, spacing and meal-distance rules, flagged conflicts (`pills-management`: Daily intake schedule, Meal timing, Spacing) | (a) |
| Intake and session cadence, calendar, reminders (`pills-management`, `therapeutics-management`, s01 reminders) | (b) |
| Intake tracker, stock and nutrition tracker designs to learn from (`pills-management` restock, `nutrition-management`) | (c) |
| Food composition and nutrient data behind a macronutrient split (`nutrition-management`) | (d) |
| Activity level for TDEE and exercise vocabularies (`nutrition-management` TDEE, `exercise-reporting`) | (e) |
| Wearable and activity exports (`exercise-reporting`, `biomarkers-and-labs` wearable import) | (f) |
| FHIR / OMOP export mapping for intake events, nutrition and exercise | (g), and M03 (below) |
| Typed parameters of periodic therapies (red light, HBOT, IHHT, cryotherapy, sauna, TPE, IV, PEMF, tVNS) | not covered: no source was scanned, see Q148 |
| VO2max as a biomarker with date and method (`exercise-reporting`: VO2max captured as a biomarker) | not covered: no code system (for example a LOINC code), UCUM unit or method vocabulary was scanned; the M02 scan has no VO2max entry, see Q149 |
| Protocol cost (s01 "Protocol cost is tracked and shown") | not covered: no external project was scanned; it is price arithmetic over our own Product and stock data |

**Already decided in M03, reused without restating** ([m03-interventions-protocols.md](m03-interventions-protocols.md)): substance and product codes (RxCUI, PubChem CID, ATC and UNII rules, Q105, Q106), FHIR MedicationStatement / PlanDefinition / CarePlan as export targets (Q55), OMOP DRUG_EXPOSURE as export target (the mapping is in [docs/omop/drug-exposure-mapping.md](../omop/drug-exposure-mapping.md)), and get-based's supplement record (dosing periods, schedule `mode`/`timesPerDay`/`daysOfWeek`/`intervalDays`, review-before-apply draft). The TG-e route/formulation and Product model are our own code in `backend/`; M04 builds on them and this scan does not re-decide them.

## (a) Intake scheduling and constraint solving

### OR-Tools (Google)
- **URL:** https://github.com/google/or-tools
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-11-27
- **Decision:** adopt as dependency
- **Verified:** api.github.com/repos/google/or-tools (licence `Apache-2.0`, not archived, pushed 2026-11-27T17:30:53Z) and pypi.org/pypi/ortools/json (license "Apache 2.0", classifier "Apache Software License", version 9.15.6755, uploaded 2026-01-14, summary "Google OR-Tools python libraries and modules"), 2026-11-28
- **Licence note:** the spec says allocation uses "a constraint solver rather than an LLM", deterministic and explainable. Assessment: OR-Tools is a candidate solver; it is not installed by this scan and `backend/pyproject.toml` has no solver today (grep for ortools, constraint, dateutil, icalendar, webpush found nothing, 2026-11-28). Adding it needs Fabio's approval of a dependency (Q140). Whether its solutions can be turned into a "stated reason" for each separation (the scenario "Competing compounds separated") was not read; the M04 change must check that, and that the solver is deterministic for a fixed input.
- **Provisional:** yes, adoption waits on Q140 (dependency approval and the explainability check).

### python-constraint2
- **URL:** https://github.com/python-constraint/python-constraint
- **Licence:** BSD-2-Clause
- **AGPL-compatible:** yes (BSD-2-Clause)
- **Last activity:** 2026-11-07
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/python-constraint/python-constraint (licence `BSD-2-Clause`, pushed 2026-11-07T03:00:58Z) and pypi.org/pypi/python-constraint2/json (license_expression `BSD-2-Clause`, version 2.9.0, uploaded 2026-10-27, summary "python-constraint is a module for efficiently solving CSPs (Constraint Solving Problems)"), 2026-11-28
- **Licence note:** a smaller CSP library as an alternative to OR-Tools. Not adopted here: the old PyPI name `python-constraint` is at 1.4.0 uploaded 2018-11-05 (pypi.org, 2026-11-28), so the maintained package name is `python-constraint2`. Assessment: a small pure constraint model may be enough for dozens of intakes into a few slots; the M04 change decides after writing the scenarios as tests. Neither library was run here.

## (b) Recurrence, calendar and reminders

### python-dateutil (rrule)
- **URL:** https://github.com/dateutil/dateutil
- **Licence:** BSD-3-Clause
- **AGPL-compatible:** yes (BSD-3-Clause)
- **Last activity:** 2026-11-18
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/dateutil/dateutil (licence `NOASSERTION`, pushed 2026-11-18T01:50:32Z) and pypi.org/pypi/python-dateutil/json (license_expression `BSD-3-Clause`, version 4.0.0, uploaded 2026-11-01, summary "Extensions to the standard Python datetime module"), 2026-11-28
- **Licence note:** the licence comes from PyPI because GitHub reported `NOASSERTION`. Assessment: its `rrule` module implements RFC 5545 recurrence rules and could express "every second day", "weekdays"; get-based's schedule (`mode`, `timesPerDay`, `daysOfWeek`, `intervalDays`, see M03) is a simpler typed form. The M04 change decides whether a typed cadence is enough before any recurrence library is added.

### icalendar
- **URL:** https://github.com/collective/icalendar
- **Licence:** BSD-2-Clause
- **AGPL-compatible:** yes (BSD-2-Clause)
- **Last activity:** 2026-11-27
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/collective/icalendar (redirects to PyCalendar/icalendar; licence `BSD-2-Clause`, pushed 2026-11-27T04:46:53Z) and pypi.org/pypi/icalendar/json (license_expression `BSD-2-Clause`, version 7.3.2, uploaded 2026-11-20, summary "RFC 5545 compatible parser and generator of iCalendar files"), 2026-11-28
- **Licence note:** assessment: a possible way to export the programming calendar (pills, therapies, exercise) as an `.ics` feed. No spec requirement asks for calendar export, so nothing is adopted; recorded for the planner of `measurement-planning`.

### pywebpush
- **URL:** https://github.com/web-push-libs/pywebpush
- **Licence:** MPL-2.0
- **AGPL-compatible:** yes (MPL-2.0)
- **Last activity:** 2026-09-01
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/web-push-libs/pywebpush (licence `MPL-2.0`, pushed 2026-09-01T21:53:33Z) and pypi.org/pypi/pywebpush/json (license_expression `MPL-2.0`, version 2.5.0, uploaded 2026-08-30, summary "WebPush publication library"), 2026-11-28
- **Licence note:** candidate server-side sender for push reminders in the PWA. The reminder channel (in-app, Web Push, email) is not specified in "Reminders for intake, due tests and restock", so nothing is adopted before Q144. How it handles VAPID keys, and its fit with the Django 5 stack, were not read. The Django wrapper `django-webpush` is listed on PyPI with the GPLv3 classifier (version 0.3.6, uploaded 2024-04-30; pypi.org, 2026-11-28) and its GitHub repository was not found under the owner tried, so it is not an entry; GPL-3.0 combining is still an open question in README.md.

## (c) Open-source trackers to learn from

### Groly (supplement tracker and meal planner PWA)
- **URL:** https://github.com/peterthepeter/groly
- **Licence:** AGPL-3.0
- **AGPL-compatible:** yes (same licence)
- **Last activity:** 2026-11-27
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/peterthepeter/groly (licence `AGPL-3.0`, pushed 2026-11-27T08:52:41Z) and raw.githubusercontent.com/peterthepeter/groly/main/README.md, 2026-11-28
- **Licence note:** description: "A lightweight self-hosted grocery list, supplement tracker & meal planner PWA". README facts: per-supplement push reminders; stock tracking with reorder to a list; one-tap intake logging (amount and time); nutrients defined per unit (the example is 500 µg B12 per capsule) and summed into a daily total; weekly meal plan; a food diary that uses built-in foods plus Open Food Facts lookups. The README does not say how doses are scheduled or repeated. The code is AGPL-3.0, so reuse would be licence-compatible, but nothing is imported: the stack and data model were not read. Pattern to learn: per-unit nutrient definition and daily sum.

### PillTracker (juscghwe)
- **URL:** https://github.com/juscghwe/pilltracker
- **Licence:** Apache-2.0
- **AGPL-compatible:** yes (Apache-2.0)
- **Last activity:** 2026-08-01
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/juscghwe/pilltracker (licence `Apache-2.0`, pushed 2026-08-01T16:00:03Z) and raw.githubusercontent.com/juscghwe/pilltracker/main/README.md, 2026-11-28
- **Licence note:** the README says it is early-stage, "not production-ready and has no functional release yet"; its scheduling model, reminders and adherence states are "not stated" (meal-relative schedules, inventory and refill planning are listed as planned). Little to learn today; recorded so the next scan can check its progress.

### wger
- **URL:** https://github.com/wger-project/wger
- **Licence:** AGPL-3.0
- **AGPL-compatible:** yes (same licence)
- **Last activity:** 2026-11-27
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/wger-project/wger (licence `AGPL-3.0`, pushed 2026-11-27T20:47:08Z), pypi.org/pypi/wger/json (classifier AGPLv3+, version 2.1, uploaded 2022-10-11, so the PyPI package is stale) and raw.githubusercontent.com/wger-project/wger/master/README.md, 2026-11-28
- **Licence note:** description "Self hosted FLOSS fitness/workout, nutrition and weight tracker". README facts: an exercise wiki, custom workout routines with weight-progression rules, calorie logging with a food database "from Open Food Facts"; the README lists "Exercise/Ingredient Data: Creative Commons (see individual entries)", so the exercise data licence varies by entry and is not a single known licence. Assessment: it is a gym and routine tracker, which `exercise-reporting` says we are not ("not a gym-management app", no per-set logging). Learn only its separation of exercise data from user logs; no exercise data is taken.

## (d) Food composition and nutrient data

Nothing in this section is downloaded into the repo and no row is seeded. Licence and redistribution terms are recorded as the source states them.

### USDA FoodData Central
- **URL:** https://fdc.nal.usda.gov/download-datasets/
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q141)
- **Last activity:** unknown
- **Decision:** learn-from only
- **Verified:** unknown
- **Licence note:** fetched 2026-11-28 from https://fdc.nal.usda.gov/download-datasets/: the page states no licence, copyright, public-domain or CC0 terms; "Latest Downloads" lists Foundation Foods and Branded Foods and the Full Download as October 2026, FNDDS as October 2024 and SR Legacy as April 2018. https://fdc.nal.usda.gov/faq/ and https://fdc.nal.usda.gov/data-documentation/ (2026-11-28) also state no licence; the FAQ says only "Obtain the API with the API Key." https://www.ars.usda.gov/oc/linking-policy-and-copyright/ returned HTTP 404. The terms, rate limits and redistribution rights are therefore unknown from the pages read; nothing is recalled.
- **Provisional:** yes, no FoodData Central value or file is stored until Q141 is answered.

### Open Food Facts (database)
- **URL:** https://world.openfoodfacts.org/terms-of-use
- **Licence:** ODbL-1.0
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q142)
- **Last activity:** unknown
- **Decision:** learn-from only
- **Verified:** unknown
- **Licence note:** fetched 2026-11-28 from the URL above: the database is under the Open Database License (ODbL 1.0), with "the attribution and the sharing under the same condition of derivative works"; individual entries are under the Database Contents License (DbCL 1.0), whose conditions the page does not spell out; product photos are under Creative Commons Attribution-ShareAlike (the linked version is CC BY-SA 3.0), credit and a link to openfoodfacts.org required, and the photo licence does not cover third-party trademarks or packaging design. ODbL is not in the README licence table, so the verdict is `unknown` until looked up. The server code is a separate project: api.github.com/repos/openfoodfacts/openfoodfacts-server reports licence `AGPL-3.0`, pushed 2026-11-28T01:43:53Z (fetched 2026-11-28); the data licence above is what matters for a lookup. wger and Groly both use it for food lookups (their READMEs).
- **Provisional:** yes, no Open Food Facts record is stored or seeded until Q142 is answered; at most a live lookup by the user with attribution.

### Ciqual (ANSES French food composition table)
- **URL:** https://ciqual.anses.fr/
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q145)
- **Last activity:** unknown
- **Decision:** learn-from only
- **Verified:** unknown
- **Licence note:** fetching https://ciqual.anses.fr/ on 2026-11-28 returned HTTP 503, so terms, formats and version are unknown. A third-party wrapper exists, plemio/ciqual-mcp, "MCP for Anses Ciqual French food composition and nutritional database", licence `MIT`, pushed 2026-08-07 (api.github.com search and repo, 2026-11-28); its licence covers the wrapper, not the Ciqual data. Listed as an example of a European table for the Italian and Chinese i18n goal; not read.
- **Provisional:** yes, nothing from Ciqual is used until the page can be fetched (Q145).

## (e) Exercise and activity vocabularies and schemas

### Compendium of Physical Activities (MET values)
- **URL:** https://pacompendium.com/
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q143)
- **Last activity:** unknown
- **Decision:** learn-from only
- **Verified:** unknown
- **Licence note:** fetched 2026-11-28 from the URL above: the latest edition is the "2024 Adult Compendium Update" (published January 2024, Journal of Sport and Health Science; earlier editions 1993, 2000, 2011). "One MET is defined as 1 kcal/kg/hour"; "Please do not change MET values or combine activities with different MET levels." No licence name and no copyright notice appear. "The Adult, Older Adult, and Wheelchair Compendia are free to use for commercial purposes"; "Researchers may download the compendium for use in their research"; teachers may use portions for education; "Please cite the Compendium website or publication(s)"; the download is by request ("To request a copy of the compendium in Excel format, please email us"). The page does not address redistribution beyond those lines, so committing the table to git is not settled.
- **Provisional:** yes, no MET value is committed until Q143 is answered. `exercise-reporting` captures activity at the level of what the user does; MET values would matter only for the TDEE activity factor in `nutrition-management`, whose formula the M04 change must cite from a source (not chosen in this scan).

### Open mHealth schemas
- **URL:** https://github.com/openmhealth/schemas
- **Licence:** Apache-2.0
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q146)
- **Last activity:** 2026-08-26
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/openmhealth/schemas (licence `Apache-2.0`, pushed 2026-08-26T20:17:30Z) and raw.githubusercontent.com/openmhealth/schemas/master/README.md, 2026-11-28
- **Licence note:** the README says the repository holds Open mHealth schemas with sample data, a validator and a Kotlin SDK, and that "schemas modeling sleep and physical activity measures and metadata are superseded" by IEEE 1752.1 schemas; the README states no licence. `Apache-2.0` above is GitHub's detection only. The project site https://www.openmhealth.org/documentation/ states "Copyright © 2011-2019 Open mHealth All Rights Reserved" and links a Terms of Use page whose text was not returned (2026-11-28). GitHub's `Apache-2.0` and the site's wording are not reconciled (Q146). Superseded by IEEE 1752.1 for activity, whose text was not fetched.

## (f) Wearable and activity exports

### Open Wearables (the-momentum)
- **URL:** https://github.com/the-momentum/open-wearables
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2026-11-27
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/the-momentum/open-wearables (licence `MIT`, pushed 2026-11-27T13:47:04Z; the path `openwearables/open-wearables` returned 404) and raw.githubusercontent.com/the-momentum/open-wearables/main/README.md, 2026-11-28
- **Licence note:** description "Self-hosted platform to unify wearable health data through one AI-ready API". README facts: cloud providers Garmin, Oura, Whoop, Polar, Suunto, Strava, Withings, Ultrahuman, SensorBio, Google Health and Fitbit (marked deprecated); on-device Apple Health, Google Health Connect and Samsung Health; a full Apple Health XML export upload; data types include daily activity summaries, sleep, workouts, time series (heart rate, HRV, SpO2, weight, steps, energy), nutrition meals with energy and macronutrients where the source gives them. The README does not say which provider delivers which type. Assessment: wearable import is a `biomarkers-and-labs` requirement ("Import from wearable export files", still open in s01), not an `exercise-reporting` one; the M04 change should not pull it in. Recorded as the main reuse candidate for that later task.

### fitdecode
- **URL:** https://github.com/polyvertex/fitdecode
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2025-08-06
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/polyvertex/fitdecode (licence `MIT`, pushed 2025-08-06T08:06:41Z) and pypi.org/pypi/fitdecode/json (license field `MIT`, version 0.11.0, uploaded 2025-08-06, summary "FIT file parser and decoder"), 2026-11-28
- **Licence note:** reads Garmin/ANT FIT files. `exercise-reporting` forbids per-set tracking, so the FIT workout detail is not needed by M04; kept as the reader to evaluate for the wearable-import task.

### python-fitparse
- **URL:** https://github.com/dtcooper/python-fitparse
- **Licence:** MIT
- **AGPL-compatible:** yes (MIT)
- **Last activity:** 2025-01-28
- **Decision:** reject
- **Verified:** api.github.com/repos/dtcooper/python-fitparse (licence `MIT`, pushed 2025-01-28T22:09:15Z) and pypi.org/pypi/fitparse/json (license field `MIT`, version 1.2.0, uploaded 2020-09-07), 2026-11-28
- **Licence note:** rejected as a second FIT reader: the last PyPI release is 2020-09-07 and fitdecode is newer (assessment). No functional comparison was run.

## (g) FHIR resources for intake, nutrition and exercise

### HL7 FHIR (MedicationAdministration, NutritionOrder, NutritionIntake)
- **URL:** https://github.com/HL7/fhir
- **Licence:** unknown
- **AGPL-compatible:** unknown — question in docs/QUESTIONS.md (Q55)
- **Last activity:** 2026-11-25
- **Decision:** learn-from only
- **Verified:** api.github.com/repos/HL7/fhir (licence `NOASSERTION`, pushed 2026-11-25T06:48:32Z) and the pages https://hl7.org/fhir/R4/medicationadministration.html, https://hl7.org/fhir/R4/nutritionorder.html and https://hl7.org/fhir/R5/nutritionintake.html, 2026-11-28
- **Licence note:** same open question as the m02 and m03 scans (Q55), not re-decided. Read facts (each page read only in part, the first 100,000 characters). MedicationAdministration (R4): Maturity Level 2, Trial Use, an event; required `status`, `medication[x]`, `subject`, `effective[x]`; its scope is "the administration of all medications and vaccines" including "self-administrations of oral medications", and it does not mention supplements; "A medication statement is not a part of the prescribe->dispense->administer sequence", so an intake log entry fits MedicationAdministration and "what a user takes" fits MedicationStatement (M03). NutritionOrder (R4): Maturity Level 2, Trial Use, a request (`status`, `intent`, `patient`, `dateTime` required) for an oral diet (with `schedule`, `nutrient`, `texture`), oral supplements or enteral formula, described for inpatient settings; parenteral nutrition is excluded. NutritionIntake (R5, not R4): Maturity Level 1, Trial Use, an event; required `status`, `subject`, `consumedItem` (with `type` and `nutritionProduct`); `ingredientLabel.nutrient` and `.amount` give total nutrient consumed; no `intakeAmount` element exists. Assessment: a meal or fasting-window log could map to NutritionIntake, but it is R5 and the stack's FHIR library targets were not checked against R5; a diet pattern (OMAD, 16/8) has no resource that was found. No FHIR resource for exercise or therapy sessions was read (Q147). Each is an export mapping target, not a storage schema.

## Decisions for the M04 OpenSpec change

No dependency is added in this task. The M04 change cites this scan and takes these decisions as input; each library is re-checked there against the scenarios.

- **(a) Scheduling:** a constraint solver, deterministic and explainable (spec). OR-Tools is the first candidate (Apache-2.0, maintained), python-constraint2 the lighter one; adding either needs Fabio's approval (Q140).
- **(b) Cadence and reminders:** a typed cadence modelled on get-based's schedule (M03) is the default; python-dateutil, icalendar and pywebpush are learn-from only until the reminder channel is decided (Q144).
- **(c) Trackers:** Groly, PillTracker and wger are design references only (per-unit nutrient definition, one-tap logging, stock-to-reorder, separation of exercise data from logs); no code imported.
- **(d) Food data:** no food-composition data is stored until the terms of FoodData Central (Q141), Open Food Facts (Q142) and Ciqual (Q145) are settled. The macronutrient split in `nutrition-management` is a user-declared typical split and needs no database.
- **(e) Exercise:** declared activity level, done/not-done, no MET table until Q143; VO2max is stored as a biomarker (`exercise-reporting`, `biomarkers-and-labs`) but its code system, unit and method vocabulary were not scanned here or in M02 (Q149).
- **(f) Wearables:** out of M04; Open Wearables and fitdecode are candidates for the wearable-import task.
- **(g) Export:** MedicationAdministration (intake events) and, for meals, NutritionIntake (R5) are mapping targets under Q55; DRUG_EXPOSURE for intake events reuses the M03 mapping.
- **Gaps:** VO2max code, unit and method vocabulary (Q149), therapy parameter vocabularies (Q148) and the cost requirement were not scanned.
