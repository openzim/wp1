<template>
  <div>
    <div class="alert alert-info my-0" role="alert">
      Welcome to the latest version of the WP 1.0 tool! Please provide all
      feedback and feature requests for this tool on
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
                !this.$route.path.startsWith('/compare')
                  ? 'active'
                  : '')
            "
          >
            <router-link class="nav-link" to="/">Projects</router-link>
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
          <div v-if="this.token">
            <button @click="logout">Logout</button>
            <span>Username</span>
          </div>
          <a v-else href="http://127.0.0.1:5000/v1/oauth/initiate"
            ><button>Login</button></a
          >
        </div>
      </div>
    </nav>
    <div id="app" class="container">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'app',
  data: function() {
    return {
      token: null
    };
  },
  methods: {
    logout: async function() {
      localStorage.removeItem('token');
      window.location.href = 'http://localhost:3000/#/';
      await fetch(`${process.env.VUE_APP_API_URL}/oauth/logout`, {
        method: 'POST',
        body: JSON.stringify(this.token)
      });
      this.token = null;
      localStorage.removeItem('token', this.token);
    }
  },
  created: async function() {
    if (!window.location.hash.split('?')[1]) {
      return;
    }
    this.token = window.location.hash.split('?')[1];
    console.log(this.token);
    const response = await fetch(`${process.env.VUE_APP_API_URL}/oauth/token`, {
      credentials: 'include',
      method: 'GET',
      body: JSON.stringify(this.token)
    });
    this.token = await response.json();
    localStorage.setItem('token', this.token);
  }
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
</style>
