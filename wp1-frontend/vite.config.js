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
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  optimizeDeps: {
    include: ['jquery'],
  },
  server: {
    port: 5173,
  },
  preview: {
    port: 5173,
  },
});
