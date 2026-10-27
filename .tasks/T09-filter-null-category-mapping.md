# T09 — Fix "Other" category filter returning empty results

> **Status:** ❌ Pending
> **Priority:** High (UI bug)
> **Est. time:** 5 min
> **Depends on:** none

## Description

Clicking the "Other" filter chip shows zero cards even though the chip badge
correctly shows 9 actors. This is because two functions disagree on how to
treat `category: null` values.

## Root Cause

- `getCategories()` (app.js:124) maps `null` → `'Other'` for chip counts.
- `getFilteredActors()` (app.js:101) compares `a.category === activeCategory`
  directly — actors have `null`, not `'Other'`, so the filter matches nothing.

## Fix

Apply the same `|| 'Other'` fallback in `getFilteredActors()`:

```js
// Before (broken):
if (activeCategory !== 'all') {
  filtered = filtered.filter((a) => a.category === activeCategory);
}

// After (fixed):
if (activeCategory !== 'all') {
  filtered = filtered.filter(
    (a) => (a.category || 'Other') === activeCategory
  );
}
```

## Checklist

- [ ] Apply the fix in `app.js` `getFilteredActors()` (line 101)
- [ ] Verify "Other" chip shows 9 actors after fix
- [ ] Verify existing category filters (AUTOMATION, MCP_SERVERS) still work
- [ ] Verify "All" chip still shows all actors
