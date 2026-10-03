// The assessment-class labels that carry a full-cell fill in labels.css.
// Labels outside this set (NA, ???, Other, Assessed…) render unfilled.
const FILLED_CLASSES = new Set([
  'Top',
  'High',
  'Mid',
  'Low',
  'FA',
  'GA',
  'B',
  'C',
  'Start',
  'Stub',
  'List',
  'Category',
  'Disambig',
  'File',
  'Project',
  'Redirect',
  'Template',
  'Unassessed',
]);

// Returns the label text usable as a labels.css fill class, or '' when the
// label has no fill.
export function fillClass(text) {
  return FILLED_CLASSES.has(text) ? text : '';
}
