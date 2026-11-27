# get-based export, backup and migration archive: format (2026-11-27)

Purpose: the facts the biohack.it importer (x01, "Import of a get-based archive") needs. Everything below was read on 2026-11-27 from the source of `elkimek/get-based`. Nothing is recalled from memory. What the source does not show is marked **unknown**.

## Sources and pinned commits

| Label | What | Pinned at |
|---|---|---|
| **M** (main) | `main` branch, head commit at the time of reading | `002c3e1e8d256854102eefe51833bca75adda1a6` (2026-11-26, merge of #1739) |
| **P** (PR) | pull request #1719 "Add checked browser migration and prepare the self-hosting transition", **open, not merged, owner review** | PR head `9e72e528ee9d673bbf48f6d93d958be1ec0b76bb` (branch `codex/hosted-transition`) |

Citations read `M js/file.ts:LINE` or `P js/file.ts:LINE`: the file at that pinned commit, e.g. `https://raw.githubusercontent.com/elkimek/get-based/<sha>/js/file.ts`. Line numbers are of the raw file.

Licence and activity, re-checked from `https://api.github.com/repos/elkimek/get-based` on 2026-11-27: licence `AGPL-3.0` (SPDX id from the API), 168 stars, default branch `main`, last push 2026-11-26T12:57:19Z. AGPL-3.0 is compatible with this project. The format itself carries no declared schema or specification document that was found in the files read; the format is defined only by code (**no documented, versioned schema: unknown whether one exists elsewhere**).

## Three containers

get-based has three file shapes that a user may hold. They share an inner data model but differ in the wrapper.

#### 1. Single-client export (JSON, plain text)
- Built by `buildClientExportObject` (M js/export.ts:212-286) and downloaded as `getbased-<client>-<YYYY-MM-DD>.json` (M js/export.ts:303).
- Top level: `version: 2`, `exportedAt` (ISO string), `profile` object (name, sex, dob, location, tags, notes, status, avatar, pinned, height, heightUnit), plus the profile data fields spread at top level: `entries`, `markerSources` lives inside entries (see below), `importSnapshots`, `manualValues`, `markerNotes`, `markerValueNotes`, `customMarkers`, `refOverrides` and many non-lab fields (M js/export.ts:224-283).
- Detection on import: no `type`, has `entries` array (M js/export-import.ts:164-172). A `profile.name` makes the importer create a new profile (M js/export-import.ts:174-182).
- Version check: the importer does **not** check `version` for this shape in the lines read (M js/export-import.ts:141-182). Whether it checks elsewhere: **unknown**.

#### 2. All-clients bundle (JSON, plain text)
- Built by `buildAllDataBundle` (M js/export.ts:312-346), downloaded as `getbased-backup-<YYYY-MM-DD>.json` (M js/export.ts:359).
- Top level: `version: 2`, `type: 'database'`, `exportedAt`, `profiles[]`, optional `wallet: {nodeUrl}` (M js/export.ts:315-345). Each profile: `id`, `name`, `sex`, `dob`, `location`, `tags`, `notes`, `status`, `avatar`, `pinned`, `height`, `heightUnit`, `data` (the profile data, holding `entries` etc.), `nutrition`, optional `chat` (M js/export.ts:328-336).
- Detection: `json.type === 'database' && Array.isArray(json.profiles)` (M js/export-import.ts:160); a backup check elsewhere requires `backup.type === 'database' && backup.version === 2` (M js/backup.ts:424).

#### 3. Full browser backup `labcharts-backup` (JSON)
- Interface `BackupSnapshot` (M js/backup.ts:43-49): `format: 'labcharts-backup'`, `version: 1`, `createdAt`, `encrypted: boolean`, `encryptionSalt: string | null`, `settings`, `profileList: string`, `profiles[]`, `wearableIDB`, `cycleIDB`, `cycleImportMeta`. Downloaded as `labcharts-backup-<date>.json` (M js/backup.ts:402).
- Stored values are the **raw stored form**, encrypted if the user's in-app encryption is on (M js/backup.ts:118-120, :173-178, :323-324). Encryption algorithm, key derivation and ciphertext layout of this in-app encryption inside the backup: the source for the in-app value format is `v1:<iv>:<ct>` as read in P js/migration-crypto.ts:40-43 (AES-GCM). Key derivation for it: PBKDF2-SHA-256 from the app passphrase with the stored salt, 600000 iterations (P js/migration-portable.ts:25-38 calls `deriveMigrationKey`, P js/migration-crypto.ts:11-15). Whether main uses the same parameters for the in-app lock: **unknown** (not read).
- Detection on import: `json.format === 'labcharts-backup'` (M js/export-import.ts:144); anything else must have `profileList` (M js/backup.ts:431).

#### 4. Planned migration archive (PR #1719, not merged)
Status: open pull request, "keep this PR unmerged ... Production policy remains inactive" (issue/PR #1719 body). Format may change before release. Do not treat as stable.
- **Outer envelope** (P js/migration-crypto.ts:7-10, :16-25):
  `{ "format": "getbased-migration", "version": 1, "iterations": 600000, "salt": <base64, 16 bytes>, "iv": <base64, 12 bytes>, "ciphertext": <base64> }`, written as JSON, content type `application/json` (P js/migration-archive.ts:68).
- **Password protection:** key = PBKDF2, hash SHA-256, 600000 iterations, from the migration password and `salt`; cipher AES-GCM 256, 96-bit `iv`, additional authenticated data = the ASCII string `getbased-migration:1` (P js/migration-crypto.ts:5, :11-15, :22). Minimum password length 12 characters on creation (P js/migration-crypto.ts:17). Decrypt failure message: "The password is incorrect or the migration file is damaged." (P js/migration-crypto.ts:37).
- **Size cap:** 512 MiB decoded (P js/migration-crypto.ts:6; PR body "documented 512 MiB decoded-content cap").
- **Version field:** the envelope `version` must be exactly `1` and `iterations` exactly `600000`, else "Unsupported migration archive." (P js/migration-crypto.ts:28-30).
- **Decrypted content** (`MigrationArchive`, P js/migration-archive.ts:12-16): `format: 'getbased-migration-content'`, `version: 1`, `createdAt` (ISO), `sourceOrigin`, `files[]` (`path`, `bytes` base64), `reconnect[]` (list of things to set up again), and `MigrationPortableData` (P js/migration-portable.ts:11-14): `local` (a snapshot of the browser's localStorage key to string), `databases[]` (IndexedDB stores: name, version, stores with `records` of `key` and `value`), `credentials`, `syncRecovery` (`mnemonic`, `ownerId`, `relay`; a secret), `inventory` (counts: profiles, meals, wearableRows, chatRecords, textDrafts, savedSnapshots; boolean walletRecovery). Validation: P js/migration-archive.ts:73-131.
- **Lab data inside the archive:** the archive is a snapshot of browser storage, not a lab schema. Per-profile data sits in `local` under a key built as `labcharts-<profileId>-<suffix>` (M js/profile-storage-key.ts:4); the lab data key is `labcharts-<profileId>-imported` (M js/export.ts:216 `profileStorageKey(profileId, 'imported')`). Whether that value inside `local` is plain JSON or the `v1:<iv>:<ct>` encrypted form depends on the source app's own encryption (P js/migration-portable.ts:25-38). When it is encrypted, the importer would need **a second secret, the original app passphrase** (P js/migration-portable.ts:27). The exact decoding of the `imported` value after decryption is **unknown** (not read); assume it matches the portable profile projection of container 1 only after verifying on a real archive.
- **Secrets in the archive:** `syncRecovery.mnemonic` and `credentials` are present (P js/migration-portable.ts:6, :12). An importer must not read, store or log them.
- Intended consumer: restore into a self-hosted get-based (P js/migration-restore.ts). A reader for any other system is not described: **unknown**.

## Lab data model (shared by containers 1 to 3)

Per profile, a list `entries[]`; one entry is one lab sample date (it may also carry `panelId`). Typed in M js/lab-entry.ts:4-20 and M js/pdf-import-commit.ts:105-179.

| Field | Meaning, from the source | Citation |
|---|---|---|
| `entries[].date` | sample date string; an entry without `date` or `markers` is skipped on import. Time zone and exact format (probably `YYYY-MM-DD`): **unknown** | M js/export-import.ts:205 |
| `entries[].markers` | object: marker key to a **number** (the value). No unit is stored beside each value | M js/lab-entry.ts:6, M js/pdf-import-commit.ts:175 |
| marker key scheme | a get-based dot key `<category>.<marker>`, e.g. `lipids.cholesterol`, `biochemistry.glucose`, `diabetes.homaIR`, `hematology.hematocrit`. Not LOINC, not UCUM, not an ontology code. Custom markers (`customMarkers`) can add keys outside the built-in catalogue | M js/marker-schema/lipids.ts:8-16, M js/lab-entry.ts:34-39, M js/schema.ts:227-231 |
| unit | the **schema's canonical unit** (SI-leaning), fixed per marker by the catalogue (`unit` in the marker definition, e.g. `lipids.cholesterol` is `mmol/l`, `lipids.apoB` is `g/l`); values are converted to it at import time by `normalizeToSI` (M js/pdf-import-commit.ts:175, M js/schema.ts:225-262). A unit is therefore not in the entry; it must come from the catalogue at the matching get-based version (the catalogue can change between versions: **catalogue version in the file: unknown**) | M js/marker-schema/lipids.ts:8-16, M js/marker-schema/types.ts:2-12 |
| LOINC / other code | **no LOINC field found** in the marker definition type (M js/marker-schema/types.ts:2-12) nor the lipid catalogue (M js/marker-schema/lipids.ts); the other catalogue files were not each read: **unknown whether any carries a code** | as cited |
| `entries[].context` | object, e.g. `sampleTime` (`HH:MM`), `fasting` (boolean) | M js/lab-entry.ts:47-126 |
| `entries[].collectionContextSources` | per field, the snapshot id it came from | M js/lab-entry.ts:83-91 |
| `entries[].deletedMarkers` | marker key to a deletion timestamp (tombstone). A marker listed here is deleted | M js/lab-entry.ts:34, M js/pdf-import-commit.ts (via `deleteLabEntryMarker`, :133) |
| `entries[].updatedAt` | timestamp number (milliseconds since epoch, from `Date.now()`) | M js/pdf-import-commit.ts:100, :160 |
| `entries[].sourceFile`, `sourceFiles[]` | name(s) of the report file(s) imported into this entry | M js/pdf-import-commit.ts:155-159 |
| `entries[].importHash` | hash of the imported file when present | M js/pdf-import-commit.ts:154 |
| `entries[].manualOriginals` | marker key to the original imported value (or `null`) kept when a value is edited | M js/lab-entry.ts:276, :304, :349 |
| `importSnapshots[]` | one per imported report: `id`, `date`, `fileName`, `markers[]`, `excludedIndices[]`. Each snapshot marker has `rawName`, `suggestedName`, `mappedKey`, `suggestedKey`, `matched`, and, from the import code, `value` and `unit` (read at M js/pdf-import-commit.ts:175) and report-range context such as `refMax` (M js/schema.ts:6). Exact full list: **unknown** (open-ended index signature) | M js/profile-marker-alias-migrations.ts:6-16, M js/profile-import-provenance.ts:18-31, M js/pdf-import-commit.ts:175 |
| `manualValues` | object, key `<markerKey>:<date>` to the original numeric value before a manual edit | M js/profile-import-provenance.ts:12, M js/lab-marker-mutations.ts:44 |
| `markerValueNotes` | key `<markerKey>:<date>` to a note up to 500 characters | M js/lab-marker-mutations.ts:53-55 |
| reference ranges | built-in catalogue `refMin`, `refMax` (and `refMin_f`, `refMax_f` for females); per-user overrides in `refOverrides`. Laboratory-specific ranges from the report: inside snapshot marker context as `refMax` (open). Not needed for the biohack.it import: it keeps its own cited ranges | M js/marker-schema/lipids.ts:10, M js/export.ts:237, M js/schema.ts:215 |

## Per-value provenance (the parts that must not be lost)

#### `markerSources` (per entry, per marker)
Shape: `entries[].markerSources: { [markerKey]: LabMarkerSource | null }`, with
```
LabMarkerSource {
  reported?: boolean         // true
  file?: string | null       // report file name, null when not from a file
  at?: number                // timestamp (milliseconds)
  snapshotId?: string        // id of the importSnapshots[] row that produced the value
  derivedFrom?: string[]     // marker keys the value was calculated from
  manuallyEdited?: boolean   // value was edited by the user after import
}
```
Declared at M js/lab-entry.ts:8 and :17-20 (`manuallyEdited` and `file`, `at`, `snapshotId` typed loosely as `unknown`; the writers below show the values).

- **`file`, `at`, `snapshotId`**: written when a value is committed from an import: `source: { file: result.fileName || null, at: importTs, snapshotId, ... }` (M js/pdf-import-commit.ts:175-178).
- **`reported: true`**: the value was printed on the report, so it must not be recalculated. In the source it is written for `diabetes.homaIR` only (M js/pdf-import-commit.ts:177, M js/lab-marker-mutations.ts:40,49) and read to skip recalculation (M js/lab-entry.ts:187, :224). Whether other markers ever get `reported`: **not seen in the files read; unknown**.
- **`derivedFrom`**: a **calculated** value. Written only for `diabetes.homaIR` when get-based computes it from glucose and insulin: `derivedFrom: ['biochemistry.glucose', insulinKey]` (M js/lab-entry.ts:199-208), with the formula `round(glucose * insulin / 22.5, 2 decimals)` (M js/lab-entry.ts:192), skipped when `context.fasting === false` (M js/lab-entry.ts:191). It is removed when the value is reported or edited (M js/lab-marker-mutations.ts:40, :49). Other markers with `derivedFrom`: **not seen; unknown**. The key group `calculatedRatios.*` exists in the catalogue (M js/profile-marker-alias-migrations.ts:106, M js/marker-schema/calculated-ratios.ts listed in the tree); whether those values carry `derivedFrom`: **unknown**.
- **`manuallyEdited: true`**: set when the user edits a value that came from an import (it has `snapshotId` or `file`): `{ ...source, at: now, manuallyEdited: true }` (M js/lab-marker-mutations.ts:48). For a value with no import origin the source is just `{ file: null, at }` (same line). It is removed again when the user reverts to the original (M js/lab-marker-mutations.ts:41) and an older-edit repair sets it (M js/profile-import-provenance.ts:35-37).

A marker value with **no** `markerSources` entry: a legacy or purely manual value, origin **unknown**. The source's own repair code refuses to guess for untracked legacy values (M js/profile-import-provenance.ts:13-15).

#### `importedWith` (per entry, not per marker)
`entries[].importedWith = { provider: string | null, modelId: string | null }` (M js/pdf-import-commit.ts:150-153), filled from `result.costInfo`, which the import flow builds from the AI provider and model actually used: `costInfo = { provider, modelId, inputTokens, outputTokens, cost }` (M js/pdf-import.ts:621-629).
- It sits on the **entry (the sample date), not on the marker**; it is **overwritten** by each later import commit into the same entry (the assignment is unconditional, M js/pdf-import-commit.ts:150). So after two imports the file shows only the last provider/model, and it cannot say which marker was read by which model.
- Which value was imported (and is therefore candidate for "read by an AI model") is told by that marker's `markerSources[key].snapshotId` / `file`, which marks an import origin (M js/pdf-import-commit.ts:177).
- When the import did not use an AI model (for example a spreadsheet path, `js/pdf-import-spreadsheet.ts`): whether `importedWith` is then absent or holds nulls: **unknown** (the `|| null` fallbacks at M js/pdf-import-commit.ts:151-152 allow nulls).
- The type of `importedWith` is not declared in `LabEntryDraft` (it is covered only by its index signature, M js/lab-entry.ts:15).

## What is not in these files (so the importer must not assume it)
- Per-value **unit**: not stored (see above); derived from the catalogue. The importer's use of it is in the OpenSpec scenario "Mapping row cites the get-based catalogue unit" (biomarkers-and-labs, change x01-ecosystem-reuse).
- **LOINC/UCUM/ontology codes**: none found.
- A **schema document** or **JSON Schema** for the export: none found.
- A **version of the marker catalogue**: none found.
- Round trip **import of the migration archive into a non-get-based system**: not described.

## Implemented

Part 2b (2026-11-27) reads the single-client export and the all-clients bundle, version 2, and stores a confirmed import: one `LabReport` (`import_source` `getbased`, `import_format` `getbased-export` or `getbased-database`, version 2, fixed file name `getbased-export.json`) and one `LabResult` per matched marker, each with a `LabResultGetbasedProvenance` row holding `markerSources` (`reported`, `file`, `at`, `snapshotId`), `manuallyEdited` and the entry-level `importedWith` (`modelId`, `provider`). Results are stored `entered`. Not yet: `labcharts-backup` and the migration archive. API: `docs/api-labs.md`. Defaults: Q101, Q102.

## Consequences for the importer (links to the spec)
Spec: `openspec/changes/x01-ecosystem-reuse/specs/biomarkers-and-labs/spec.md`, requirement "Import of a get-based archive". Decisions and defaults: docs/QUESTIONS.md Q91 to Q96. The mapping from get-based marker keys to LOINC-coded analytes has **no source yet**: it must be a stored, cited table; none is invented here.

Related: [get-based strategy watch](getbased-watch-2026-11.md), [integrations scan](integrations.md), [GIVEBACK register](GIVEBACK.md).
