// Shared helpers for the redesigned Selections screens. All data shapes
// mirror what the API returns from /v1/selection/lists and /v1/builders/*.

export const MODEL_LABELS = {
  simple: 'Simple',
  sparql: 'SPARQL',
  petscan: 'Petscan',
  book: 'Book',
  wikiproject: 'WikiProject',
  combinator: 'Combinator',
};

export const COMBINATOR_MODEL = 'wp1.selection.models.combinator';

// The six selection sources, in picker order. Blurbs are design-final copy.
export const SOURCES = [
  { key: 'simple', label: 'Simple', blurb: 'Paste article titles.' },
  {
    key: 'sparql',
    label: 'SPARQL',
    blurb: 'A Wikidata query returning articles.',
  },
  { key: 'petscan', label: 'Petscan', blurb: 'A saved Petscan URL or PSID.' },
  { key: 'book', label: 'Book', blurb: 'A Wikipedia book page.' },
  {
    key: 'wikiproject',
    label: 'WikiProject',
    blurb: 'Every article a project assesses.',
  },
  {
    key: 'combinator',
    label: 'Combinator',
    blurb: 'Combine selections you already have.',
  },
];

export function modelFragment(model) {
  if (!model) {
    return '';
  }
  const fragments = model.split('.');
  return fragments[fragments.length - 1];
}

export function modelLabel(model) {
  const fragment = modelFragment(model);
  return MODEL_LABELS[fragment] || fragment;
}

// ZIM/selection status vocabulary. Derived from the same fields the old
// MyLists table used; every screen shares this single derivation.
//
// dot: Tailwind classes for the 7px status dot.
export const STATUSES = {
  processing: {
    key: 'processing',
    label: 'Processing…',
    dot: 'bg-accent',
    attention: false,
  },
  selection_failed: {
    key: 'selection_failed',
    label: 'Failed',
    dot: 'bg-danger',
    attention: true,
  },
  building: {
    key: 'building',
    label: 'Building…',
    dot: 'bg-accent',
    attention: false,
  },
  ready: {
    key: 'ready',
    label: 'Up to date',
    dot: 'bg-ok',
    attention: false,
  },
  stale: {
    key: 'stale',
    label: 'Stale',
    dot: 'bg-warn',
    attention: true,
  },
  expired: {
    key: 'expired',
    label: 'Expired',
    dot: 'bg-warn',
    attention: true,
  },
  zim_failed: {
    key: 'zim_failed',
    label: 'Failed',
    dot: 'bg-danger',
    attention: true,
  },
  none: {
    key: 'none',
    label: 'No ZIM',
    // Filled muted dot: the hollow variant read as an empty radio button.
    dot: 'bg-ink-5',
    attention: false,
  },
};

// Selection materialization status — the backend re-renders the TSV after
// every save. Shown separately from the ZIM status in the detail pane.
export const SELECTION_STATUSES = {
  processing: STATUSES.processing,
  failed: STATUSES.selection_failed,
  ready: {
    key: 'selection_ready',
    label: 'Ready',
    dot: 'bg-ok',
    attention: false,
  },
};

export function selectionIsPending(item) {
  return (!item.s_url && !item.s_status) || item.updated_at > item.s_updated_at;
}

export function selectionHasError(item) {
  return !!item.s_status && item.s_status !== 'OK';
}

export function deriveSelectionStatus(item) {
  if (selectionHasError(item)) {
    return SELECTION_STATUSES.failed;
  }
  if (selectionIsPending(item)) {
    return SELECTION_STATUSES.processing;
  }
  return SELECTION_STATUSES.ready;
}

// Status of the ZIM file alone, ignoring the selection's materialization
// state.
export function deriveZimStatus(item) {
  if (item.z_status === 'REQUESTED') {
    return STATUSES.building;
  }
  if (item.z_status === 'FAILED') {
    return STATUSES.zim_failed;
  }
  if (item.z_status === 'FILE_READY') {
    if (item.z_is_deleted) {
      return STATUSES.expired;
    }
    if (item.z_updated_at && item.z_updated_at < item.s_updated_at) {
      return STATUSES.stale;
    }
    return STATUSES.ready;
  }
  return STATUSES.none;
}

// Single overall status, used by the rail rows and filters: selection
// problems and progress take precedence over the ZIM state.
export function deriveStatus(item) {
  if (selectionIsPending(item) && !selectionHasError(item)) {
    return STATUSES.processing;
  }
  if (selectionHasError(item)) {
    return STATUSES.selection_failed;
  }
  return deriveZimStatus(item);
}

export function hasZim(item) {
  return item.z_status && item.z_status !== 'NOT_REQUESTED';
}

export function apiUrl(path) {
  return `${import.meta.env.VITE_API_URL}${path}`;
}

export function tsvDownloadUrl(item) {
  return item.s_url;
}

