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

export function pickLocale(lang: string | undefined): Locale {
  const l = (lang ?? "en").toLowerCase();
  if (l.startsWith("it")) return "it";
  if (l.startsWith("zh")) return "zh";
  return "en";
}
