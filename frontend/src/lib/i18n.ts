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

export function pickLocale(lang: string | undefined): Locale {
  const l = (lang ?? "en").toLowerCase();
  if (l.startsWith("it")) return "it";
  if (l.startsWith("zh")) return "zh";
  return "en";
}
