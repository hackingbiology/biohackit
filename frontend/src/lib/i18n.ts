// SPDX-License-Identifier: AGPL-3.0-or-later
// biohack.it — open-source biohacking platform
// Copyright (C) HackingBiology 2026 — https://biohack.it
// Full license text: https://www.gnu.org/licenses/agpl-3.0.html

export type Locale = "en" | "it" | "zh";

export interface SignInStrings {
  title: string;
  intro: string;
  continueWith: string;
  passkey: string;
  or: string;
  email: string;
  sendCode: string;
  sending: string;
  codeSent: string;
  code: string;
  confirm: string;
  error: string;
  codeError: string;
  passkeyError: string;
}

export const signInStrings: Record<Locale, SignInStrings> = {
  en: {
    title: "Sign in or create your account",
    intro: "One step: use an account you already have, or get a code by email.",
    continueWith: "Continue with",
    passkey: "Use a passkey",
    or: "or",
    email: "Email",
    sendCode: "Email me a code",
    sending: "Sending…",
    codeSent: "We sent a code to your email. Enter it below.",
    code: "Code",
    confirm: "Confirm",
    error: "Something went wrong. Please try again.",
    codeError: "That code did not work. Check it and try again.",
    passkeyError: "Passkey sign-in did not complete.",
  },
  it: {
    title: "Accedi o crea il tuo account",
    intro:
      "Un solo passaggio: usa un account che hai già, oppure ricevi un codice via email.",
    continueWith: "Continua con",
    passkey: "Usa una passkey",
    or: "oppure",
    email: "Email",
    sendCode: "Inviami un codice",
    sending: "Invio…",
    codeSent: "Ti abbiamo inviato un codice via email. Inseriscilo qui sotto.",
    code: "Codice",
    confirm: "Conferma",
    error: "Qualcosa è andato storto. Riprova.",
    codeError: "Codice non valido. Controllalo e riprova.",
    passkeyError: "Accesso con passkey non completato.",
  },
  zh: {
    title: "登录或创建账户",
    intro: "只需一步：使用已有账户，或通过邮箱获取验证码。",
    continueWith: "使用以下方式继续",
    passkey: "使用通行密钥",
    or: "或",
    email: "邮箱",
    sendCode: "发送验证码",
    sending: "发送中…",
    codeSent: "验证码已发送至您的邮箱，请在下方输入。",
    code: "验证码",
    confirm: "确认",
    error: "出错了，请重试。",
    codeError: "验证码无效，请检查后重试。",
    passkeyError: "通行密钥登录未完成。",
  },
};

export interface EcosystemStrings {
  title: string;
  intro: string;
  scanHeading: string;
  name: string;
  licence: string;
  agpl: string;
  decision: string;
  verified: string;
  provisional: string;
  licenceNote: string;
  giveBackHeading: string;
  giveBackIntro: string;
  approval: string;
  upstream: string;
  contribution: string;
  status: string;
  date: string;
  tableRegion: string;
  link: string;
  back: string;
}

export const ecosystemStrings: Record<Locale, EcosystemStrings> = {
  en: {
    title: "Ecosystem",
    intro:
      "biohack.it reuses open-source projects, standards and datasets instead of rebuilding them. This page lists what we looked at, the licence, and what we decided. Where a fact could not be checked, it says unknown.",
    scanHeading: "What we build on",
    name: "Project",
    licence: "Licence",
    agpl: "AGPL-compatible",
    decision: "Decision",
    verified: "Verified",
    provisional: "Provisional",
    licenceNote: "Licence note",
    giveBackHeading: "What we give back",
    giveBackIntro:
      "Ideas for helping the projects we use. They are only proposals.",
    approval: "Nothing is posted upstream without the owner's approval.",
    upstream: "Upstream project",
    contribution: "Proposed contribution",
    status: "Status",
    date: "Date",
    tableRegion: "Scrollable table",
    link: "Link",
    back: "Back to home",
  },
  it: {
    title: "Ecosistema",
    intro:
      "biohack.it riusa progetti open source, standard e dataset invece di rifarli da zero. Questa pagina elenca cosa abbiamo valutato, la licenza e la decisione presa. Dove un dato non è stato verificato, c'è scritto unknown.",
    scanHeading: "Su cosa costruiamo",
    name: "Progetto",
    licence: "Licenza",
    agpl: "Compatibile con AGPL",
    decision: "Decisione",
    verified: "Verificato",
    provisional: "Provvisorio",
    licenceNote: "Nota sulla licenza",
    giveBackHeading: "Cosa restituiamo",
    giveBackIntro:
      "Idee per aiutare i progetti che usiamo. Sono solo proposte.",
    approval:
      "Nulla viene pubblicato presso i progetti originali senza l'approvazione del titolare.",
    upstream: "Progetto originale",
    contribution: "Contributo proposto",
    status: "Stato",
    date: "Data",
    tableRegion: "Tabella scorrevole",
    link: "Link",
    back: "Torna alla home",
  },
  zh: {
    title: "生态系统",
    intro:
      "biohack.it 复用开源项目、标准和数据集，而不是重新开发。本页列出我们评估过的项目、许可证和决定。无法核实的信息标为 unknown。",
    scanHeading: "我们基于什么构建",
    name: "项目",
    licence: "许可证",
    agpl: "与 AGPL 兼容",
    decision: "决定",
    verified: "核实依据",
    provisional: "暂定",
    licenceNote: "许可证说明",
    giveBackHeading: "我们回馈什么",
    giveBackIntro: "帮助我们所用项目的想法，仅为提议。",
    approval: "未经所有者批准，不会向上游发布任何内容。",
    upstream: "上游项目",
    contribution: "拟议贡献",
    status: "状态",
    date: "日期",
    tableRegion: "可滚动表格",
    link: "链接",
    back: "返回首页",
  },
};