// The TSV link is only valid once the selection has materialized cleanly;
// while re-rendering (or after an error) it would serve a stale or missing
// file.
export function tsvReady(item) {
  return !!item.s_url && !selectionIsPending(item) && !selectionHasError(item);
}

// A ZIM can only be requested once the selection has materialized cleanly;
// a failed or never-materialized selection has nothing to build from (the
// ZIM page's article-count fetch would just error out).
export function canRequestZim(item) {
  return !!item.s_url && !selectionHasError(item);
}

export function zimDownloadUrl(builderId) {
  return apiUrl(`/builders/${builderId}/zim/latest`);
}

export function detailPath(builderId) {
  return `/selections/user/${builderId}`;
}

export function editPath(item) {
  if (item.model === COMBINATOR_MODEL) {
    return `/selections/combinator/${item.id}`;
  }
  return `/selections/user/${item.id}/edit`;
}

export function zimPagePath(builderId) {
  return `/selections/${builderId}/zim`;
}

function groupExpression(group, nameForId) {
  const names = (group.builders || []).map(nameForId);
  const joiner = group.operation === 'intersection' ? ' AND ' : ' OR ';
  const joined = names.join(joiner);
  return names.length > 1 ? `(${joined})` : joined;
}

// Renders combinator params as e.g. `(Petscan Templates OR Democracy) NOT LGBTQ`.
export function combinatorExpression(params, nameForId) {
  const include = params.include || {};
  const exclude = params.exclude || {};
  const includeExpr =
    (include.builders || []).length > 0
      ? groupExpression(include, nameForId)
      : '…';
  if ((exclude.builders || []).length > 0) {
    return `${includeExpr} NOT ${groupExpression(exclude, nameForId)}`;
  }
  return includeExpr;
}

// Plain-English description of a combinator recipe.
export function combinatorSentence(params) {
  const include = params.include || {};
  const exclude = params.exclude || {};
  const nIncl = (include.builders || []).length;
  const nExcl = (exclude.builders || []).length;

  if (nIncl === 0) {
    return 'Add at least one selection to include.';
  }

  let sentence =
    include.operation === 'intersection'
      ? `Take the articles that appear in every one of ${nIncl} included ` +
        `selection${nIncl === 1 ? '' : 's'}`
      : `Take every article from ${nIncl} included selection` +
        `${nIncl === 1 ? '' : 's'}`;

  if (nExcl > 0) {
    sentence +=
      exclude.operation === 'intersection'
        ? `, then remove the articles shared by all ${nExcl} excluded ` +
          `selection${nExcl === 1 ? '' : 's'}.`
        : `, then remove any article in the ${nExcl} excluded selection` +
          `${nExcl === 1 ? '' : 's'}.`;
  } else {
    sentence += '.';
  }
  return sentence;
}

// The type-specific definition, rendered as preformatted text for the
// detail pane. nameForId resolves combinator member ids to names.
export function definitionText(model, params, nameForId) {
  switch (modelFragment(model)) {
    case 'simple':
      return (params.list || []).join('\n');
    case 'sparql':
      return params.query || '';
    case 'petscan':
    case 'book':
      return params.url || '';
    case 'wikiproject': {
      const lines = ['Include:'];
      (params.include || []).forEach((p) => lines.push(`  ${p}`));
      if ((params.exclude || []).length > 0) {
        lines.push('Exclude:');
        params.exclude.forEach((p) => lines.push(`  ${p}`));
      }
      return lines.join('\n');
    }
    case 'combinator':
      return combinatorExpression(params, nameForId);
    default:
      return JSON.stringify(params, null, 2);
  }
}

// One-sentence plain-English note shown under the definition.
export function definitionNote(model, params) {
  switch (modelFragment(model)) {
    case 'simple': {
      const n = (params.list || []).filter(
        (line) => line.trim() && !line.trim().startsWith('#')
      ).length;
      return `${n} title${n === 1 ? '' : 's'}.`;
    }
    case 'sparql':
      return 'A Wikidata SPARQL query, re-run on every rebuild.';
    case 'petscan':
      return 'A Petscan query, re-run on every rebuild.';
    case 'book':
      return 'Every article in a Wikipedia book page.';
    case 'wikiproject':
      return 'Every article assessed by the listed WikiProjects.';
    case 'combinator':
      return combinatorSentence(params);
    default:
      return '';
  }
}

// Human description of an active schedule from /zim/status, e.g.
// `Every 3 months · next 8/1/26`.
export function describeSchedule(activeSchedule) {
  if (!activeSchedule) {
    return null;
  }
  const months = activeSchedule.interval_months;
  let text = months === 1 ? 'Every month' : `Every ${months} months`;
  if (activeSchedule.next_generation_date) {
    // Wikipedia-style (ISO) date; the backend already sends YYYY-MM-DD.
    const formatted = String(activeSchedule.next_generation_date).slice(0, 10);
    text += ` · next ${formatted}`;
  }
  return text;
}
