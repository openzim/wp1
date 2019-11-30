<template>
  <div id="app" class="container">
    <div class="row">
      <div class="col">
        <h1>Wikipedia 1.0 Server</h1>
        <Stats></Stats>
      </div>
    </div>
  </div>
</template>

<script>
import Stats from './components/Stats.vue'

export default {
  name: 'app',
  components: {
    Stats,
  },
}
</script>

<style>
  #app {
    margin-top: 10px;
  }
</style>
