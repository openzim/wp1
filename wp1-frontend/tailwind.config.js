/**
 * Tailwind styles the whole app (Bootstrap was retired with the
 * non-Selections redesign). Design tokens come from the OpenZIM Selections
 * redesign handoff.
 */
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        page: 'var(--color-page)',
        // Header/footer chrome bands: a step darker than the page grey so
        // the white content column reads between them.
        chrome: {
          DEFAULT: 'var(--color-chrome)',
          edge: 'var(--color-chrome-edge)',
        },
        surface: {
          DEFAULT: 'var(--color-surface)',
          muted: 'var(--color-surface-muted)',
        },
        // Two effective border weights: DEFAULT for standard control/card
        // edges, strong for emphasized structure (genuinely darker than
        // DEFAULT). The subtle/row/row-light names are kept as aliases of a
        // single hairline tint so templates don't churn, but they are one
        // color on purpose — the old ~4-hex-step distinctions were
        // invisible.
        border: {
          DEFAULT: 'var(--color-border)',
          strong: 'var(--color-border-strong)',
          subtle: 'var(--color-border-subtle)',
          row: 'var(--color-border-row)',
          'row-light': 'var(--color-border-row-light)',
        },
        // Text tiers. Every tier used for text must hold WCAG AA (>= 4.5:1)
        // on both surface.DEFAULT and surface.muted; ink-5 is reserved for
        // decorative, aria-hidden glyphs only.
        ink: {
          DEFAULT: 'var(--color-ink)',
          2: 'var(--color-ink-2)',
          3: 'var(--color-ink-3)',
          4: 'var(--color-ink-4)',
          5: 'var(--color-ink-5)',
        },
        accent: {
          DEFAULT: 'var(--color-accent)',
          hover: 'var(--color-accent-hover)',
          'link-hover': 'var(--color-accent-link-hover)',
          tint: 'var(--color-accent-tint)',
          'tint-2': 'var(--color-accent-tint-2)',
          border: 'var(--color-accent-border)',
          'border-2': 'var(--color-accent-border-2)',
        },
        ok: {
          DEFAULT: 'var(--color-ok)',
          border: 'var(--color-ok-border)',
          tint: 'var(--color-ok-tint)',
          'tint-2': 'var(--color-ok-tint-2)',
        },
        warn: {
          DEFAULT: 'var(--color-warn)',
          text: 'var(--color-warn-text)',
          'text-strong': 'var(--color-warn-text-strong)',
          tint: 'var(--color-warn-tint)',
          border: 'var(--color-warn-border)',
          'border-2': 'var(--color-warn-border-2)',
        },
        danger: {
          DEFAULT: 'var(--color-danger)',
          border: 'var(--color-danger-border)',
          tint: 'var(--color-danger-tint)',
          'tint-2': 'var(--color-danger-tint-2)',
        },
      },
      fontFamily: {
        sans: ['IBM Plex Sans', 'system-ui', 'sans-serif'],
        mono: [
          'IBM Plex Mono',
          'ui-monospace',
          'SFMono-Regular',
          'Menlo',
          'monospace',
        ],
      },
      boxShadow: {
        // Used by floating surfaces (overflow menu, autocomplete, dialog);
        // strong enough to read as elevation on a white page.
        card: 'var(--shadow-card)',
      },
    },
  },
  plugins: [],
};
