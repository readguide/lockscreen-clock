# Liquid-white finishes and visual-switch investigation

## Delivered scope

Only the third (`frost`, 柔雾白) and fourth (`prism`, 细亮边) optical materials change. The HTML/CSS layout, typography, cell spacing, positions, classic finish, second finish and SDF geometry are untouched.

The old frost preset applied a constant ~90% white body tint **after** the Fresnel/specular calculation, erasing almost all rim depth. Its photographed inner-rim P05/P95 were 243/245 (standard deviation 0.61). The fourth preset also buried most optical shading (210/219, std 3.12).

The new materials use the existing Oliver Nemo MIT circular meniscus, normals, Snell displacement, Schlick Fresnel and two specular lobes. Body tint now follows the rounded thickness profile; reflected light survives above it. Third is softer/broader, fourth is clearer with a fine directional glint, both retain a legible neutral-white body. Dispersion remains zero. Black surroundings remain black; a uniform black scene has no visible background detail to refract, and no wallpaper is invented.

`material_regression.py before` failed on the actual old photographed frost rim; after passes:

| Material | Old rim P05–P95 / std | New rim P05–P95 / std |
| --- | --- | --- |
| Second, unchanged | 173–210 / 12.44 | 173–210 / 12.44 |
| Third | 243–245 / 0.61 | 189–214 / 7.89 |
| Fourth | 210–219 / 3.12 | 174–200 / 8.37 |

Second-finish before/after PNG SHA-256 is identical: `0700e8507c20d73868ba2eed10e2f39a9ece08b8320e6bbd36186cbe66a26703`.

## Enlargement report: NOT reproduced, NOT claimed fixed

Production baseline `df01c4b` index and renderer were fetched and matched local SHA-256 before edits. No style-switch scale/transform transition exists in its CSS; viewport CSS size is explicitly fixed, backing size is DPR-capped, and shader coordinates use CSS pixels. There was no evidence justifying a speculative geometry or canvas-handoff rewrite.

`visual_switch.py` records real Chrome compositor screenshots with a tiny unrelated opacity marker to prevent unchanged frames being omitted. It tests all 12 directed pairs at 1440×900/DPR1, 1920×1080/DPR2, 390×844/DPR3, and 844×390/DPR3, with 6× CPU throttling. The marker and controls are excluded from photographic ink analysis. Both union and individual glyph pixel bounding boxes are checked, rather than only DOM rectangles. GL viewport, drawing buffer, backing dimensions, CSS dimensions and uRes are checked; console/page errors fail the test. `--old` serves the committed baseline JS/shader bytes without changing working files; `--headed` uses visible installed Chrome.

Preserved frame folders and `visual-summary.json` contain the measured results. Baseline headed capture recorded 2,914 screenshots, no enlarged frame; maximum per-glyph difference was 2 CSS pixels across different optical finishes, maximum inter-capture gap 33.11 ms. Thus this work does **not** establish a root cause or a fix for the user's reported enlargement.

Existing `regression.py` and `verify.py` also passed across all four sizes: black neutral background, centered fixed cells, no extra idle draws, no console errors, minute/midnight changes, resize, full-screen controls hidden, persistence, and CSS fallback. New screenshot files include material before/after images and contact sheets for classic→glass, glass→third, third→fourth and fourth→classic.

## Reproduce

Use existing `/tmp/clock-qa-venv/bin/python`; no dependencies were installed. The existing local HTTP server serves this repository at `http://127.0.0.1:8794/`.

```
/tmp/clock-qa-venv/bin/python material_regression.py after
/tmp/clock-qa-venv/bin/python regression.py
/tmp/clock-qa-venv/bin/python verify.py
/tmp/clock-qa-venv/bin/python visual_switch.py before-headed --headed --old
/tmp/clock-qa-venv/bin/python visual_switch.py after-headed --headed
/tmp/clock-qa-venv/bin/python summarize_visual.py
```

Set `CLOCK_URL` to the deployed URL to run the visual test there. Physical iOS/Android devices and the reporting user's browser/cache/GPU were not available. A user recording plus browser/device/version remains necessary if the enlargement persists; do not describe these passing baseline captures as proof of a fix.
