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
        <div v-if="this.$route.params.projectName && !updateTime">
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
        <div v-if="this.$route.params.projectName && updateTime">
          <p>
            Manual update of <b>{{ this.$route.params.projectName }}</b> has
            been scheduled. It can take anywhere from 2 - 200 minutes, depending
            on project size. The next update can be performed at
            <b>{{ updateTime }}</b
            >.
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
  props: ['incomingSearch'],
  data: function() {
    return {
      currentProject: null,
      updateTime: null
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
    currentProject: async function(val) {
      if (val !== this.$route.params.projectName) {
        this.$router.push({ path: `/update/${val}` });
      }
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${this.currentProjectId}/nextUpdateTime`
      );
      const data = await response.json();
      this.updateTime = data.next_update_time;
    }
  },
  beforeRouteUpdate(to, from, next) {
    this.incomingSearch = to.params.projectName;
    next();
  },
  methods: {
    onUpdateClick: async function() {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${this.currentProjectId}/update`,
        { method: 'POST' }
      );
      const data = await response.json();
      this.updateTime = data.next_update_time;
    }
  }
};
</script>

<style></style>
