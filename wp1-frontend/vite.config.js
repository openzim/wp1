import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue2';
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
    host: '0.0.0.0',
    watch: {
      usePolling: true,
    },
  },
  preview: {
    port: 5173,
  },
});
