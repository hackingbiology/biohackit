# [review] Residual medium findings on x01-tg5-ecosystem-docs-page

Labels: autodev

[
 {
  "file": "frontend/src/app/ecosystem/page.tsx",
  "line": 27,
  "severity": "medium",
  "claim": "The page picks it/zh from Accept-Language, but `<html lang>` stays \"en\" and `<main>` has no lang attribute. This fails WCAG 3.1.1/3.1.2.",
  "fix": "Have requestLocale's result set `lang={locale}` on `<main>`, or set `<html lang>` in layout.tsx from the same call. Add a test assertion on the lang attribute.",
  "confirmed": true,
  "reason": "layout.tsx:28 hard-codes `<html lang=\"en\">`. page.tsx:25-27 renders the localized strings in `<main>` with no lang attribute. The only other `lang=` uses are the sign-in and sign-up pages, which pass `lang` to a form component."
 }
]
