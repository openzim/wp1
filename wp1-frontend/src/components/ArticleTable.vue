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
      <div class="my-0 row">
        <p class="pages-cont">
          Article {{ articleData.pagination.display.start }} -
          {{ articleData.pagination.display.end }} of
          {{ articleData.pagination.total }} ({{
            articleData.pagination.total_pages
          }}
          pages)
        </p>
      </div>
      <ArticleTablePagination
        v-if="articleData.pagination.total_pages > 1"
        class="row justify-content-between my-0"
        v-on:update-page="onUpdatePage($event)"
        :page="page"
        :totalPages="articleData.pagination.total_pages"
      >
      </ArticleTablePagination>

      <hr class="mt-0" />

      <table>
        <tr v-for="(row, index) in tableData" :key="row.article">
          <td>{{ articleData.pagination.display.start + index }}</td>
          <td>
            <a :href="row.article_link">{{ row.article }}</a> (
            <a :href="row.article_talk_link">t</a> ·
            <a :href="row.article_history_link">h</a> )
          </td>
          <td :class="row.importance">{{ row.importance }}</td>
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
          <td :class="row.quality">{{ row.quality }}</td>
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

      <div class="my-0 row">
        <p class="pages-cont">
          Article {{ articleData.pagination.display.start }} -
          {{ articleData.pagination.display.end }} of
          {{ articleData.pagination.total }}
        </p>
      </div>
      <ArticleTablePagination
        v-if="articleData.pagination.total_pages > 1"
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
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';

export default {
  name: 'articletable',
  components: {
    ArticleTablePagination,
    ArticleTablePageSelect,
    PulseLoader
  },
  data: function() {
    return {
      articleData: null,
      loading: false,
      loaderColor: '#007bff',
      loaderSize: '1rem'
    };
  },
  props: {
    projectId: String,
    importance: String,
    quality: String,
    page: String
  },
  computed: {
    tableData: function() {
      if (this.articleData === null) {
        return [];
      }
      return this.articleData['articles'];
    }
  },
  created: function() {
    this.updateTable();
  },
  watch: {
    projectId: async function(projectId) {
      window.console.log('watching projectId:', projectId);
      if (!projectId) {
        this.tableData = null;
        return;
      }
      await this.updateTable();
    },
    importance: async function() {
      await this.updateTable();
    },
    quality: async function() {
      await this.updateTable();
    },
    page: async function() {
      await this.updateTable();
    }
  },
  methods: {
    onPageSelect: function(selection) {
      const projectName = this.projectId.replace(/_/g, ' ');
      this.$router.push({
        path: `/project/${projectName}/articles`,
        query: {
          quality: this.quality,
          importance: this.importance,
          page: selection.startPage,
          numRows: selection.numRows
        }
      });
    },
    onUpdatePage: function(page) {
      const projectName = this.projectId.replace(/_/g, ' ');
      this.$router.push({
        path: `/project/${projectName}/articles`,
        query: {
          quality: this.quality,
          importance: this.importance,
          page: page.toString()
        }
      });
    },
    updateTable: async function() {
      const url = new URL(
        `${process.env.VUE_APP_API_URL}/projects/${this.projectId}/articles`
      );
      const params = {};
      if (this.importance) {
        params.importance = this.importance;
      }
      if (this.quality) {
        params.quality = this.quality;
      }
      if (this.page) {
        params.page = this.page;
      }
      Object.keys(params).forEach(key =>
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
    },
    formatTimestamp: function(ts) {
      return ts.split('T')[0];
    },
    timestampLink: function(articleName, ts) {
      return `${process.env.VUE_APP_API_URL}/articles/${encodeURIComponent(
        articleName
      )}/${encodeURIComponent(ts)}/redirect`;
    }
  }
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
