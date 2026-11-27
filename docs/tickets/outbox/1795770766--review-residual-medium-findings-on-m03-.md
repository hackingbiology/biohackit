# [review] Residual medium findings on m03-openspec-change-interventions-protocols

Labels: autodev

[
 {
  "file": "docs/QUESTIONS.md",
  "line": 308,
  "severity": "medium",
  "claim": "Q109 default says 'immutable once superseded', which disagrees with the delta and D4: every created version, including the latest, is immutable.",
  "fix": "Reword the Q109 default to 'every created version is immutable, including the latest; a Draft is edited in place and has no version'.",
  "confirmed": true,
  "reason": "Line 308 reads 'immutable once superseded'. The delta (protocols/spec.md:4) says every created version is unchanged, including the latest one, and a correction creates a new version. A reader following Q109 could allow edits to the latest version in place."
 },
 {
  "file": "openspec/changes/m03-interventions-protocols/specs/protocols/spec.md",
  "line": 4,
  "severity": "medium",
  "claim": "The ADDED Draft exemption (no version, edited in place) conflicts with the main-spec 'Versioning and change tracking', which is not MODIFIED. That requirement says every facet change is a versioned event with a mandatory reason and has no Draft exception.",
  "fix": "Add a MODIFIED 'Versioning and change tracking' that restates the full requirement and its scenarios and states the Draft exception. State how measurements taken during Draft are handled. Keep only immutability as ADDED.",
  "confirmed": true,
  "reason": "Main spec lines 51-57 say every facet change is versioned with a mandatory reason and give no Draft exception. The delta line 4 and its scenario say Draft edits create no version. The delta has no MODIFIED block, so the merged spec would hold two conflicting SHALLs. The delta also doesn't say what a measurement taken during Draft binds to."
 },
 {
  "file": "openspec/changes/m03-interventions-protocols/specs/protocols/spec.md",
  "line": 4,
  "severity": "medium",
  "claim": "Duplicate of the previous finding: the Draft exemption in an ADDED requirement contradicts the unmodified main-spec versioning requirement.",
  "fix": "Same as the previous finding: move the Draft exemption into a MODIFIED 'Versioning and change tracking' block.",
  "confirmed": true,
  "reason": "Same defect as the previous finding. It is real, but it is a duplicate, so treat the two as one fix."
 }
]
