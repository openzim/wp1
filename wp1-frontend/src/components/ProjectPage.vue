<template>
  <div>
    <div class="row">
      <div class="col-6">
        <Autocomplete
          :incomingSearch="incomingSearch || $route.params.projectName"
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
      currentProject: null,
      incomingSearch: null
    };
  },
  computed: {
    currentProjectId: function() {
      if (!this.currentProject) {
        return null;
      }
      return this.currentProject.replace(/ /g, '_');
    }
  },
  watch: {
    currentProject: function(val) {
      if (val !== this.$route.params.projectName) {
        this.$router.push({ path: `/project/${val}` });
      }
    }
  },
  beforeRouteUpdate(to, from, next) {
    this.incomingSearch = to.params.projectName;
    next();
  }
};
</script>

<style></style>
