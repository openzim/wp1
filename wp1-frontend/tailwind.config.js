/**
 * Tailwind is used only by the redesigned Selections pages (and the global
 * app chrome). The rest of the app is still Bootstrap 4; preflight is
 * disabled so Tailwind never restyles those pages. Design tokens come from
 * the OpenZIM Selections redesign handoff.
 */
module.exports = {
  content: ['./index.html', './src/**/*.{vue,js}'],
  corePlugins: {
    preflight: false,
    container: false,
  },
  // Bootstrap markup on the untouched pages uses class="collapse"
  // (accordions, navbars). Tailwind's .collapse utility (visibility:
  // collapse) must not be emitted or it breaks them.
  blocklist: ['collapse'],
  theme: {
    extend: {
      colors: {
        page: '#eceeef',
        // Header/footer chrome bands: a step darker than the page grey so
        // the white content column reads between them.
        chrome: {
          DEFAULT: '#dfe3e6',
          edge: '#ced3d7',
        },
        surface: {
          DEFAULT: '#ffffff',
          muted: '#fafbfb',
        },
        // Two effective border weights: DEFAULT for standard control/card
        // edges, strong for emphasized structure (genuinely darker than
        // DEFAULT). The subtle/row/row-light names are kept as aliases of a
        // single hairline tint so templates don't churn, but they are one
        // color on purpose — the old ~4-hex-step distinctions were
        // invisible.
        border: {
          DEFAULT: '#dfe3e6',
          strong: '#ced3d7',
          subtle: '#eef0f2',
          row: '#eef0f2',
          'row-light': '#eef0f2',
        },
        // Text tiers. Every tier used for text must hold WCAG AA (>= 4.5:1)
        // on both surface.DEFAULT and surface.muted; ink-5 is reserved for
        // decorative, aria-hidden glyphs only.
        ink: {
          DEFAULT: '#14171a',
          2: '#4c545c',
          3: '#5d6670',
          4: '#697380',
          5: '#c3c9cf',
        },
        accent: {
          DEFAULT: '#2456c9',
          hover: '#1d49ad',
          'link-hover': '#1a3f97',
          tint: '#f7f9fe',
          'tint-2': '#eef2fc',
          border: '#cfdcf8',
          'border-2': '#b9cbf3',
        },
        ok: {
          DEFAULT: '#1f7a4d',
          border: '#cfe4d8',
          tint: '#f2f9f5',
          'tint-2': '#f7faf8',
        },
        warn: {
          DEFAULT: '#b8860b',
          text: '#8a5b00',
          'text-strong': '#6b4b00',
          tint: '#fdf8ec',
          border: '#f2e2bd',
          'border-2': '#e6d3a8',
        },
        danger: {
          DEFAULT: '#b3261e',
          border: '#f0d5d2',
          tint: '#fdf5f4',
          'tint-2': '#fdf8f7',
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
        card: '0 1px 2px rgba(20,23,26,0.04)',
      },
    },
  },
  plugins: [],
};
