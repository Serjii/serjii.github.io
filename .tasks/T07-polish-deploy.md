# T07 — Polish & Deployment

> **Status:** 🟡 Partial (frontend done; CI pipeline and live deploy pending)
> **Est. time:** 30 min
> **Depends on:** T03, T06

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
- [ ] Set up CI workflow (T03) to auto-update `actors.json` on push
- [ ] Verify `actors.json` updates on push (CI pipeline works)

## Deliverable

Live site at `https://serjii.github.io` with working data pipeline.

## Remaining Work

1. **CI Workflow (T03)** — Create `.github/workflows/fetch-actors.yml` that runs `fetch-actors.py` on push to `main`.
2. **Mobile Testing** — Test on actual devices or Chrome DevTools device emulation.
3. **Accessibility Audit** — Verify focus styles, contrast ratios, keyboard navigation work correctly.
4. **Deploy** — Push to GitHub, ensure GitHub Pages is enabled, verify live site.
5. **CI Verification** — Push a commit, confirm `actors.json` updates automatically.

## Notes

- All frontend code (HTML, CSS, JS) is complete and functional.
- The main remaining blocker is the CI workflow (T03) — once that's set up, deploy verification is straightforward.
- `actors.json` is currently manually generated. CI will make it automatic.
