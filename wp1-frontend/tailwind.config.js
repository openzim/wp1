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
        border: {
          DEFAULT: '#dfe3e6',
          strong: '#e2e5e8',
          subtle: '#eaedef',
          row: '#f0f2f3',
          'row-light': '#f4f5f6',
        },
        ink: {
          DEFAULT: '#14171a',
          2: '#4c545c',
          3: '#6b7480',
          4: '#9aa2ab',
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
