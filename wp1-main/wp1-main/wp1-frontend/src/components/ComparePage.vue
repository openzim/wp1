<template>
  <div class="container">
    <div class="row">
      <div clas="col-xl-6">
        Select two projects to compare the articles that are in both, with
        optional quality and importance filters for each.
      </div>
    </div>
    <div class="row mt-4">
      <div class="col-xl-6">
        <Autocomplete
          :incomingSearch="incomingSearchA"
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
          :initialQuality="this.$route.query.quality"
          :initialImportance="this.$route.query.importance"
          v-on:rating-select="onProjectARatingSelect($event)"
        ></ArticleTableRatingSelect>
      </div>
    </div>
    <div class="row mt-4">
      <div class="col-xl-6">
        <Autocomplete
          :incomingSearch="incomingSearchB"
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
          :initialQuality="this.$route.query.qualityB"
          :initialImportance="this.$route.query.importanceB"
          v-on:rating-select="onProjectBRatingSelect($event)"
        ></ArticleTableRatingSelect>
      </div>
    </div>
    <div v-if="showCompareButton" class="row mt-4">
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
    <div v-if="projectsSelected && !showCompareButton" class="row mt-4">
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
          v-on:page-select="onPageSelect($event)"
          v-on:name-filter="onNameFilter($event)"
          v-on:update-page="onUpdatePage($event)"
        ></ArticleTable>
      </div>
    </div>
  </div>
</template>

<script>
import ArticleTable from './ArticleTable.vue';
import ArticleTableRatingSelect from './ArticleTableRatingSelect.vue';
import Autocomplete from './Autocomplete.vue';

export default {
  name: 'update-page',
  components: {
    ArticleTable,
    ArticleTableRatingSelect,
    Autocomplete,
  },
  props: ['incomingSearchA', 'incomingSearchB'],
  data: function () {
    return {
      projectA: null,
      projectB: null,
      projectAQuality: null,
      projectAImportance: null,
      projectBQuality: null,
      projectBImportance: null,
      compareClicked: false,
    };
  },
  computed: {
    showCompareButton: function () {
      return (
        !this.compareClicked && (!this.incomingSearchA || !this.incomingSearchB)
      );
    },
    projectIdA: function () {
      if (!this.projectA) {
        return null;
      }
      return this.projectA.replace(/ /g, '_');
    },
    projectIdB: function () {
      if (!this.projectB) {
        return null;
      }
      return this.projectB.replace(/ /g, '_');
    },
    projectsSelected: function () {
      return !!this.projectA && !!this.projectB;
    },
  },
  watch: {
    $route: function (to) {
      if (to.path == '/compare') {
        this.reset();
      }
    },
    projectAQuality: function (quality) {
      if (this.showCompareButton) {
        return;
      }
      this.$router.push({
        path: `/compare/${this.projectA}/${this.projectB}`,
        query: {
          quality,
          importance: this.$route.query.importance,
          qualityB: this.$route.query.qualityB,
          importanceB: this.$route.query.importanceB,
          page: this.$route.query.page,
          numRows: this.$route.query.numRows,
          articlePattern: this.$route.query.articlePattern,
        },
      });
    },
    projectAImportance: function (importance) {
      if (this.showCompareButton) {
        return;
      }
      this.$router.push({
        path: `/compare/${this.projectA}/${this.projectB}`,
        query: {
          quality: this.$route.query.quality,
          importance,
          qualityB: this.$route.query.qualityB,
          importanceB: this.$route.query.importanceB,
          page: this.$route.query.page,
          numRows: this.$route.query.numRows,
          articlePattern: this.$route.query.articlePattern,
        },
      });
    },
    projectBQuality: function (qualityB) {
      if (this.showCompareButton) {
        return;
      }
      this.$router.push({
        path: `/compare/${this.projectA}/${this.projectB}`,
        query: {
          quality: this.$route.query.quality,
          importance: this.$route.query.importance,
          qualityB,
          importanceB: this.$route.query.importanceB,
          page: this.$route.query.page,
          numRows: this.$route.query.numRows,
          articlePattern: this.$route.query.articlePattern,
        },
      });
    },
    projectBImportance: function (importanceB) {
      if (this.showCompareButton) {
        return;
      }
      this.$router.push({
        path: `/compare/${this.projectA}/${this.projectB}`,
        query: {
          quality: this.$route.query.quality,
          importance: this.$route.query.importance,
          qualityB: this.$route.query.qualityB,
          importanceB,
          page: this.$route.query.page,
          numRows: this.$route.query.numRows,
          articlePattern: this.$route.query.articlePattern,
        },
      });
    },
  },
  methods: {
    onCompareClick: async function () {
      this.compareClicked = true;
      this.$router.push({
        path: `/compare/${this.projectA}/${this.projectB}`,
        query: {
          quality: this.projectAQuality,
          importance: this.projectAImportance,
          qualityB: this.projectBQuality,
          importanceB: this.projectBImportance,
        },
      });
    },
    onProjectARatingSelect: function (event) {
      this.projectAQuality = event.quality;
      this.projectAImportance = event.importance;
    },
    onProjectBRatingSelect: function (event) {
      this.projectBQuality = event.quality;
      this.projectBImportance = event.importance;
    },
    onPageSelect: function (selection) {
      this.$router.push({
        path: `/compare/${this.projectA}/${this.projectB}`,
        query: {
          quality: this.$route.query.quality,
          importance: this.$route.query.importance,
          qualityB: this.$route.query.qualityB,
          importanceB: this.$route.query.importanceB,
          page: selection.page,
          numRows: selection.rows,
          articlePattern: this.$route.query.articlePattern,
        },
      });
    },
    onNameFilter: function (selection) {
      this.$router.push({
        path: `/compare/${this.projectA}/${this.projectB}`,
        query: {
          quality: this.$route.query.quality,
          importance: this.$route.query.importance,
          qualityB: this.$route.query.qualityB,
          importanceB: this.$route.query.importanceB,
          page: this.$route.query.page,
          numRows: this.$route.query.numRows,
          articlePattern: selection,
        },
      });
    },
    onUpdatePage: function (page) {
      this.$router.push({
        path: `/compare/${this.projectA}/${this.projectB}`,
        query: {
          quality: this.$route.query.quality,
          importance: this.$route.query.importance,
          qualityB: this.$route.query.qualityB,
          importanceB: this.$route.query.importanceB,
          page: page.toString(),
          numRows: this.$route.query.numRows,
          articlePattern: this.$route.query.articlePattern,
        },
      });
    },
    reset: function () {
      this.projectA = null;
      this.projectB = null;
      this.projectAQuality = null;
      this.projectAImportance = null;
      this.projectBQuality = null;
      this.projectBImportance = null;
      this.compareClicked = false;
    },
  },
};
</script>

<style></style>
