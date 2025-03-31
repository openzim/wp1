<template>
  <div>
    <div class="alert alert-info my-0" role="alert">
      {{ $t("welcomeMessage") }}
      <a href="https://wp1.readthedocs.io/en/latest/">read the docs</a>.
      {{ $t("provideFeedback") }}
      <a href="https://en.wikipedia.org/wiki/Wikipedia_talk:Version_1.0_Editorial_Team/Index">
        {{ $t("englishWikipedia") }}
      </a>.
    </div>

    <div class="language-selector">
      <label for="language">{{ $t("language") }}: </label>
      <select v-model="selectedLanguage" @change="changeLanguage">
        <option value="en">English</option>
        <option value="es">Español</option>
        <option value="fr">Français</option>
        <option value="ar">العربية</option>
      </select>
    </div>

    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="/">Wikipedia 1.0 Server</a>

      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarSupportedContent"
        aria-controls="navbarSupportedContent"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item">
            <router-link class="nav-link" to="/">{{ $t("projects") }}</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/selections/user">{{ $t("selections") }}</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/update">{{ $t("manualUpdate") }}</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/compare">{{ $t("compareProjects") }}</router-link>
          </li>
        </ul>

        <div>
          <div v-if="username">
            <span class="username"> {{ username }} </span>
            <button type="button" class="btn btn-secondary" @click="logout">
              {{ $t("logout") }}
            </button>
          </div>
          <a v-else :href="loginInitiateUrl">
            <button type="button" class="btn btn-primary">{{ $t("login") }}</button>
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
  data() {
    return {
      username: null,
      loginInitiateUrl: `${import.meta.env.VITE_API_URL}/oauth/initiate`,
      selectedLanguage: localStorage.getItem('lang') || 'en'
    };
  },
  methods: {
    logout: async function () {
      await fetch(`${import.meta.env.VITE_API_URL}/oauth/logout`, {
        credentials: 'include',
      });
      this.username = null;
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
        .then((response) => (response.ok ? response.json() : Promise.reject(response.status)))
        .catch((err) => console.error(err));

      if (data) {
        this.username = data.username;
      }
    },
    changeLanguage() {
      this.$i18n.locale = this.selectedLanguage;
      localStorage.setItem('lang', this.selectedLanguage);
    }
  },
  created() {
    this.identify();
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
  position: relative;
  top: 2px;
}
.language-selector {
  margin: 10px;
}
</style>
