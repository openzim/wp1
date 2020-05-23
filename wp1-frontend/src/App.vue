<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="#">Wikipedia 1.0 Server</a>
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
              'nav-item ' + (this.$route.path !== '/update' ? 'active' : '')
            "
          >
            <router-link class="nav-link" to="/">Projects</router-link>
          </li>
          <li
            :class="
              'nav-item ' + (this.$route.path === '/update' ? 'active' : '')
            "
          >
            <router-link class="nav-link" to="/update"
              >Manual Update</router-link
            >
          </li>
        </ul>
      </div>
    </nav>
    <div id="app" class="container">
      <div class="row">
        <div class="col">
          <Stats></Stats>
        </div>
      </div>
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
import Stats from './components/Stats.vue';

export default {
  name: 'app',
  components: {
    Stats
  }
};
</script>

<style>
.row {
  margin-top: 10px;
}
</style>
