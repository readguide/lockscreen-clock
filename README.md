# Lockscreen Clock

Live: https://readguide.github.io/lockscreen-clock/

A centered 24-hour local HH:mm clock, with four remembered appearances:
- Classic white: clean opaque white on charcoal.
- Clear white: white-bodied glass, narrow refracting bevel and crisp highlights.
- Soft frost: brighter milky body, scattered transmission and subtle grain.
- Cool/warm refraction: deeper optical bevel, dispersion and restrained cool/warm edge reflections.

Click the time or press F for real browser fullscreen; the appearance controls return on exit. Changed digits crossfade in place, never slide or change the clock bounds. Reduced motion updates immediately. Rendering is event-driven: minute changes, size/font changes and appearance changes; no continuous animation loop. WebGL2 failure or context loss retains readable CSS white glass.

On iPhone Safari, use Share → Add to Home Screen for standalone display; a website cannot force native Safari chrome to disappear. Standalone hides controls. No claim of Apple-native rendering: this is an independent browser implementation. Rounded system fonts are used where available; Barlow Condensed (SIL OFL) is bundled as a licensed resource.

## Sources and licenses

Optical shader adapted from [Oliver Nemo's webgl-apple-liquid-glass](https://github.com/Oliverrr2424/webgl-apple-liquid-glass), revision e8030bd, MIT. Full upstream notice: `vendor/LICENSE-Oliver-Nemo.txt`. Clock adaptation adds supersampled glyph Euclidean SDF geometry, smooth normals, white-readable material variants and event-only rendering. Font license: `assets/OFL.txt`.

## Run and verify

Serve over HTTP (`python3 -m http.server 8794`); ES modules require HTTP, not file://. No runtime dependencies or build step. `verify.py` exercises real installed Google Chrome via an existing Playwright environment. Screenshots and verification results are in `qa/`. GitHub Actions packages all required modules, shaders, font and licenses for Pages.

Limitations: WebGL2 device/driver rendering varies; fallback prioritizes readability over optical equivalence. Fullscreen support is browser-dependent. This is a web clock, not an OS lock screen, and does not lock the device or guarantee the display stays awake.
