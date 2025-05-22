export function localDate(secs) {
  const fmt = new Intl.DateTimeFormat('en-US', {
    dateStyle: 'short',
    timeStyle: 'short',
  });
  return fmt.format(new Date(secs * 1000));
}
