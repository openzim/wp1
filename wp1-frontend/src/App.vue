<template>
  <div>
    <div class="alert alert-info my-0" role="alert">
      Welcome to the latest version of WP 1.0! Documentation is on
      <a href="https://wp1.readthedocs.io/en/latest/">read the docs</a>. Please
      provide all feedback on
      <a
        href="https://en.wikipedia.org/wiki/Wikipedia_talk:Version_1.0_Editorial_Team/Index"
        >English Wikipedia</a
      >.
    </div>
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
    <div id="app">
      <router-view></router-view>
    </div>
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

.username {
  /* Center the username vertically */
  position: relative;
  top: 2px;
}
</style>
