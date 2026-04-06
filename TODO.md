- [ ] Add fallback JPEG
- [ ] Make it less hardcoded


- [ ]   Option 1 — Fully automatic
  A script analyzes each page (white pixel ratio, entropy, color variance) and assigns settings. Simple to build, zero manual work. Main risk: misclassification is silent — you
  won't know a page was compressed wrong until you notice quality loss. Works best when content types are clearly distinct.

  Option 2 — Manual web UI
  A local HTML tool showing page thumbnails with dropdowns per page. You set everything explicitly. Full control, but tedious for 67 pages — you'd end up leaving most at the
  default anyway.

  Option 3 — Hybrid
  Auto-detection runs first and writes a page_settings.json. The web UI loads that JSON, shows each page's thumbnail with its detected setting pre-filled, and lets you override
  any page before running the conversion. You only touch the pages the auto-detection got wrong.

  ---
  My take: Option 3 is the right approach for this use case. The auto-detection handles the 90% case, and the UI exists specifically for the edge cases — architectural renders
  that look like photos, or cover pages that need special treatment.

  The implementation naturally splits into three pieces:
  1. analyze_pdfs.py — writes page_settings.json with a class + suggested settings per page
  2. editor.html — local web UI, reads thumbnails from images/, reads/writes page_settings.json
  3. convert_pdfs.py — reads page_settings.json instead of global DPI/AVIF_QUALITY constants

  The editor runs locally only (not deployed), so it can use fetch() to read the manifest but would need a small local server with write access to save the JSON back. A tiny
  Python server (editor_server.py) alongside the HTML would handle that.