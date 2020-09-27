<template>
  <div>
    <div class="row">
      <div clas="col-xl-6">
        Select two projects to compare the articles that are in both, with
        optional quality and importance filters for each.
      </div>
    </div>
    <div class="row mt-4">
      <div class="col-xl-6">
        <Autocomplete
          :incomingSearch="incomingSearchA || $route.params.projectNameA"
          :hideInstructions="true"
          v-on:select-project="projectA = $event"
        ></Autocomplete>
      </div>
    </div>
    <div class="row mt-4">
      <div class="col-xl-6">
        <Autocomplete
          :incomingSearch="incomingSearchB || $route.params.projectNameB"
          :hideInstructions="true"
          v-on:select-project="projectB = $event"
        ></Autocomplete>
      </div>
    </div>
    <div class="row mt-4">
      <div class="col-xl-6">
        <div class="input-group">
          <button
            v-on:click="onCompareClick()"
            :disabled="!projectsSelected"
            class="btn btn-primary form-control"
          >
            Compare
          </button>
        </div>
      </div>
    </div>
    <div class="row mt-4">
      <div class="col">
        <div v-if="projectsSelected">
          The projects are {{ projectA }} and {{ projectB }}.
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
  props: ['incomingSearchA', 'incomingSearchB'],
  data: function() {
    return {
      projectA: null,
      projectB: null
    };
  },
  computed: {
    currentProjectIdA: function() {
      if (!this.projectA) {
        return null;
      }
      return this.currentProjectA.replace(/ /g, '_');
    },
    currentProjectIdB: function() {
      if (!this.projectB) {
        return null;
      }
      return this.currentProjectB.replace(/ /g, '_');
    },
    projectsSelected: function() {
      return !!this.projectA && !!this.projectB;
    }
  },
  methods: {
    onCompareClick: async function() {}
  }
};
</script>

<style></style>