export interface AiSurfacesStrings {
  title: string;
  intro: string;
  aiCaption: string;
  deterministicCaption: string;
  surface: string;
  kind: string;
  where: string;
  status: string;
  tableRegion: string;
  docsIndex: string;
  back: string;
  kindLabels: Record<string, string>;
  statusLabels: Record<string, string>;
}

const aiSurfacesEn: AiSurfacesStrings = {
  title: "What is AI, what is not",
  intro:
    "Computed values such as safety thresholds, indexes, percentiles, trends and schedules come from deterministic code that gives the same result for the same input. AI writes explanations and evidence reviews, and reads a lab report only when its format is not yet known, with you confirming the values.",
  aiCaption: "Where AI is used",
  deterministicCaption: "Computed by code, not AI",
  surface: "Surface",
  kind: "AI or deterministic",
  where: "Where in the code or spec",
  status: "Status",
  tableRegion: "Scrollable table",
  docsIndex: "Documentation",
  back: "Back to documentation",
  kindLabels: { AI: "AI", deterministic: "Computed by code (not AI)" },
  statusLabels: { implemented: "Built", specified: "Planned, not built yet" },
};

// IT and ZH fall back to EN until translated, as for other pages.
export const aiSurfacesStrings: Record<Locale, AiSurfacesStrings> = {
  en: aiSurfacesEn,
  it: aiSurfacesEn,
  zh: aiSurfacesEn,
};

export interface ArchitectureStrings {
  title: string;
  intro: string;
  builtCaption: string;
  specifiedCaption: string;
  component: string;
  layer: string;
  path: string;
  purpose: string;
  requirement: string;
  tableRegion: string;
  back: string;
  layerLabels: Record<string, string>;
}

const architectureEn: ArchitectureStrings = {
  title: "Architecture",
  intro:
    "What the platform is made of today, with the file or folder of each part, and what is specified but not built yet. Every built part points to something that exists in the repository.",
  builtCaption: "Built components",
  specifiedCaption: "Specified, not yet built",
  component: "Component",
  layer: "Layer",
  path: "Where in the repository",
  purpose: "Purpose",
  requirement: "Requirement that specifies it",
  tableRegion: "Scrollable table",
  back: "Back to documentation",
  layerLabels: {
    backend: "Backend",
    frontend: "Frontend",
    deployment: "Deployment",
    process: "Development process",
  },
};

// IT and ZH fall back to EN until translated, as for other pages.
export const architectureStrings: Record<Locale, ArchitectureStrings> = {
  en: architectureEn,
  it: architectureEn,
  zh: architectureEn,
};

export interface UserGuideStrings {
  title: string;
  intro: string;
  stepsCaption: string;
  signinCaption: string;
  laterCaption: string;
  laterNote: string;
  step: string;
  action: string;
  route: string;
  method: string;
  availability: string;
  source: string;
  feature: string;
  requirement: string;
  tableRegion: string;
  back: string;
}

const userGuideEn: UserGuideStrings = {
  title: "User guide",
  intro:
    "How to use biohack.it today. This guide describes only what is built. Features that are planned come last, in their own list.",
  stepsCaption: "Steps you can take today",
  signinCaption: "Ways to sign in",
  laterCaption: "Coming later",
  laterNote: "These features are specified but not built. Do not look for them yet.",
  step: "Step",
  action: "What you do",
  route: "Page in the code",
  method: "Method",
  availability: "When it is available",
  source: "Where in the code",
  feature: "Feature",
  requirement: "Requirement that specifies it",
  tableRegion: "Scrollable table",
  back: "Back to documentation",
};

