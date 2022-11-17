import { defineConfig } from 'vite';
import { createVuePlugin as vue } from 'vite-plugin-vue2';
import inject from '@rollup/plugin-inject';

const path = require('path');

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    inject({
      jQuery: 'jquery',
    }),
  ],
  build: {
    rollupOptions: {
      external: ['jquery'],
      output: {
        globals: {
          jquery: ['$', 'window.jQuery'],
        },
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  optimizeDeps: {
    include: ['jquery'],
  },
});
