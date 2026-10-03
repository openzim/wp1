import { reactive } from 'vue';

// Minimal shared state, replacing the Vue 2 pattern of reading
// $root.$data. reactive() works identically in Vue 2.7 and Vue 3.
export const loginStore = reactive({ isLoggedIn: false });
