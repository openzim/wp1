<template>
  <div class="wp1r flex flex-1 flex-col bg-page">
    <div
      class="mx-auto flex w-full max-w-[1200px] flex-1 flex-col border-x border-border bg-surface"
    >
      <div class="px-[18px] pb-16 pt-6 max-md:px-3">
        <h2 class="m-0 text-[19px] font-semibold tracking-[-0.015em]">
          Compare projects
        </h2>
        <p
          class="mb-4 mt-1 max-w-[640px] text-[13.5px] leading-[1.55] text-ink-2"
        >
          Select two projects to compare the articles that are in both, with
          optional quality and importance filters for each.
        </p>
        <div class="grid gap-3 md:grid-cols-2">
          <div class="rounded border border-border bg-surface-muted p-3">
            <div class="wp1r-microlabel mb-2">Project A</div>
            <Autocomplete
              buttonLabel="Select"
              buttonVariant="secondary"
              :incomingSearch="incomingSearchA"
              v-on:select-project="projectA = $event"
            ></Autocomplete>
            <RatingSelect
              class="mt-2.5"
              :projectId="projectIdA"
              :initialQuality="$route.query.quality"
              :initialImportance="$route.query.importance"
              v-on:rating-select="onProjectARatingSelect($event)"
            ></RatingSelect>
          </div>
          <div class="rounded border border-border bg-surface-muted p-3">
            <div class="wp1r-microlabel mb-2">Project B</div>
            <Autocomplete
              buttonLabel="Select"
              buttonVariant="secondary"
              :incomingSearch="incomingSearchB"
              v-on:select-project="projectB = $event"
            ></Autocomplete>
            <RatingSelect
              class="mt-2.5"
              :projectId="projectIdB"
              :initialQuality="$route.query.qualityB"
              :initialImportance="$route.query.importanceB"
              v-on:rating-select="onProjectBRatingSelect($event)"
            ></RatingSelect>
          </div>
        </div>
        <button
          v-if="showCompareButton"
          type="button"
          class="wp1r-btn-primary mt-3 h-8 px-4"
          :disabled="!projectsSelected"
          v-on:click="onCompareClick()"
        >
          Compare
        </button>
        <ArticleTable
          v-if="projectsSelected && !showCompareButton"
          class="mt-3"
          :projectId="projectIdA"
          :projectIdB="projectIdB"
          :quality="$route.query.quality"
          :importance="$route.query.importance"
          :qualityB="$route.query.qualityB"
          :importanceB="$route.query.importanceB"
          :page="$route.query.page"
          :numRows="$route.query.numRows"
          :articlePattern="$route.query.articlePattern"
          :hideRatingSelect="true"
          v-on:update-filters="onUpdateFilters($event)"
          v-on:update-page="onUpdatePage($event)"
        ></ArticleTable>
      </div>
    </div>
  </div>
</template>

<script>
import ArticleTable from './ArticleTable.vue';
import Autocomplete from './Autocomplete.vue';
import RatingSelect from './RatingSelect.vue';

export default {
  name: 'compare-page',
  components: {
    ArticleTable,
    Autocomplete,
    RatingSelect,
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
    // The compare-mode filter bar commits the name filter and pagination in
    // one push (there are no shared rating filters in compare mode).
    onUpdateFilters: function (selection) {
      this.$router.push({
        path: `/compare/${this.projectA}/${this.projectB}`,
        query: {
          quality: this.$route.query.quality,
          importance: this.$route.query.importance,
          qualityB: this.$route.query.qualityB,
          importanceB: this.$route.query.importanceB,
          page: String(selection.page) === '1' ? undefined : selection.page,
          numRows:
            String(selection.rows) === '100' ? undefined : selection.rows,
          articlePattern: selection.articlePattern || undefined,
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
