<template>
  <div>
    <div class="row">
      <div class="col-6">
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
  name: 'articlepage',
  components: {
    Autocomplete
  }
};
</script>

<style scoped></style>
