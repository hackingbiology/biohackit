## ADDED Requirements

### Requirement: Import of a get-based archive
The system SHALL let a user import lab results from a get-based export, backup or migration archive (format: `docs/ecosystem/getbased-archive-format.md`) in two steps, a preview and a confirmation. Nothing SHALL be saved before the user confirms. Every get-based marker SHALL be matched to a stored, LOINC-coded `Biomarker` only through a stored mapping that cites its source, or be listed as not recognised with the reason; a marker SHALL never be matched by name guessing. get-based's per-value provenance (`importedWith`, `markerSources` with `reported`, `manuallyEdited` and `derivedFrom`) SHALL be kept and SHALL never be dropped, so that a value read by an AI model, a calculated value or an edited value is never stored or shown as an ordinary measured laboratory result. A result SHALL be exempt from the "check against your report" flag only when `importedWith` positively shows a non-AI path; otherwise it is flagged and stored `entered`. Exactly one profile of the archive SHALL be imported, chosen by the user, and profile identity fields, chat, nutrition, wallet, credentials and the Sync recovery record SHALL never be stored or logged. The unit of every measured mapping row (a row with a Biomarker; deny-list rows carry no unit) SHALL cite the get-based catalogue unit for that marker at a pinned commit, and a marker whose measured row cites no unit SHALL be listed as not recognised. Calculated markers SHALL never be stored as measured, whether or not `derivedFrom` is present.

#### Scenario: Preview before anything is saved
- **WHEN** a user uploads a get-based archive
- **THEN** the system returns a preview listing every result with its marker, value, unit, date and status, and a summary of counts
- **AND** no report and no result has been stored

#### Scenario: Markers matched through a cited mapping or not recognised
- **WHEN** the preview is built
- **THEN** each marker whose get-based key has a measured mapping row (one with a `Biomarker`) that cites its unit is shown matched to its LOINC-coded `Biomarker`, with the mapping's source
- **AND** a key with a deny-list row is handled by "Calculated ratios are never stored as measured", and a measured row with no cited unit is handled by "Mapping row cites the get-based catalogue unit"
- **AND** every other marker, with no row of any kind for its key, is listed as not recognised with the reason, "no mapping stored for this get-based marker"
- **AND** no marker is matched by comparing names

#### Scenario: Mapping row cites the get-based catalogue unit
- **WHEN** a measured mapping row (one with a `Biomarker`) is stored or used
- **THEN** it records the get-based catalogue unit for that marker key with a source path and pinned commit (for example `js/marker-schema/<group>.ts@<sha>`)
- **AND** the importer stores the value only in that unit or converts it through a stored UCUM conversion, and never guesses a unit
- **AND** a marker whose measured mapping row has no cited unit is listed as "not recognised: unit not verified" and blocks confirm like any other not recognised row

#### Scenario: Confirm refused while a row is not recognised
- **WHEN** a user confirms an import whose preview still holds a not recognised row
- **THEN** the system refuses with a message listing those rows, and nothing is stored

#### Scenario: Undo of a confirmed import
- **WHEN** the user undoes a confirmed get-based import
- **THEN** the report created by that import and all its results are removed
- **AND** results and reports not created by it are untouched

#### Scenario: Origin of the import is recorded
- **WHEN** an import is confirmed
- **THEN** the stored report records its origin as get-based, the archive format name and version, and the file name

#### Scenario: Values read by an AI model are flagged and stay unconfirmed
- **WHEN** an archive entry carries `importedWith` and a result in it has an import origin in `markerSources` (a `snapshotId` or a `file`)
- **THEN** the preview flags the row in plain words, "read by an AI model, check against your report", and shows the `modelId` and `provider` (or "unknown" where they are empty), qualified as "last import into this date; the model for this value is unknown"
- **AND** the stored result keeps `modelId` and `provider` as entry-level provenance with that same qualifier, never as the proven model of that single value
- **AND** it is stored with validation state `entered`, never `user_confirmed`, until the user confirms that result

