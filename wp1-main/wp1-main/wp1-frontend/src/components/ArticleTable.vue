<template>
  <div class="row">
    <div v-if="loading" class="col">
      <pulse-loader
        class="loader"
        :loading="loading"
        :color="loaderColor"
        :size="loaderSize"
      ></pulse-loader>
    </div>
    <div v-else-if="articleData" class="col">
      <ArticleTablePageSelect
        :numRows="articleData.pagination.display.num_rows"
        :startPage="page || '1'"
        v-on:page-select="onPageSelect($event)"
      ></ArticleTablePageSelect>
      <ArticleTableRatingSelect
        v-if="!hideRatingSelect"
        :initialQuality="quality"
        :initialImportance="importance"
        :projectId="projectId"
        v-on:rating-select="onRatingSelect($event)"
      ></ArticleTableRatingSelect>
      <ArticleTableNameFilter
        :filterValue="articlePattern"
        v-on:name-filter="onNameFilter($event)"
      ></ArticleTableNameFilter>
      <div v-if="tableData.length > 0" class="my-0 row">
        <p class="pages-cont">
          Article {{ articleData.pagination.display.start }} -
          {{ articleData.pagination.display.end }} of
          {{ articleData.pagination.total }} ({{
            articleData.pagination.total_pages
          }}
          page<span v-if="articleData.pagination.total_pages !== 1">s</span>)
        </p>
      </div>
      <ArticleTablePagination
        v-if="articleData && articleData.pagination.total_pages > 1"
        class="row justify-content-between my-0"
        v-on:update-page="onUpdatePage($event)"
        :page="page"
        :totalPages="articleData.pagination.total_pages"
      >
      </ArticleTablePagination>

      <hr class="mt-0" />

      <table v-if="!projectIdB">
        <tr v-for="(row, index) in tableData" :key="index">
          <td>{{ articleData.pagination.display.start + index }}</td>
          <td>
            <a :href="row.article_link">{{ row.article }}</a> (
            <a :href="row.article_talk_link">t</a> ·
            <a :href="row.article_history_link">h</a> )
          </td>
          <td :class="classLabel(row.importance)">
            {{ classLabel(row.importance) }}
          </td>
          <td>
            <a :href="timestampLink(row.article, row.importance_updated)">{{
              formatTimestamp(row.importance_updated)
            }}</a>
            (
            <a :href="timestampLink(row.article_talk, row.importance_updated)"
              >t</a
            >
            )
          </td>
          <td :class="classLabel(row.quality)">
            {{ classLabel(row.quality) }}
          </td>
          <td>
            <a :href="timestampLink(row.article, row.quality_updated)">{{
              formatTimestamp(row.quality_updated)
            }}</a>
            (
            <a :href="timestampLink(row.article_talk, row.quality_updated)"
              >t</a
            >
            )
          </td>
        </tr>
      </table>

      <table v-else-if="tableData.length">
        <tr>
          <th colspan="2"></th>
          <th colspan="2">{{ projectId.replace(/_/g, ' ') }}</th>
          <th></th>
          <th colspan="2">{{ projectIdB.replace(/_/g, ' ') }}</th>
        </tr>

        <tr v-for="(row, index) in tableData" :key="index">
          <td>{{ articleData.pagination.display.start + index }}</td>
          <td>
            <a :href="row[0].article_link">{{ row[0].article }}</a> (
            <a :href="row[0].article_talk_link">t</a> ·
            <a :href="row[0].article_history_link">h</a> )
          </td>
          <td :class="classLabel(row[0].importance)">
            {{ classLabel(row[0].importance) }}
          </td>
          <td :class="classLabel(row[0].quality)">
            {{ classLabel(row[0].quality) }}
          </td>
          <td class="spacer"></td>
          <td :class="classLabel(row[1].importance)">
            {{ classLabel(row[1].importance) }}
          </td>
          <td :class="classLabel(row[1].quality)">
            {{ classLabel(row[1].quality) }}
          </td>
        </tr>
      </table>

      <div v-if="tableData.length > 0" class="my-0 row">
        <p class="pages-cont">
          Article {{ articleData.pagination.display.start }} -
          {{ articleData.pagination.display.end }} of
          {{ articleData.pagination.total }}
        </p>
      </div>
      <ArticleTablePagination
        v-if="articleData && articleData.pagination.total_pages > 1"
        class="row justify-content-between mb-5 mt-0"
        v-on:update-page="onUpdatePage($event)"
        :page="page"
        :totalPages="articleData.pagination.total_pages"
      >
      </ArticleTablePagination>

      <h2 v-if="!tableData.length">No results to display</h2>
    </div>
  </div>
