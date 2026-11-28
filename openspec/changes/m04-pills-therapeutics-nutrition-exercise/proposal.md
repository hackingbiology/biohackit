# M04 Pills, Therapeutics, Nutrition and Exercise — OpenSpec Change Proposal

**Author:** autodev · **Date:** 2026-11-28 · **Module issue:** unknown (no M04 issue found)
**Capabilities in scope:** `pills-management`, `therapeutics-management`, `nutrition-management`, `exercise-reporting`, plus `daily-log-and-adherence` (where intake events and reminders live).
**Supersedes:** a first attempt (`m04-openspec-change-pills-therapeutics-nutrition-e`) that failed review and was not merged. Its blocking finding (an export that mapped every intake event, taken or not, to a DRUG_EXPOSURE row) is fixed here by an explicit state filter, see "Intake export".

## Why
`openspec/specs/{pills-management,therapeutics-management,nutrition-management,exercise-reporting}/spec.md` describe what a user takes, when, which sessions they do, what they eat and how they move. Nothing is built. M03 already gives the Substance, Product and Protocol models and the OMOP DRUG_EXPOSURE mapping (`backend/protocols/omop.py`, `docs/omop/drug-exposure-mapping.md`). M04 turns the four specs into a schedule of intakes and sessions that the daily log (M05) can check off, without inventing any dose, range, MET value, food composition value or code.

## What changes
- **Cadence and schedule (`pills-management`, `therapeutics-management`):** a typed cadence (mode, times per day, days of week, interval in days; the shape comes from get-based, see the M03 scan) and a deterministic daily allocation of intakes into slots. Competing-compound, meal and spacing constraints are data entered with a cited source; an unsourced constraint is listed, not enforced as a rule.
- **Solver:** the scan names OR-Tools (Apache-2.0) and python-constraint2 (BSD-2-Clause). **No dependency is added by this change.** The solver task group is blocked on Q140; until approved, only a plain deterministic allocation without a new package is in scope (task group TG-c).
- **Therapies (`therapeutics-management`):** a therapy catalog with typed parameters and a cadence. A parameter has a name and a unit; it has no default and no permitted range unless one is cited (Q148).
- **Nutrition (`nutrition-management`):** a declared eating pattern and window, a user-declared macronutrient split, TDEE computed by a formula whose source is cited at implementation (Q153). No food composition data is stored (Q141, Q142, Q145).
- **Exercise (`exercise-reporting`):** a declared activity profile, done/partial/skipped/missed logging, VO2max as a biomarker with a free-text method and a unit and no invented code (Q149). No MET table (Q143).
- **Reminders (`daily-log-and-adherence`):** in-app only (Q144).
- **Intake export (`daily-log-and-adherence`):** see below.

## Intake export
Only intakes marked **done** (taken as planned) and **partial** (something was taken) describe an exposure. A **skipped** or **missed** intake did not happen and writes **no** DRUG_EXPOSURE row. The rule depends on the stored adherence state and the state is never guessed: an event without a recorded state exports nothing. The exposure date is the date of the intake event, and `quantity` stays empty and is never taken from the planned dose (Q152). A state is set only by an explicit user action, never by a rule. FHIR MedicationAdministration `status` codes `completed`, `stopped` and `not-done` were checked against the R4 value set (https://hl7.org/fhir/R4/valueset-medication-admin-status.html, fetched 2026-11-28; `completed`: "All actions that are implied by the administration have occurred"; `not-done`: "The administration was terminated prior to any impact on the subject (though preparatory actions may have been taken)"; `stopped`: "Actions implied by the administration have been permanently halted, before all of them occurred"). The mapping of each state is in the delta; the defaults are in Q150–Q152. Scope follows Q147: intake events only; nutrition, exercise and therapy-session export are left to a later task.

## Ecosystem scan
Reuse decisions: [docs/ecosystem/m04-pills-therapeutics-nutrition-exercise.md](../../../docs/ecosystem/m04-pills-therapeutics-nutrition-exercise.md) (change `x01-ecosystem-reuse`; facts fetched 2026-11-28).

- **(a) Solver:** OR-Tools first candidate, python-constraint2 lighter; neither installed (Q140). The change must show determinism and a stated reason per separation before adoption.
- **(b) Cadence and reminders:** typed cadence; python-dateutil, icalendar and pywebpush are learn-from only. Reminders in-app (Q144).
- **(c) Trackers:** Groly, PillTracker, wger are design references only (per-unit nutrient definition, one-tap logging, stock-to-reorder, exercise data apart from logs). No code imported.
- **(d) Food data:** none stored or seeded (Q141 FoodData Central, Q142 Open Food Facts, Q145 Ciqual).
- **(e) Exercise:** no MET table (Q143); Open mHealth is learn-from only (Q146).
- **(f) Wearables:** out of scope (belongs to `biomarkers-and-labs`).
- **(g) Export:** intake events only (Q147); DRUG_EXPOSURE reuses the M03 mapping, FHIR hand-written against the spec and blocked by Q55.
- **Gaps:** therapy parameter vocabularies (Q148), VO2max code and unit (Q149), protocol cost (belongs to `procurement-and-inventory`).

## Out of scope
The daily log screen and adherence computation (M05, only the export and reminder rules of intake events are specified here); stock and purchase (`procurement-and-inventory`; the restock link already exists in `pills-management`); wearable import; calendar `.ics` export; Web Push and email reminders (Q144); food database lookups; n-of-1 analysis (M06); AI narration (M07). Protocol cost is not part of this change.

## Scientific-data policy
No dose, range, MET value, TDEE factor, food composition value, LOINC/RxNorm/ATC code, URL or package name is written in this change unless fetched and cited on the day (the FHIR status codes above are the only coded values). Where one is needed, the scenario says "from a cited source" and a question with a default is recorded. This change seeds nothing.

## Decisions taken (defaults; Fabio may reverse)
| # | Decision | Default |
|---|---|---|
| D1 | Solver | no dependency; plain deterministic allocation first, OR-Tools/python-constraint2 after approval (Q140) |
| D2 | Food data | nothing stored or seeded (Q141, Q142, Q145) |
| D3 | MET | no table; TDEE activity factor from a cited source (Q143, Q153) |
| D4 | Reminders | in-app only (Q144) |
| D5 | Export | intake events only, state-filtered (Q147, Q150–Q152) |
| D6 | State names | done = taken-as-planned, partial = partial-dose, skipped = intentionally-skipped, missed = forgotten (Q150) |
| D7 | Constraints | entered with a cited source; none seeded (Q154) |
