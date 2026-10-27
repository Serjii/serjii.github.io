# T04 — Design System & `styles.css`

> **Status:** ✅ Done
> **Est. time:** 2h
> **Depends on:** T05

## Goal

A polished, modern dark theme with glassmorphism. Better than the reference site.

## Design Specs

| Element | Decision |
|---------|----------|
| **Font** | `Outfit` (Google Fonts, variable weight 300–800) |
| **Background** | Dark `#0a0a0f` with two large blurred gradient orbs (blue top-left, purple bottom-right) |
| **Header** | Frosted glass (`backdrop-filter: blur(14px)`), flexbox with brand + nav links |
| **Hero** | Centered, gradient text (`#3b82f6 → #8b5cf6 → #ec4899`), large font, lede paragraph, CTA buttons |
| **Stats** | Three big numbers in gradient, centered row |
| **Filter bar** | Sticky top, glass effect, horizontal scroll on mobile |
| **Search input** | Pill-shaped, focus ring with blue glow, `/` keyboard shortcut to focus, `Escape` to clear |
| **Category chips** | Pill buttons, active state = gradient fill + shadow, show count badge |
| **Card grid** | CSS Grid, `minmax(320px, 1fr)`, auto-fill |
| **Cards** | Frosted glass bg, hover: lift (-4px) + glow shadow + gradient border reveal |
| **Footer** | Glass effect, CTA for commissions, social links |
| **Mobile** | Break at 720px: filter bar stacks vertically, grid becomes single column |

## CSS Architecture

- CSS custom properties for all colors, spacing, radii, shadows, transitions
- `@import` for Outfit font via Google Fonts
- Well-commented sections (16 numbered sections)
- No framework, no build step
- Staggered card entrance animation (`fadeInUp` with delays)
- Icon pulse on card hover

## Deliverable

`styles.css` with full design system, works with `index.html`.

## Notes

- All CSS is written and functional. The design system covers every interactive element.
- Responsive breakpoint: 720px.
- Custom properties defined in `:root` for easy theming.
