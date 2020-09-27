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
    <div class="row">
      <div class="col-xl-6">
        <ArticleTableRatingSelect
          :projectId="projectIdA"
          :layout="'alternate'"
          v-on:rating-select="onProjectARatingSelect($event)"
        ></ArticleTableRatingSelect>
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
    <div class="row">
      <div class="col-xl-6">
        <ArticleTableRatingSelect
          :projectId="projectIdB"
          :layout="'alternate'"
          v-on:rating-select="onProjectBRatingSelect($event)"
        ></ArticleTableRatingSelect>
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
    <div v-if="projectsSelected && compareClicked" class="row mt-4">
      <div class="col">
        <ArticleTable
          :hideRatingSelect="true"
          :projectId="projectIdA"
          :projectIdB="projectIdB"
          :importance="projectAImportance"
          :quality="projectAQuality"
          :importanceB="projectBImportance"
          :qualityB="projectBQuality"
          :page="$route.query.page"
          :numRows="$route.query.numRows"
          :articlePattern="$route.query.articlePattern"
        ></ArticleTable>
      </div>
    </div>
  </div>
</template>

<script>
import ArticleTable from './ArticleTable.vue';
import ArticleTableRatingSelect from './ArticleTableRatingSelect';
import Autocomplete from './Autocomplete.vue';

export default {
  name: 'updatepage',
  components: {
    ArticleTable,
    ArticleTableRatingSelect,
    Autocomplete
  },
  props: ['incomingSearchA', 'incomingSearchB'],
  data: function() {
    return {
      projectA: null,
      projectB: null,
      projectAQuality: null,
      projectAImportance: null,
      projectBQuality: null,
      projectBImportance: null,
      compareClicked: false
    };
  },
  computed: {
    projectIdA: function() {
      if (!this.projectA) {
        return null;
      }
      return this.projectA.replace(/ /g, '_');
    },
    projectIdB: function() {
      if (!this.projectB) {
        return null;
      }
      return this.projectB.replace(/ /g, '_');
    },
    projectsSelected: function() {
      return !!this.projectA && !!this.projectB;
    }
  },
  methods: {
    onCompareClick: async function() {
      this.compareClicked = true;
    },
    onProjectARatingSelect: function(event) {
      this.projectAQuality = event.quality;
      this.projectAImportance = event.importance;
    },
    onProjectBRatingSelect: function(event) {
      this.projectBQuality = event.quality;
      this.projectBImportance = event.importance;
    }
  }
};
</script>

<style></style>
