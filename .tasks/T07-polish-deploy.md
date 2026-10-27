# T07 — Polish & Deployment

> **Status:** 🟡 Partial (frontend done; live deploy pending)
> **Est. time:** 30 min
> **Depends on:** T06

## Goal

Final touches, SEO, and production deployment.

## Checklist

- [x] Add `<meta>` tags for SEO: title, description, og:image, twitter:card
- [x] Add `favicon.svg` to `<head>`
- [x] Add `apple-touch-icon` for iOS
- [ ] Test on mobile (Chrome DevTools, actual device)
- [ ] Verify accessibility: focus styles, contrast ratios, keyboard navigation
- [x] Add `rel="noopener"` to all external links
- [x] Lazy-load actor icons (`loading="lazy"` on `<img>`)
- [ ] Push to GitHub → verify GitHub Pages deploy at `https://serjii.github.io`
- [ ] Update `actors.json` manually (`uv run python fetch-actors.py`) and push
- [ ] Verify `actors.json` updates after manual push

## Deliverable

Live site at `https://serjii.github.io` with working data pipeline.

## Remaining Work

1. **Mobile Testing** — Test on actual devices or Chrome DevTools device emulation.
2. **Accessibility Audit** — Verify focus styles, contrast ratios, keyboard navigation work correctly.
3. **Deploy** — Push to GitHub, ensure GitHub Pages is enabled, verify live site.

## Notes

- All frontend code (HTML, CSS, JS) is complete and functional.
- All frontend code (HTML, CSS, JS) is complete and functional.
- `actors.json` is generated manually via `fetch-actors.py` — no CI pipeline is needed.
