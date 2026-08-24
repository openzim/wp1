<template>
  <div class="wp1r flex flex-1 flex-col bg-page">
    <div
      class="mx-auto flex w-full max-w-[1200px] flex-1 flex-col border-x border-border bg-surface"
    >
      <!-- The hero block keeps its position whether or not a table is
           shown below, so selecting a project never shifts the layout. -->
      <div
        class="mx-auto flex w-full max-w-[560px] flex-col items-stretch px-6 pt-20"
      >
        <div class="wp1r-microlabel">Wikipedia 1.0 Server</div>
        <h2 class="mb-2 mt-1 text-[20px] font-semibold tracking-[-0.015em]">
          Projects
        </h2>
        <p class="mb-5 mt-0 text-[13.5px] leading-[1.55] text-ink-2">
          Search for a WikiProject to view its quality × importance assessment
          table.
        </p>
        <Autocomplete
          size="lg"
          :incomingSearch="incomingSearch || $route.params.projectName"
          v-on:select-project="currentProject = $event"
        ></Autocomplete>
        <p
          v-if="projectCount !== null"
          class="mt-16 text-center font-mono text-[12px] text-ink-3"
        >
          {{ projectCount.toLocaleString() }} projects tracked
        </p>
      </div>
      <div class="px-[18px] pb-16 pt-6">
        <ProjectTable v-bind:projectId="currentProjectId"></ProjectTable>
      </div>
    </div>
  </div>
</template>

<script>
import Autocomplete from './Autocomplete.vue';
import ProjectTable from './ProjectTable.vue';

export default {
  name: 'index-page',
  components: {
    Autocomplete,
    ProjectTable,
  },
  data: function () {
    return {
      currentProject: null,
      incomingSearch: null,
      projectCount: null,
    };
  },
  computed: {
    currentProjectId: function () {
      if (!this.currentProject) {
        return null;
      }
      return this.currentProject.replace(/ /g, '_');
    },
  },
  created: async function () {
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/count`
      );
      const data = await response.json();
      this.projectCount = data.count;
    } catch (err) {
      console.error(err);
    }
  },
  watch: {
    currentProject: function (val) {
      if (val && val !== this.$route.params.projectName) {
        this.$router.push({ path: `/project/${val}` });
      }
    },
  },
  // Serves both / and /project/:projectName; the instance is reused across
  // the two records, so param changes and returns to the bare index are
  // handled here.
  beforeRouteUpdate(to, from, next) {
    if (to.params.projectName) {
      this.incomingSearch = to.params.projectName;
    } else {
      this.incomingSearch = null;
      this.currentProject = null;
    }
    next();
  },
};
</script>
