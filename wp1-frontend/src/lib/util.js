export function localDate(secs) {
  const date = new Date(secs * 1000);
  if (isNaN(date.getTime())) {
    // Missing/invalid timestamps render as blank rather than throwing.
    return '';
  }
  const fmt = new Intl.DateTimeFormat('en-US', {
    dateStyle: 'short',
    timeStyle: 'short',
  });
  return fmt.format(date);
}
