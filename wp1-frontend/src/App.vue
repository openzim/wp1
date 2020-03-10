<template>
  <div id="app" class="container">
    <div class="row">
      <div class="col">
        <h1>Wikipedia 1.0 Server</h1>
        <Stats></Stats>
      </div>
    </div>
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
import Autocomplete from './components/Autocomplete.vue';
import ProjectTable from './components/ProjectTable.vue';
import Stats from './components/Stats.vue';

export default {
  name: 'app',
  components: {
    Autocomplete,
    ProjectTable,
    Stats
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

<style>
.row {
  margin-top: 10px;
}
</style>
