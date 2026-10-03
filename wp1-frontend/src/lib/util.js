// Wikipedia-style (ISO) local timestamp, e.g. `2026-07-25 22:46`.
export function isoDateTime(secs) {
  const d = new Date(secs * 1000);
  const pad = (n) => String(n).padStart(2, '0');
  return (
    `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ` +
    `${pad(d.getHours())}:${pad(d.getMinutes())}`
  );
}

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