#### Scenario: Import origin without importedWith fails closed
- **WHEN** a result's `markerSources` record has an import origin (a `snapshotId` or a `file`) but its entry has no `importedWith`
- **THEN** the preview flags the row "may have been read by an AI model, check against your report", because a non-AI path cannot be shown
- **AND** it is stored `entered`, never `user_confirmed`, until the user confirms that result

#### Scenario: Result without markerSources fails closed
- **WHEN** a marker has no `markerSources` record
- **THEN** the row is stored with provenance "origin unknown in get-based", validation state `entered`, and flagged "origin unknown, check against your report"
- **AND** it is never stored `user_confirmed` until the user confirms that result

#### Scenario: Result whose markerSources has no import origin fails closed
- **WHEN** a result's `markerSources` record has no `snapshotId` and no `file` (a manual entry in get-based)
- **THEN** the preview flags the row "origin not shown in get-based, check against your report"
- **AND** it is stored `entered`, never `user_confirmed`, until the user confirms that result

#### Scenario: Deleted markers are not imported
- **WHEN** a marker is listed in an entry's `deletedMarkers`
- **THEN** the preview shows it as "not imported: deleted in get-based"
- **AND** it is never stored and does not block confirm

#### Scenario: Exactly one profile is imported
- **WHEN** the archive holds more than one profile
- **THEN** the preview makes the user choose exactly one profile and only that profile's entries are previewed and imported
- **AND** nothing is imported until a profile is chosen

#### Scenario: Identity and non-lab data are never stored
- **WHEN** an archive is previewed or confirmed
- **THEN** profile identity fields (name, sex, date of birth, location, notes, avatar), chat, nutrition and wallet data are never stored and never logged

#### Scenario: Calculated ratios are never stored as measured
- **WHEN** a marker is in the `calculatedRatios` group, or its key has a deny-list row of kind `calculated` in the mapping table, whether or not `derivedFrom` is present
- **THEN** the row is shown as "not imported: calculated" and is never stored as a laboratory result
- **AND** it is excluded from the confirm refusal
- **AND** the mapping table may hold a deny-list row for a key (no `Biomarker`, a cited reason, kind `calculated`), and refuses only a measured mapping row (one with a `Biomarker`) for such a key; deny-list rows carry no unit, so the unit-citation rule does not apply to them

#### Scenario: Per-value markerSources is kept
- **WHEN** a result is stored from an archive marker that has a `markerSources` record
- **THEN** the record's `reported`, `file`, `at` and `snapshotId` values are kept as provenance on the stored result

#### Scenario: Calculated values are not stored as measured
- **WHEN** a marker's `markerSources` record has `derivedFrom`
- **THEN** the row is shown as "not imported: calculated by get-based from other markers, not measured", with the reason
- **AND** it is never stored as a laboratory result
- **AND** it is excluded from the confirm refusal, so an archive holding such rows (for example HOMA-IR) can still be confirmed once every other row is matched; the preview states how many rows were left out

#### Scenario: Edited values are labelled
- **WHEN** a marker's `markerSources` record has `manuallyEdited` set
- **THEN** the preview and the stored result are labelled "edited in get-based after import"
- **AND** the label stays on the stored result

#### Scenario: Password-protected archive handled in memory only
- **WHEN** a user uploads a password-protected get-based migration archive and enters its password
- **THEN** the archive is decrypted in memory only
- **AND** only the confirmed results and their provenance are stored; the password, the decrypted archive as a whole, credentials and the Sync recovery record are never stored and never logged
- **AND** confirming requires the archive and the password to be sent again, and the system keeps no decrypted content between preview and confirm

#### Scenario: Archive whose lab store is still locked by the get-based passphrase
- **WHEN** the decrypted lab-store value is in the `v1:` encrypted form (still locked with the get-based app passphrase)
- **THEN** the archive is rejected with a plain message that the lab data is still locked with the get-based passphrase, and nothing is stored

#### Scenario: Unknown archive format version rejected
- **WHEN** an archive has a format or version the importer does not support
- **THEN** it is rejected with a plain-language message naming the version found and the versions supported, and nothing is stored
