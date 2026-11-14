# Lockscreen Clock

Live: https://readguide.github.io/lockscreen-clock/

A single-screen local-time 24-hour HH:mm clock on a dark background. Visible numerals are centered in both axes and occupy approximately 92% of the viewport width (height-limited on extreme aspect ratios). Only changed digits slide vertically at minute boundaries; the colon stays still. Initial load, tab restoration and reduced-motion mode update immediately.

Click the time or press F to toggle the browser Fullscreen API where supported. Ordinary iPhone Safari cannot be forced to hide its browser chrome by a web page; use Share → Add to Home Screen and open the installed standalone app instead. There are no on-screen buttons.

Native rounded fonts are used when available. The bundled Barlow Condensed fallback is licensed under SIL OFL; see assets/OFL.txt. No tracking or external runtime dependencies.

Open index.html directly or run `python3 -m http.server 8765`. GitHub Actions deploys the HTML, standalone manifest and licensed font assets on pushes to main.
