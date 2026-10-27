/**
 * app.js — Apify Actor Portfolio
 * T06: Client-side rendering & interactivity
 *
 * Responsibilities:
 *   1. Fetch actors.json and store in module-scoped array
 *   2. Update hero stats (total, public, categories)
 *   3. Render category chips dynamically
 *   4. Render cards with search / filter / sort
 *   5. Keyboard shortcuts (/, Esc)
 *   6. Error handling & loading states
 */

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

let actors = [];           // full data array
let activeCategory = 'all'; // current category filter
let searchQuery = '';      // current search text
let sortValue = 'newest';  // current sort order

// DOM references (captured once after DOMContentLoaded)
const $ = (sel) => document.querySelector(sel);
let elStats, elGrid, elEmpty, elSearch, elClear, elChips, elSort;

// ---------------------------------------------------------------------------
// XSS Prevention
// ---------------------------------------------------------------------------

/** Escape HTML special characters in user-controlled strings. */
function esc(str) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
  };
  return String(str).replace(/[&<>"'\/]/g, (ch) => map[ch]);
}

// ---------------------------------------------------------------------------
// Data Loading
// ---------------------------------------------------------------------------

async function loadData() {
  try {
    const resp = await fetch('actors.json');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    actors = Array.isArray(data.actors) ? data.actors : [];
    updateStats();
    renderChips();
    renderGrid();
  } catch (err) {
    console.error('Failed to load actors.json:', err);
    showError(err.message || 'Could not load data.');
  }
}

function showError(message) {
  if (elGrid) {
    elGrid.innerHTML = '';
    const errEl = document.createElement('p');
    errEl.className = 'empty';
    errEl.innerHTML = `<span>⚠️ ${esc(message)}</span>`;
    elGrid.after(errEl);
  }
}

// ---------------------------------------------------------------------------
// Stats (hero section)
// ---------------------------------------------------------------------------

function updateStats() {
  const total = actors.length;
  const publicCount = actors.filter((a) => a.isPublic).length;
  const categories = new Set(actors.map((a) => a.category).filter(Boolean));

  set(elStats, 'stat-total', total);
  set(elStats, 'stat-public', publicCount);
  set(elStats, 'stat-categories', categories.size || 0);
}

function set(el, id, value) {
  const node = el.querySelector(`#${id}`);
  if (node) node.textContent = value;
}

// ---------------------------------------------------------------------------
// Category Chips
// ---------------------------------------------------------------------------

function getFilteredActors() {
  let filtered = actors;

  // Category filter
  if (activeCategory !== 'all') {
    filtered = filtered.filter(
      (a) => (a.category || 'Other') === activeCategory
    );
  }

  // Search filter
  if (searchQuery) {
    const q = searchQuery.toLowerCase();
    filtered = filtered.filter(
      (a) =>
        (a.title && a.title.toLowerCase().includes(q)) ||
        (a.description && a.description.toLowerCase().includes(q)) ||
        (a.category && a.category.toLowerCase().includes(q))
    );
  }

  // Sort
  filtered = applySort(filtered);

  return filtered;
}

function getCategories() {
  const counts = {};
  for (const a of actors) {
    const cat = a.category || 'Other';
    counts[cat] = (counts[cat] || 0) + 1;
  }
  // Sort by count descending
  return Object.entries(counts).sort((a, b) => b[1] - a[1]).map(([name, count]) => ({
    name,
    count,
  }));
}

function renderChips() {
  if (!elChips) return;
  const cats = getCategories();

  // Build "All" chip
  let html = `<button class="chip" data-cat="all" data-active="${activeCategory === 'all'}" aria-pressed="${activeCategory === 'all'}">All<span class="chip__count">${actors.length}</span></button>`;

  for (const { name, count } of cats) {
    const isActive = activeCategory === name;
    html += `<button class="chip" data-cat="${esc(name)}" data-active="${isActive}" aria-pressed="${isActive}">${esc(name)}<span class="chip__count">${count}</span></button>`;
  }

  elChips.innerHTML = html;

  // Bind click events
  elChips.querySelectorAll('.chip').forEach((chip) => {
    chip.addEventListener('click', () => {
      const cat = chip.getAttribute('data-cat');
      activeCategory = (cat === 'all') ? 'all' : cat;
      renderChips(); // re-render to update active state
      renderGrid();  // re-render cards
    });
  });
}

// ---------------------------------------------------------------------------
// Sorting
// ---------------------------------------------------------------------------

function applySort(list) {
  const sorted = [...list];

  switch (sortValue) {
    case 'oldest':
      sorted.sort((a, b) => new Date(a.createdAt || 0) - new Date(b.createdAt || 0));
      break;
    case 'updated':
      sorted.sort((a, b) => new Date(b.modifiedAt || 0) - new Date(a.modifiedAt || 0));
      break;
    case 'az':
      sorted.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
      break;
    case 'newest':
    default:
      sorted.sort((a, b) => new Date(b.createdAt || 0) - new Date(a.createdAt || 0));
      break;
  }

  return sorted;
}

// ---------------------------------------------------------------------------
// Card Rendering
// ---------------------------------------------------------------------------

function renderGrid() {
  if (!elGrid || !elEmpty) return;

  const filtered = getFilteredActors();

  // Show / hide empty state
  if (filtered.length === 0) {
    elEmpty.style.display = '';
    elGrid.style.display = 'none';
    return;
  }

  elEmpty.style.display = 'none';
  elGrid.style.display = '';

  // Build fragment for batch DOM insertion
  const fragment = document.createDocumentFragment();

  for (const actor of filtered) {
    fragment.appendChild(createCardEl(actor));
  }

  // Clear and append
  elGrid.innerHTML = '';
  elGrid.appendChild(fragment);
}

function createCardEl(actor) {
  const article = document.createElement('article');
  article.className = 'card';
  article.setAttribute('role', 'listitem');

  // Icon
  const iconDiv = document.createElement('div');
  iconDiv.className = 'card__icon';

  if (actor.iconUrl) {
    const img = document.createElement('img');
    img.src = actor.iconUrl;
    img.alt = `${actor.title} icon`;
    img.loading = 'lazy';
    img.onerror = () => {
      // Fallback to letter initial on image error
      img.replaceWith(createLetterFallback(actor));
    };
    iconDiv.appendChild(img);
  } else {
    iconDiv.appendChild(createLetterFallback(actor));
  }

  // Header (title + status)
  const header = document.createElement('div');
  header.className = 'card__header';

  const title = document.createElement('h2');
  title.className = 'card__title';
  title.textContent = actor.title || 'Untitled Actor';

  const status = document.createElement('span');
  status.className = `card__status ${actor.isPublic ? 'card__status--public' : 'card__status--private'}`;
  status.innerHTML = `<span class="card__status-dot"></span>${actor.isPublic ? 'Public' : 'Private'}`;

  header.appendChild(title);
  header.appendChild(status);

  // Summary / description
  const summary = document.createElement('p');
  summary.className = 'card__summary';
  summary.textContent = actor.description || '';

  // Category badge
  const category = document.createElement('span');
  category.className = 'card__category';
  category.textContent = actor.category || 'Other';

  // Stats row
  const statsRow = document.createElement('div');
  statsRow.className = 'card__stats';

  const stats = actor.stats || {};
  if (stats.totalRuns || stats.totalUsers) {
    const runsSpan = document.createElement('span');
    if (stats.totalRuns) runsSpan.innerHTML = `<svg class="icon" aria-hidden="true"><use href="#icon-arrow" /></svg> ${stats.totalRuns} runs`;
    statsRow.appendChild(runsSpan);

    const usersSpan = document.createElement('span');
    if (stats.totalUsers) usersSpan.innerHTML = `${stats.totalUsers} users`;
    statsRow.appendChild(usersSpan);
  }

  // CTA link
  const cta = document.createElement('a');
  cta.className = 'card__cta';
  cta.href = actor.link || '#';
  cta.target = '_blank';
  cta.rel = 'noopener';
  cta.textContent = 'View on Apify';
  const ctaIcon = document.createElement('svg');
  ctaIcon.className = 'icon';
  ctaIcon.setAttribute('aria-hidden', 'true');
  ctaIcon.innerHTML = '<use href="#icon-arrow" />';
  cta.appendChild(ctaIcon);

  // Assemble card
  article.appendChild(iconDiv);
  article.appendChild(header);
  article.appendChild(summary);
  article.appendChild(category);
  article.appendChild(statsRow);
  article.appendChild(cta);

  return article;
}

/** Create a letter-initial fallback for missing icon images. */
function createLetterFallback(actor) {
  const span = document.createElement('span');
  span.className = 'card__icon-letter';
  const initial = (actor.title || 'A').charAt(0).toUpperCase();
  span.textContent = initial;
  return span;
}

// ---------------------------------------------------------------------------
// Search & Keyboard Shortcuts
// ---------------------------------------------------------------------------

let searchTimeout = null;

function handleSearch(input) {
  const q = input.value.trim();

  // Show / hide clear button based on whether search has text
  if (elClear) elClear.hidden = q.length === 0;

  // Debounce: only re-render after 300ms of inactivity
  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    searchQuery = q;
    renderGrid();
    renderChips(); // update count badges after filter
  }, 300);
}

function clearSearch() {
  if (elSearch) elSearch.value = '';
  searchQuery = '';
  renderGrid();
  renderChips();
  if (elSearch) elSearch.focus();
}

function focusSearch(e) {
  // / key focuses search (but not when typing in an input)
  if (e.key === '/' && document.activeElement !== elSearch &&
      !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName)) {
    e.preventDefault();
    elSearch?.focus();
  }

  // Escape clears search
  if (e.key === 'Escape' && elSearch && document.activeElement === elSearch) {
    clearSearch();
  }
}

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

function init() {
  // Cache DOM refs
  elStats = $('#stats');
  elGrid = $('#grid');
  elEmpty = $('#empty');
  elSearch = $('#search');
  elClear = $('#search-clear');
  elChips = $('#chips');
  elSort = $('#sort');

  // Event listeners
  elSearch.addEventListener('input', () => handleSearch(elSearch));
  elClear.addEventListener('click', clearSearch);
  document.addEventListener('keydown', focusSearch);

  elSort.addEventListener('change', () => {
    sortValue = elSort.value;
    renderGrid();
  });

  // Load data and render
  loadData();
}

// Boot on DOM ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
