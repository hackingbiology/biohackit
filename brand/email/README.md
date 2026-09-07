# BIOHACK.IT — HTML email signature (bilingual EN/中文)

`signature.html` — table-based, inline CSS, works in Thunderbird, Apple Mail, Gmail, Outlook.
The logo is loaded from **https://biohack.it/brand/sig-logo.png** so recipients always see it
(no attachment, no data-URI that some clients block). Edit the name/title/contact fields per person.

## Thunderbird
1. Menu → **Account Settings** → pick your identity.
2. Tick **"Use HTML"**.
3. Tick **"Attach the signature from a file instead"** → **Choose** → select `signature.html`.
   (Or paste the HTML directly into the signature box with HTML enabled.)

## Apple Mail
Easiest: open `signature.html` in **Safari**, press **⌘A** then **⌘C** (select all, copy),
then Mail → **Settings → Signatures**, create a signature and **⌘V** into the right pane.
If the logo/formatting drops, use the file method:
1. Mail → Settings → Signatures → create a new signature (type one character), quit Mail.
2. Open `~/Library/Mail/V*/MailData/Signatures/` → find the newest `*.mailsignature` file.
3. Replace everything **after** the header block (the lines with `Content-...` and the blank line)
   with the contents of `signature.html`. Save.
4. Reopen Mail. (Lock the file if Mail overwrites it: `chflags uchg <file>.mailsignature`.)

## Notes
- Fonts fall back to Helvetica/Arial in mail clients (Jost lives in the logo image).
- Colours: charcoal `#25292C`, teal `#0C877A`. Keep the logo width ~230px.
