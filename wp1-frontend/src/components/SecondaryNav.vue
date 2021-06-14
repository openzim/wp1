<template>
  <div>
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="/">Selection</a>
      <button
        class="navbar-toggler"
        type="button"
        data-toggle="collapse"
        data-target="#selections"
        aria-controls="selections"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="selections">
        <ul class="navbar-nav mr-auto">
          <li
            :class="
              'nav-item ' +
                (this.$route.path.startsWith('/selection/myLists')
                  ? 'active'
                  : '')
            "
          >
            <router-link class="nav-link" to="/selection/myLists"
              >My Lists</router-link
            >
          </li>
          <li
            :class="
              'nav-item ' +
                (this.$route.path.startsWith('/selection/createSimpleList')
                  ? 'active'
                  : '')
            "
          >
            <router-link class="nav-link" to="/selection/createSimpleList"
              >Create Simple List</router-link
            >
          </li>
        </ul>
      </div>
    </nav>
  </div>
</template>

<script>
export default {
  name: 'SecondaryNav'
};
</script>

<style scoped></style>
