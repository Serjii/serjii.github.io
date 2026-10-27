# T10 — Fix "No actors match your search" always visible alongside results

> **Status:** ❌ Pending
> **Priority:** High (UI bug)
> **Est. time:** 2 min
> **Depends on:** T06 (`app.js` client-side rendering)

## Description

The empty-state message ("No actors match your search") is always visible in the
card grid, appearing below the actor cards regardless of whether the list is
actually empty. It should only appear when filtering or searching yields zero
results.

## Root Cause

`renderGrid()` in `app.js` uses the HTML `hidden` attribute to toggle the
empty element:

```js
if (filtered.length === 0) {
    elEmpty.hidden = false;  // show empty message
} else {
    elEmpty.hidden = true;   // hide empty message
}
```

The `hidden` attribute relies on the browser's user-agent stylesheet to apply
`display: none`, which can be unreliable — especially when the `.empty` class
explicitly sets `display: flex` in `styles.css`. The attribute gets overridden
or ignored, so the empty message is always visible.

## Fix

Replace `hidden` attribute toggling with explicit `style.display` assignments in
both `renderGrid()` (app.js line 197–204):

```js
// Before (fragile — relies on UA stylesheet for hidden):
if (filtered.length === 0) {
    elGrid.style.display = 'none';
    elEmpty.hidden = false;
    return;
}
elGrid.style.display = '';
elEmpty.hidden = true;

// After (robust — explicit inline styles):
if (filtered.length === 0) {
    elEmpty.style.display = '';
    elGrid.style.display = 'none';
    return;
}
elEmpty.style.display = 'none';
elGrid.style.display = '';
```

## Checklist

- [ ] Replace `elEmpty.hidden = true/false` with `elEmpty.style.display = 'none'/'` in `renderGrid()` (app.js lines 197–204)
- [ ] Verify empty message is hidden when actor list has results
- [ ] Verify empty message appears correctly when filters/search yield zero matches
- [ ] Verify the `/` keyboard shortcut still works after the change
