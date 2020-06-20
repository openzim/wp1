<template>
  <div>
    <div class="alert alert-info my-0" role="alert">
      Welcome to the latest version of the WP 1.0 tool! If you need a feature
      that is only in the old tool, it's still running
      <a href="https://tools.wmflabs.org/enwp10/cgi-bin/pindex.fcgi">here</a>.
      Please provide all feedback and feature requests for this tool on
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
                (!this.$route.path.startsWith('/update') ? 'active' : '')
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
        </ul>
      </div>
    </nav>
    <div id="app" class="container">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'app'
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
