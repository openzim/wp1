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
      <div class="col-6">
        <div v-if="this.$route.params.projectName && !showSuccessMessage">
          <label class="mt-2" for="confirm"
            >Proceed with manual update of
            <b>{{ this.$route.params.projectName }}</b
            >?</label
          >
          <div class="input-group">
            <button v-on:click="onUpdateClick()" class="btn-primary">
              Manual Update
            </button>
          </div>
        </div>
        <div v-if="this.$route.params.projectName && showSuccessMessage">
          <p>
            Manual update of <b>{{ this.$route.params.projectName }}</b> has
            been scheduled. It can take anywhere from 2 - 200 minutes, dpending
            on project size.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Autocomplete from './Autocomplete.vue';

export default {
  name: 'updatepage',
  components: {
    Autocomplete
  },
  data: function() {
    return {
      currentProject: null,
      incomingSearch: null,
      showSuccessMessage: false
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
        this.$router.push({ path: `/update/${val}` });
      }
    }
  },
  beforeRouteUpdate(to, from, next) {
    this.incomingSearch = to.params.projectName;
    this.showSuccessMessage = false;
    next();
  },
  methods: {
    onUpdateClick: async function() {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${this.currentProjectId}/update`
      );
      this.showSuccessMessage = response.ok;
    }
  }
};
</script>

<style></style>
