# Verification

Executed using installed Google Chrome through `/tmp/clock-qa-venv/bin/python`, no dependencies installed.

- 1440×900, 1920×1080, 390×844, 844×390: all four styles rendered, clock box centered to <1 CSS px, no clipping.
- Every style: 1.2 second idle observation yielded zero additional WebGL draws; minute-change QA kept identical bounds and used in-place transition.
- Every viewport: style persistence after reload; real Fullscreen API entered; controls hidden inside and restored after exit; no console/page errors; gl.getError() == 0.
- Timer-driven midnight rollover tested with browser clock: 23:59 → 00:00.
- Forced WebGL2 unavailable: readable CSS glass verified as rgb(237,244,247), screenshot saved.
- Screenshots: `qa/{desktop,wide,mobile,landscape}-{classic,glass,frost,prism}.png`; fallback `qa/css-fallback.png`.
- Visual self-review: all four desktop variants viewed; final clear/prism and mobile frost re-viewed after strengthening optical differences. White bodies are legible, no dark-outline-only digits; restrained teal/slate/amber environment has fine curves, no broad white diagonal stripe.
- Design audit: 0/10 applicable slop tells. Centered large numeric monitor is the actual product, not a marketing hero or decorative statistic; optical glass is requested functional content, not an unearned panel treatment.

Limitations: Chrome headless is the real installed Chrome binary, not physical iOS hardware. Standalone media emulation did not activate in this environment, so installed-PWA standalone was not runtime verified (CSS rule and existing manifest retained). Fullscreen was runtime verified. Device GPU/font differences may affect appearance. Optical differences are intentionally subtle on small screens to retain white readability. Continuous long-duration battery profiling was not performed; idle draw counter was measured. Pages resource byte verification is performed separately after deployment.
