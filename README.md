# Lockscreen Clock

A quiet, single-screen clock inspired by lock-screen typography.

Live: https://readguide.github.io/lockscreen-clock/

Only HH:mm is displayed, using the device's local time zone and a 24-hour clock. Updates are aligned to minute boundaries; returning to the tab immediately resynchronizes the time. Responsive on phones and desktops, with no external dependencies, tracking, or downloaded fonts. SF Pro Rounded is used only when available locally, with system fallbacks.

Open `index.html` directly, or run `python3 -m http.server 8765` and visit http://localhost:8765.

GitHub Actions publishes only `index.html` to GitHub Pages on pushes to `main` or a manual workflow run.
