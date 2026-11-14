# Chrome rounded numeral regression

## Diagnosis

On the user's Chrome/macOS, CDP `CSS.getPlatformFontsForNode` reports the original clock's actual digits as `.SF NS`, PostScript `.SFNS-Regular_wdth_opsz600000_GRAD_wght2580000`, not rounded SF. `ui-rounded` being accepted as a CSS string does not establish that it renders rounded glyphs.

System SFNSRounded.ttf exists, with name-table family `.SF NS Rounded` and PostScript `.SFNSRounded-Regular`. Chrome FontFace local() rejected both names and other SF Rounded aliases (NetworkError); no Apple font was copied. Arial Rounded MT Bold is accessible, but its bold-only, heavier geometry is less close to the approved slender Safari figures. The fallback is original Nunito variable, weight 600, OFL; rounded real contours, no blur or synthetic rounding. Its footed 1 is not an exact SF replica.

Nunito source: https://github.com/google/fonts/tree/main/ofl/nunito
Full original font and OFL are under assets/. No installed package, copied system font, CDN runtime request, or font subsetting is required.

## Scope

Only desktop Chrome is considered (Chrome/ token; iOS CriOS/Safari and Edge excluded). Raster comparison of the original family stack with/without `ui-rounded` gates the override: if rounded has distinct rendering, leave it alone. On the observed Chrome the rasters match, proving fallback. FontFace is loaded before measuring cells; failures retain the original stack. All original CSS, fixed ink-centered cells, material/shader parameters and animation timings are unchanged. `digit-glass.js` is byte-identical to 726c9b1.

## Verification

- RED: headed real Google Chrome CDP assertion failed with original `.SF NS` digits.
- GREEN: `rounded_font_qa.py` passes 32 combinations: 390x844, 844x390, 1440x900, 1920x1080 × hm/hms × classic/glass/frost/prism. Numerals now report custom `Nunito-SemiBold`. Clock bounds are centered/in viewport; GL error 0; no page or console errors; minute+second updates exercised.
- Screenshots visually inspected: rounded 1/2/5 terminals, white on black, no clipping. `contact.png` shows all 8 size/format combinations; `1440-hms-glass.png` shows real rounded contours under unchanged glass.
- Safari exclusion: actual Safari WebDriver attempted, but blocked because Allow Remote Automation is disabled. Playwright WebKit is not installed; none was installed. **No real Safari rendering claim.** Chrome with Safari UA exercised the exact exclusion path against original 726c9b1: computed typography, complete clock DOM/geometry and loaded font set identical in all four materials. Glass/frost/prism screenshots pixel-identical; classic differed by at most one edge AA pixel. This is a branch/DOM regression check, not Safari-engine testing.
- Deployment regression found and fixed: the Pages workflow's explicit copy allowlist initially omitted `chrome-rounded.js`, so a static import prevented *all* initialization. Added it to the artifact, then isolated the optional import behind the Chrome branch with catch. A failing-then-passing regression aborts `chrome-rounded.js` and verifies Safari-UA clock startup still succeeds; Safari now requests neither module nor font. This initial production interruption is not a Safari font or shader issue.
- Existing unrelated dirty files were not staged or changed.

Run local server on 8917 and `/tmp/clock-qa-venv/bin/python rounded_font_qa.py http://127.0.0.1:8917/`. All full screenshots go to `/tmp/clock-rounded-qa/`.
