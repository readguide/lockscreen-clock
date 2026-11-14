# Lockscreen Clock

Live: https://readguide.github.io/lockscreen-clock/

A centered 24-hour local HH:mm clock, with four remembered appearances:
- Classic white: clean opaque white on pure black (#000).
- Clear white: neutral white-bodied glass with restrained optical bevel.
- Soft frost: brighter milky white body and subtle achromatic grain.
- Fine white edge (stored key `prism` retained for preference compatibility): narrow neutral edge lighting, zero RGB dispersion.

All four backgrounds are exactly #000. A uniform black field contains no detail to visibly refract: these finishes honestly emphasize white readability, upstream Fresnel/specular edges and soft frost instead of fabricating a colored environment.

Click the time or press F for real browser fullscreen; the appearance controls return on exit. In glass modes, only changed digits fade out in place (340ms), switch at zero opacity, then fade in (340ms); unchanged digits and the colon remain fixed. Classic white retains its DOM crossfade. Reduced motion updates immediately. Rendering is event-driven, with a bounded requestAnimationFrame loop only during digit fades; static clocks stop drawing. Style/size changes, rapid updates, hidden pages and reduced-motion changes settle to the newest time. WebGL2 failure or context loss retains readable CSS white glass.

On iPhone Safari, use Share → Add to Home Screen for standalone display; a website cannot force native Safari chrome to disappear. Standalone hides controls. No claim of Apple-native rendering: this is an independent browser implementation. Rounded system fonts are used where available; Barlow Condensed (SIL OFL) is bundled as a licensed resource.

## Sources and licenses

Optical shader adapted from [Oliver Nemo's webgl-apple-liquid-glass](https://github.com/Oliverrr2424/webgl-apple-liquid-glass), revision e8030bd, MIT. Full upstream notice: `vendor/LICENSE-Oliver-Nemo.txt`. Clock adaptation adds supersampled glyph Euclidean SDF geometry, smooth normals, white-readable material variants and event-only rendering. Font license: `assets/OFL.txt`.

## Run and verify

Serve over HTTP (`python3 -m http.server 8794`); ES modules require HTTP, not file://. No runtime dependencies or build step. `verify.py` exercises real installed Google Chrome via an existing Playwright environment. Screenshots and verification results are in `qa/`. GitHub Actions packages all required modules, shaders, font and licenses for Pages.

Limitations: WebGL2 device/driver rendering varies; fallback prioritizes readability over optical equivalence. Fullscreen support is browser-dependent. This is a web clock, not an OS lock screen, and does not lock the device or guarantee the display stays awake.

Digit-transition acceptance: `/tmp/clock-qa-venv/bin/python transition_test.py` is the original pixel regression; `transition_qa.py` covers four viewport sizes, rollovers, interruption, hidden/idle zero drawing, reduced motion and fullscreen; `transition_timer_test.py` drives the real minute timer with Chrome's virtual clock. `transition_preview.py` records actual compositor frames and uses the existing system ffmpeg. Evidence and a short 10:38 → 10:39 MP4 are under `qa/digit-transition/`. Upstream supplies the optical material, not a ready-made clock-digit transition; the per-cell sequential fade is this project's addition.