</template>

<script>
import ArticleTablePagination from './ArticleTablePagination.vue';
import ArticleTablePageSelect from './ArticleTablePageSelect.vue';
import ArticleTableRatingSelect from './ArticleTableRatingSelect.vue';
import ArticleTableNameFilter from './ArticleTableNameFilter.vue';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';

export default {
  name: 'article-table',
  components: {
    ArticleTablePagination,
    ArticleTablePageSelect,
    ArticleTableRatingSelect,
    ArticleTableNameFilter,
    PulseLoader,
  },
  data: function () {
    return {
      articleData: null,
      categoryLinks: {},
      loading: false,
      loaderColor: '#007bff',
      loaderSize: '1rem',
    };
  },
  props: [
    'projectId',
    'projectIdB',
    'importance',
    'quality',
    'importanceB',
    'qualityB',
    'page',
    'numRows',
    'articlePattern',
    'hideRatingSelect',
  ],
  computed: {
    tableData: function () {
      if (this.articleData === null) {
        return [];
      }
      return this.articleData['articles'];
    },
  },
  created: function () {
    this.updateTable();
  },
  watch: {
    projectId: async function (projectId) {
      if (!projectId) {
        this.articleData = null;
        return;
      }
      await this.updateTable();
    },
    projectIdB: async function () {
      await this.updateTable();
    },
    importance: async function () {
      await this.updateTable();
    },
    quality: async function () {
      await this.updateTable();
    },
    importanceB: async function () {
      await this.updateTable();
    },
    qualityB: async function () {
      await this.updateTable();
    },
    page: async function () {
      await this.updateTable();
    },
    numRows: async function () {
      await this.updateTable();
    },
    articlePattern: async function () {
      await this.updateTable();
    },
  },
  methods: {
    onPageSelect: function (selection) {
      this.$emit('page-select', selection);
    },
    onRatingSelect: function (selection) {
      this.$emit('rating-select', selection);
    },
    onNameFilter: function (selection) {
      this.$emit('name-filter', selection);
    },
    onUpdatePage: function (page) {
      this.$emit('update-page', page);
    },
    classLabel: function (qualOrImp) {
      if (!this.categoryLinks[qualOrImp]) {
        return '';
      }
      return (
        this.categoryLinks[qualOrImp].text || this.categoryLinks[qualOrImp]
      );
    },
    getCategoryLinks: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${
          this.projectId
        }/category_links`
      );
      this.categoryLinks = await response.json();
    },
    updateTable: async function () {
      const url = new URL(
        `${import.meta.env.VITE_API_URL}/projects/${this.projectId}/articles`
      );
      const params = {};
      if (this.importance) {
        params.importance = this.importance;
      }
      if (this.quality) {
        params.quality = this.quality;
      }
      if (this.projectIdB) {
        params.projectB = this.projectIdB;
      }
      if (this.importanceB) {
        params.importanceB = this.importanceB;
      }
      if (this.qualityB) {
        params.qualityB = this.qualityB;
      }
      if (this.page) {
        params.page = this.page;
      }
      if (this.numRows) {
        params.numRows = this.numRows;
      }
      if (this.articlePattern) {
        params.articlePattern = this.articlePattern;
      }
      Object.keys(params).forEach((key) =>
        url.searchParams.append(key, params[key])
      );

      let finishedRequest = false;
      setTimeout(() => {
        if (!finishedRequest) {
          this.loading = true;
        }
      }, 100);
      const response = await fetch(url);
      finishedRequest = true;
      if (response.ok) {
        this.articleData = await response.json();
      } else {
        this.articleData = null;
      }
      this.loading = false;
      await this.getCategoryLinks();
    },
    formatTimestamp: function (ts) {
      return ts.split('T')[0];
    },
    timestampLink: function (articleName, ts) {
      return `${import.meta.env.VITE_API_URL}/articles/${encodeURIComponent(
        articleName
      )}/${encodeURIComponent(ts)}/redirect`;
    },
  },
};
</script>

<style scoped>
@import '../labels.scss';

h2 {
  text-align: center;
}

table {
  border-collapse: collapse;
  border: 1px solid #aaa;
  margin: 1rem auto;
}

td {
  border: 1px solid #aaa;
  padding: 0 0.5rem;
}

.spacer {
  width: 1rem;
}

tr:nth-child(even) {
  background: lightyellow;
}

.pages-cont {
  margin: auto;
  text-align: center;
}

.loader {
  margin: auto;
  text-align: center;
}
</style>
