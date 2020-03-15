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
    <div class="row">
      <div class="col">
        <ProjectTable v-bind:projectId="currentProjectId"></ProjectTable>
      </div>
    </div>
  </div>
</template>

<script>
import Autocomplete from './Autocomplete.vue';
import ProjectTable from './ProjectTable.vue';

export default {
  name: 'projectpage',
  components: {
    Autocomplete,
    ProjectTable
  },
  data: function() {
    return {
      currentProject: null
    };
  },
  computed: {
    currentProjectId: function() {
      if (!this.currentProject) {
        return null;
      }
      return this.currentProject.replace(/ /g, '_');
    }
  }
};
</script>

<style></style>
