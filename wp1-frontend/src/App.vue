<template>
  <div id="app">
    <div class="alert alert-info my-0" role="alert">
      Welcome to the latest version of WP 1.0! Documentation is on
      <a href="https://wp1.readthedocs.io/en/latest/">read the docs</a>. Please
      provide all feedback on
      <a
        href="https://en.wikipedia.org/wiki/Wikipedia_talk:Version_1.0_Editorial_Team/Index"
        >English Wikipedia</a
      >.
    </div>
    <div id="replag-embed" data-wiki="en.wikipedia.org"></div>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="/">Wikipedia 1.0 Server</a>
      <button
        class="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav mr-auto">
          <li
            :class="
              'nav-item ' +
              (!this.$route.path.startsWith('/update') &&
              !this.$route.path.startsWith('/compare') &&
              !this.$route.path.startsWith('/selections')
                ? 'active'
                : '')
            "
          >
            <router-link class="nav-link" to="/">Projects</router-link>
          </li>
          <li
            :class="
              'nav-item ' +
              (this.$route.path.startsWith('/selections') ? 'active' : '')
            "
          >
            <router-link class="nav-link" to="/selections/user"
              >Selections</router-link
            >
          </li>
          <li
            :class="
              'nav-item ' +
              (this.$route.path.startsWith('/update') ? 'active' : '')
            "
          >
            <router-link class="nav-link" to="/update"
              >Manual Update</router-link
            >
          </li>
          <li
            :class="
              'nav-item ' +
              (this.$route.path.startsWith('/compare') ? 'active' : '')
            "
          >
            <router-link class="nav-link" to="/compare"
              >Compare Projects</router-link
            >
          </li>
        </ul>
        <div>
          <div v-if="this.username">
            <span class="username"> {{ this.username }} </span>
            <button type="button" class="btn btn-secondary" @click="logout">
              Logout
            </button>
          </div>
          <a v-else :href="this.loginInitiateUrl"
            ><button type="button" class="btn btn-primary">Login</button>
          </a>
        </div>
      </div>
    </nav>
    <div class="main-content">
      <router-view></router-view>
    </div>
    <footer class="footer bg-light border-top">
      <div class="container-fluid py-3">
        <div class="text-right">
          <a href="https://kiwix.org/privacy-policy/" target="_blank" rel="noopener noreferrer">
            Privacy Policy
          </a>
        </div>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'app',
  data: function () {
    return {
      username: null,
      loginInitiateUrl: `${import.meta.env.VITE_API_URL}/oauth/initiate`,
    };
  },
  methods: {
    logout: async function () {
      await fetch(`${import.meta.env.VITE_API_URL}/oauth/logout`, {
        credentials: 'include',
      });
      this.username = null;
      this.$root.$data.isLoggedIn = false;
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
        },
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
        this.$root.$data.isLoggedIn = true;
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
/* 1. CSS Variables for Themes */
:root {
  --bg-main: #ffffff;
  --text-main: #212529;
  --nav-bg: #f8f9fa;
  --footer-bg: #f8f9fa;
  --link-color: #0063cc;
  --link-hover: #000;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg-main: #121212;
    --text-main: #e0e0e0;
    --nav-bg: #1f1f1f;
    --footer-bg: #1f1f1f;
    --link-color: #66b2ff;
    --link-hover: #ffffff;
  }
}

/* 2. Global Styles */
html, body {
  height: 100%;
  background-color: var(--bg-main) !important;
  color: var(--text-main) !important;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: var(--bg-main);
  color: var(--text-main);
}

.main-content {
  flex: 1;
  padding-bottom: 20px;
}

/* 3. Navbar & Footer Styles */
.footer {
  margin-top: auto;
  background-color: var(--footer-bg) !important;
}

.footer a {
  color: var(--link-color);
  text-decoration: none;
}

.footer a:hover {
  color: var(--link-hover);
  text-decoration: underline;
}

/* 4. Link & Component Styles */
a {
  color: var(--link-color);
}
a:hover, a:visited {
  color: var(--link-hover) !important;
}

.btn-primary {
  background-color: #0071eb;
}

.row {
  margin-top: 10px;
}

.username {
  position: relative;
  top: 2px;
}

/* 5. Dark Mode Component Overrides */
@media (prefers-color-scheme: dark) {
  .navbar-light.bg-light {
    background-color: var(--nav-bg) !important;
    border-color: #333 !important;
  }
  
  .navbar-light .navbar-nav .nav-link, 
  .navbar-light .navbar-brand {
    color: var(--text-main) !important;
  }

  .alert-info {
    background-color: #0c5460 !important;
    color: #bee5eb !important;
    border-color: #117a8b !important;
  }
}
</style>