// IT and ZH fall back to EN until translated, as for other pages.
export const userGuideStrings: Record<Locale, UserGuideStrings> = {
  en: userGuideEn,
  it: userGuideEn,
  zh: userGuideEn,
};

export interface ChangelogStrings {
  title: string;
  intro: string;
  caption: string;
  summary: string;
  change: string;
  commit: string;
  tableRegion: string;
  back: string;
}

const changelogEn: ChangelogStrings = {
  title: "Changelog",
  intro:
    "What changed on biohack.it, newest day first. Each line names the project change it belongs to and the commit that delivered it.",
  caption: "Changes made on",
  summary: "What changed",
  change: "Project change",
  commit: "Commit",
  tableRegion: "Scrollable table",
  back: "Back to documentation",
};

// IT and ZH fall back to EN until translated, as for the user guide.
export const changelogStrings: Record<Locale, ChangelogStrings> = {
  en: changelogEn,
  it: changelogEn,
  zh: changelogEn,
};

export interface LabImportStrings {
  title: string;
  intro: string;
  headerHelp: string;
  fileLabel: string;
  check: string;
  checking: string;
  tableCaption: string;
  colRow: string;
  colLoinc: string;
  colValue: string;
  colUnit: string;
  colStatus: string;
  colReason: string;
  colRange: string;
  rangeWithin: string;
  rangeOutside: string;
  rangeNotChecked: string;
  rangeFlagNote: string;
  rangeSource: string;
  savedLock: string;
  recognised: string;
  notRecognised: string;
  inferred: string;
  summary: string;
  save: string;
  saving: string;
  saveBlocked: string;
  noFile: string;
  savedTitle: string;
  savedBody: string;
  originalKept: string;
  originalNotKept: string;
  undo: string;
  undoConfirm: string;
  undone: string;
  signIn: string;
  signInLink: string;
  genericError: string;
  confirmRefused: string;
  tableRegion: string;
  undoFailed: string;
}

const labImportEn: LabImportStrings = {
  title: "Import lab results (CSV)",
  intro:
    "Choose a CSV file, check it, and save it only when every row is recognised. Nothing is stored until you save, and you can undo a saved import.",
  headerHelp:
    "The first line must be: loinc_code,value,unit. Optional columns after that: collected_at, reported_at, laboratory, method. Times need a UTC offset.",
  fileLabel: "Lab results file (.csv)",
  check: "Check file",
  checking: "Checking…",
  tableCaption: "Rows of your file and whether each one is recognised",
  colRow: "Row",
  colLoinc: "LOINC code",
  colValue: "Value",
  colUnit: "Unit",
  colStatus: "Status",
  colReason: "Reason",
  colRange: "Range check",
  rangeWithin: "Within the cited reference range",
  rangeOutside: "Outside the cited reference range",
  rangeNotChecked: "Not checked",
  rangeFlagNote:
    "The range check is only a flag. It never stops you from saving.",
  rangeSource: "Range source:",
  savedLock:
    "Report number {id} is saved. Undo it before you check another file.",
  recognised: "Recognised",
  notRecognised: "Not recognised",
  inferred: "Inferred",
  summary: "{recognised} of {total} rows recognised",
  save: "Save report",
  saving: "Saving…",
  saveBlocked:
    "Save is not available because at least one row is not recognised. Fix the file and check it again.",
  noFile: "Choose a CSV file first.",
  savedTitle: "Report saved",
  savedBody: "Report number {id} was saved.",
  originalKept: "The original file was kept privately.",
  originalNotKept: "The original file was not kept.",
  undo: "Undo this import",
  undoConfirm: "Undo this import? The report and its results will be deleted.",
  undone: "Import undone. The report was deleted.",
  signIn: "Please sign in to import lab results.",
  signInLink: "Go to sign in",
  genericError: "Something went wrong. Nothing was saved. Try again.",
  confirmRefused:
    "The file was not saved because some rows are not recognised.",
  tableRegion: "Scrollable table",
  undoFailed:
    "The import was not undone. The report is still saved. Try again.",
};

// IT and ZH fall back to EN until translated (Q86).
export const labImportStrings: Record<Locale, LabImportStrings> = {
  en: labImportEn,
  it: labImportEn,
  zh: labImportEn,
};

