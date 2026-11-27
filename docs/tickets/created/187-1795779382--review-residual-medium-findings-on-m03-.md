# [review] Residual medium findings on m03-tgf1-protocol-and-version-models

Labels: autodev

[
 {
  "file": "backend/protocols/facets.py",
  "line": 39,
  "severity": "medium",
  "claim": "The amount check uses Python's lenient Decimal() parser and stores the raw text, so non-standard forms such as '1_0', non-ASCII digits and '6E-1' are accepted and kept as typed.",
  "fix": "Before the Decimal parse, require plain ASCII decimal syntax, e.g. re.fullmatch(r'[0-9]+(\\.[0-9]+)?', text, re.ASCII). Cap the length. Add tests for '1_0', '\u0666' and '6E-1'.",
  "confirmed": true,
  "reason": "Read facets.py:32-44. `_amount` strips the text, calls `Decimal(text)`, checks only finiteness and sign, and returns the raw `text`. It has no regex and no length cap, because `MAX_TEXT` is applied only in `_text`. Python's Decimal accepts underscores, Unicode digits and exponent notation. The docstring says amounts are exact decimal strings and AMOUNT_HINT says 'such as \"6\" or \"0.5\"', so the stored value can disagree with what downstream readers parse. I did not run the code. The Decimal behaviour is documented, and the code shows no guard."
 }
]
