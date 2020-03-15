<template>
  <div>
    <div class="row">
      <div class="col-6">
        <p>
          A list of indexed projects is available using the autocomplete search
          box below
        </p>
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