export interface LabStrings {
  importLink: string;
  newLink: string;
  viewReport: string;
  newTitle: string;
  newIntro: string;
  reportLaboratory: string;
  resultHeading: string;
  addRow: string;
  removeRow: string;
  loincCode: string;
  reportedValue: string;
  reportedUnit: string;
  laboratory: string;
  method: string;
  device: string;
  collectedAt: string;
  reportedAt: string;
  dateHelp: string;
  submit: string;
  submitting: string;
  required: string;
  fixErrors: string;
  signIn: string;
  signInLink: string;
  genericError: string;
  reportTitle: string;
  loading: string;
  notFound: string;
  origin: string;
  originManual: string;
  originCsv: string;
  originRetainedYes: string;
  originRetainedNo: string;
  laboratoryLabel: string;
  colLoinc: string;
  colValue: string;
  colUnit: string;
  colNormalised: string;
  colLaboratory: string;
  colMethod: string;
  colDevice: string;
  colCollected: string;
  colReported: string;
  colState: string;
  colAggregation: string;
  colRange: string;
  tableCaption: string;
  tableRegion: string;
  notGiven: string;
  stateEntered: string;
  stateUserConfirmed: string;
  stateSourceVerified: string;
  stateDisputed: string;
  stateRetracted: string;
  aggregationYes: string;
  aggregationNo: string;
  undo: string;
  undoConfirm: string;
  undone: string;
  undoFailed: string;
  undoManualNote: string;
  undoConflict: string;
  originUnknown: string;
  rowProblem: string;
}

const labEn: LabStrings = {
  importLink: "Import a CSV file instead",
  newLink: "Type a report by hand instead",
  viewReport: "View report",
  newTitle: "Enter lab results by hand",
  newIntro: "Type each result as your lab reported it. Nothing is stored until you save, and you can undo a saved report.",
  reportLaboratory: "Laboratory for the whole report (optional)",
  resultHeading: "Result {n}",
  addRow: "Add another result",
  removeRow: "Remove result {n}",
  loincCode: "LOINC code",
  reportedValue: "Reported value",
  reportedUnit: "Reported unit",
  laboratory: "Laboratory (optional)",
  method: "Method (optional)",
  device: "Device (optional)",
  collectedAt: "Collected at (optional)",
  reportedAt: "Reported at (optional)",
  dateHelp: "Dates are sent with your browser's UTC offset, so the time you type is read as your local time.",
  submit: "Save report",
  submitting: "Saving…",
  required: "This field is required.",
  fixErrors: "The report was not saved. Fix the marked fields and try again.",
  signIn: "Please sign in to save lab results.",
  signInLink: "Go to sign in",
  genericError: "Something went wrong. Nothing was saved. Try again.",
  reportTitle: "Lab report {id}",
  loading: "Loading…",
  notFound: "Report not found",
  origin: "Origin:",
  originManual: "Typed by hand",
  originCsv: "Imported from a CSV file",
  originRetainedYes: "The original file was kept privately.",
  originRetainedNo: "No original file was kept.",
  laboratoryLabel: "Laboratory:",
  colLoinc: "LOINC code",
  colValue: "Reported value",
  colUnit: "Reported unit",
  colNormalised: "Normalised value",
  colLaboratory: "Laboratory",
  colMethod: "Method",
  colDevice: "Device",
  colCollected: "Collected at",
  colReported: "Reported at",
  colState: "Validation state",
  colAggregation: "Used in aggregations",
  colRange: "Range check",
  tableCaption: "Results of this report, as reported",
  tableRegion: "Scrollable table",
  notGiven: "Not given",
  stateEntered: "Entered, not yet confirmed",
  stateUserConfirmed: "Confirmed by the user",
  stateSourceVerified: "Verified against the source",
  stateDisputed: "Disputed",
  stateRetracted: "Retracted",
  aggregationYes: "Yes, counted in aggregations",
  aggregationNo: "No, not counted in aggregations",
  undo: "Undo this report",
  undoConfirm: "Undo this report? The report and its results will be deleted.",
  undone: "Report undone. It was deleted.",
  undoFailed: "The report was not undone. It is still saved. Try again.",
  undoManualNote: "A report you typed by hand cannot be undone.",
  undoConflict: "This report cannot be undone because it was typed by hand. It is still saved.",
  originUnknown: "Unknown origin",
  rowProblem: "Problem with this result:",
};

// IT and ZH fall back to EN until translated (Q86).
export const labStrings: Record<Locale, LabStrings> = {
  en: labEn,
  it: labEn,
  zh: labEn,
};

export function pickLocale(lang: string | undefined): Locale {
  const l = (lang ?? "en").toLowerCase();
  if (l.startsWith("it")) return "it";
  if (l.startsWith("zh")) return "zh";
  return "en";
}
