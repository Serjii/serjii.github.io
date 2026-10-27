# T06 — `app.js` — Client-Side Rendering & Interactivity

> **Status:** ✅ Done
> **Est. time:** 1h
> **Depends on:** T02, T04, T05

## Goal

Fetch `actors.json`, render cards, implement search/filter/sort with keyboard shortcuts.

## Requirements

### 1. Data Loading
- [x] `fetch('actors.json')` on DOM ready
- [x] Parse JSON, store in module-scoped `actors` array
- [x] Update hero stats with computed values (total, public, categories)
- [x] Render category chips dynamically from unique categories

### 2. Card Rendering
- [x] For each actor: `<article class="card">` with:
  - Icon: `<img>` if `iconUrl` exists, else fallback letter initial
  - Title: `<h2>`
  - Description: `<p class="summary">` (clamped to 3 lines)
  - Category badge (pill)
  - Stats row (runs, users)
  - CTA: `<a>` to `link` with "View on Apify" + arrow icon
  - Status indicator: Public (green dot) / Private (grey dot)
- [x] Escape all user-controlled strings (XSS prevention)
- [x] Lazy-load actor icons (`loading="lazy"`)
- [x] Image error fallback to letter initial

### 3. Search
- [x] Debounced input (300ms) on `input` event
- [x] Filters by title, description, category (case-insensitive substring match)
- [x] Clear button appears when search has text
- [x] `/` key focuses search (when not typing in another input)
- [x] `Escape` clears search

### 4. Category Filter
- [x] Click chip → toggle active state (single-select)
- [x] `activeCategory === 'all'` shows everything
- [x] Update chip count badges after filter applied

### 5. Sort
- [x] `<select>` dropdown with 4 options
- [x] Re-sorts filtered array and re-renders grid

### 6. Performance
- [x] Debounce search input (300ms)
- [x] Re-render only when data, query, or category changes
- [x] Use `DocumentFragment` for batch DOM insertion

### 7. Error Handling
- [x] If `actors.json` fails to load: show inline error message in grid area

## Deliverable

`app.js` fully functional with search, filter, sort, and responsive rendering.

## Notes

- XSS prevention via `esc()` function that escapes `& < > " ' /`.
- State is module-scoped (no closures): `actors`, `activeCategory`, `searchQuery`, `sortValue`.
- DOM refs cached once in `init()`.
- Cards get `fadeInUp` animation via CSS (staggered delays).
