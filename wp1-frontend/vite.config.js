import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
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
