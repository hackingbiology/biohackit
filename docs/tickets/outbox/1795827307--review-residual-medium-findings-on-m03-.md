# [review] Residual medium findings on m03-tgk-publish-visibility-origin-level

Labels: autodev

[
 {
  "file": "backend/protocols/views.py",
  "line": 232,
  "severity": "medium",
  "claim": "The anonymous throttle on /api/public/protocols/ can be bypassed by sending a different spoofed X-Forwarded-For header on each request, because NUM_PROXIES is not set.",
  "fix": "Set REST_FRAMEWORK[\"NUM_PROXIES\"] from an env var (0 with no reverse proxy, otherwise the real proxy count). Add a test that sends 3 requests with different HTTP_X_FORWARDED_FOR values at a 2/min rate and expects a 429 on the third.",
  "confirmed": true,
  "reason": "A grep of backend (excluding .venv) finds no NUM_PROXIES or X_FORWARDED anywhere. PublicProtocolView at views.py:230-233 has authentication_classes = [] and uses ScopedRateThrottle with scope public_protocols, so every caller is anonymous and keyed by get_ident(). From my knowledge of DRF (I did not open the installed source), get_ident() with NUM_PROXIES unset returns the raw X-Forwarded-For string when the header is present, so each new value gets a new bucket. The only throttle test, test_protocol_publication.py:181, sends no XFF header and cannot catch this. Whether it is exploitable depends on the proxy in front, but the repo as it stands does not handle it."
 }
]
