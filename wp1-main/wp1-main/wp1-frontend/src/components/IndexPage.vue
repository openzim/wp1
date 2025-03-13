<template>
  <div class="container">
    <div class="row">
      <div class="col-xl-6">
        <Autocomplete
          v-on:select-project="currentProject = $event"
        ></Autocomplete>
      </div>
    </div>
  </div>
</template>

<script>
import Autocomplete from './Autocomplete.vue';

export default {
  name: 'app',
  components: {
    Autocomplete
  },
  data: function() {
    return {
      currentProject: null
    };
  },
  watch: {
    currentProject: function(val) {
      this.$router.replace({ path: `project/${val}` });
    }
  }
};
</script>

<style></style>
