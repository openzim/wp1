<template>
  <div id="app">
    <div id="replag-embed" data-wiki="en.wikipedia.org"></div>
    <header class="wp1r border-b border-chrome-edge bg-chrome">
      <nav
        class="flex h-12 items-center gap-2 overflow-x-auto px-3"
        aria-label="Main navigation"
      >
        <router-link to="/" class="wp1r-brand flex shrink-0 items-center gap-2">
          <span class="text-[15px] font-semibold">WP1</span>
        </router-link>
        <div class="ml-2 flex items-center gap-0.5">
          <router-link
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="wp1r-navlink"
            :class="{ 'wp1r-navlink-active': isActiveNav(item) }"
            >{{ item.label }}</router-link
          >
        </div>
        <div class="ml-auto flex shrink-0 items-center gap-2.5 pl-2">
          <template v-if="username">
            <span class="text-sm text-ink">{{ username }}</span>
            <span
              aria-hidden="true"
              class="flex h-6 w-6 items-center justify-center rounded-full border border-border bg-[#e9edf6] text-[11px] font-medium text-ink-2"
              >{{ username.charAt(0).toUpperCase() }}</span
            >
            <span
              aria-hidden="true"
              class="h-[18px] w-px bg-border-strong"
            ></span>
            <button
              type="button"
              class="cursor-pointer border-0 bg-transparent p-0 text-sm text-ink-2 hover:text-ink"
              @click="logout"
            >
              Log out
            </button>
          </template>
          <a v-else :href="loginInitiateUrl" class="wp1r-btn-primary h-7 px-3"
            >Login</a
          >
        </div>
      </nav>
    </header>
    <div
      class="main-content"
      :class="{ 'main-content-flush': isSelectionsRoute }"
    >
      <router-view></router-view>
    </div>
    <footer class="wp1r border-t border-chrome-edge bg-chrome">
      <div class="flex h-12 items-center gap-1 px-3">
        <span class="px-[9px] text-sm text-ink-3">All times are local.</span>
        <span class="ml-auto"></span>
        <a
          href="https://en.wikipedia.org/wiki/Wikipedia_talk:Version_1.0_Editorial_Team/Index"
          target="_blank"
          rel="noopener noreferrer"
          class="wp1r-navlink"
        >
          Feedback
        </a>
        <a
          href="https://kiwix.org/privacy-policy/"
          target="_blank"
          rel="noopener noreferrer"
          class="wp1r-navlink"
        >
          Privacy Policy
        </a>
      </div>
    </footer>
  </div>
</template>

<script>
import { loginStore } from './store.js';

export default {
  name: 'app',
  data: function () {
    return {
      username: null,
      loginInitiateUrl: `${import.meta.env.VITE_API_URL}/oauth/initiate`,
      navItems: [
        { to: '/', label: 'Projects', prefix: null },
        { to: '/selections/user', label: 'Selections', prefix: '/selections' },
        { to: '/update', label: 'Manual Update', prefix: '/update' },
        { to: '/compare', label: 'Compare Projects', prefix: '/compare' },
        {
          to: '/assessments',
          label: 'Assessments by Project',
          prefix: '/assessments',
        },
      ],
    };
  },
  computed: {
    // The redesigned Selections pages render as a full-height column that
    // touches the header and footer; everything else keeps the padded flow.
    isSelectionsRoute: function () {
      return this.$route.path.startsWith('/selections');
    },
  },
  methods: {
    isActiveNav: function (item) {
      if (item.prefix === null) {
        return !this.navItems.some(
          (other) =>
            other.prefix !== null && this.$route.path.startsWith(other.prefix)
        );
      }
      return this.$route.path.startsWith(item.prefix);
    },
    logout: async function () {
      await fetch(`${import.meta.env.VITE_API_URL}/oauth/logout`, {
        credentials: 'include',
      });
      this.username = null;
      loginStore.isLoggedIn = false;
      this.$router.push({ path: `/` });
    },
    identify: async function () {
      if (this.username) {
        return;
      }
      const data = await fetch(
        `${import.meta.env.VITE_API_URL}/oauth/identify`,
        {
          credentials: 'include',
        }
      )
        .then((response) => {
          if (response.ok) {
            return response.json();
          } else {
            throw new Error(response.status);
          }
        })
        .catch((err) => {
          console.error(err);
        });
      if (data) {
        this.username = data.username;
        loginStore.isLoggedIn = true;
      }
    },
  },
  watch: {
    $route: function () {
      this.loginInitiateUrl =
        `${import.meta.env.VITE_API_URL}/oauth/initiate?next=` +
        this.$route.path.toString().substr(1);
    },
  },
  created: function () {
    this.identify();
  },
};
</script>

<style>
html,
body {
  height: 100%;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding-bottom: 20px;
}

.main-content-flush {
  display: flex;
  flex-direction: column;
  padding-bottom: 0;
}

a {
  color: #0063cc;
}
a:hover {
  color: #000 !important;
}
a:visited {
  color: #000 !important;
}

.btn-primary {
  background-color: #0071eb;
}

.row {
  margin-top: 10px;
}
</style>
