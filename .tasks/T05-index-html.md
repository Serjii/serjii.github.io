# T05 — `index.html` — Page Structure

> **Status:** ✅ Done
> **Est. time:** 30 min
> **Depends on:** —

## Goal

Semantic HTML5 page matching the wireframe with proper accessibility.

## Structure (in order)

1. **`<header class="site">`** — Top navigation
   - Brand: avatar image + "Serhii" + "Apify Developer" subtitle
   - Nav links: GitHub, Apify Profile, Email

2. **`<main>`**
   - **Hero section** (`<section class="hero">`)
     - `<h1>` — Gradient text "My Apify Actors"
     - `<p class="lede">` — Description linking to Apify profile
     - `<div class="stats" id="stats">` — Three stat cards (populated by JS)
     - `<div class="ctas">` — Two buttons: "Browse on Apify" (primary gradient), "Commission an actor" (secondary outlined)
   - **Filter bar** (`<section class="filters">`)
     - Search input with icon, clear button, keyboard hint `/`
     - Category chips container (rendered dynamically by JS)
     - Sort dropdown: Newest / Oldest / Recently updated / A→Z
   - **Card grid** (`<div class="grid-wrap">`)
     - `<div class="grid" id="grid" aria-live="polite" role="list">` — populated by JS
     - `<p class="empty" id="empty" hidden>` — "No actors match your search."
3. **`<footer class="site">`**
   - CTA: "Need a custom actor?" + email link
   - Social links row (GitHub, Apify, Email)

4. **Hidden `<svg>` sprite sheet** — inline SVG defs for icons (link arrow, search, mail, close, GitHub, Apify)

## Accessibility

- Semantic HTML (`<header>`, `<main>`, `<footer>`, `<nav>`, `<section>`)
- `aria-label` on nav, filter bar, category chips, social links
- `aria-live="polite"` on grid for screen readers
- `role="list"` on grid, `role="listitem"` on cards
- `sr-only` class for hidden labels
- `:focus-visible` styles for keyboard navigation

## SEO Meta Tags

- `<meta charset="UTF-8">`
- `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
- `<title>Serhii — Apify Actor Portfolio</title>`
- `<meta name="description">`
- `<link rel="icon" href="/favicon.svg" type="image/svg+xml">`
- `<link rel="apple-touch-icon" href="/assets/og-image.png">`
- Google Fonts: Outfit (variable weight)

## Deliverable

`index.html` with proper structure, accessible markup, linked to CSS/JS.

## Notes

- All SEO meta tags, favicon, and apple-touch-icon are in place.
- The sprite sheet includes all icons used across the site.
- Data attributes (`data-cat`, `data-active`, `aria-pressed`) on chips for JS consumption.
