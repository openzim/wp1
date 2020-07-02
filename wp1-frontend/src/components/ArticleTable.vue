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
      <div class="my-0 row">
        <p class="pages-cont">
          Article {{ articleData.pagination.display.start }} -
          {{ articleData.pagination.display.end }} of
          {{ articleData.pagination.total }}
        </p>
      </div>
      <div
        v-if="articleData.pagination.total_pages > 1"
        class="row justify-content-between my-0"
      >
        <p class="prev-page col-3 m-0">
          <span :class="page === '1' || !page ? '' : ' link'"
            ><a v-on:click="previousPage()">previous page</a></span
          >
        </p>
        <p class="pages-cont col-6">
          <span v-if="articleData.pagination.total_pages > 1">
            <span
              v-for="i in getPageDisplay()"
              :key="i"
              :class="
                'page-indicator' +
                  (i === Number(page) || (i === 1 && !page) ? '' : ' link')
              "
              ><a v-on:click="updatePage(i)">{{ i }}</a></span
            >
          </span>
        </p>
        <p class="next-page col-3 m-0">
          <span
            :class="
              Number(page) === articleData.pagination.total_pages ? '' : ' link'
            "
            ><a v-on:click="nextPage()">next page</a></span
          >
        </p>
      </div>

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

      <h2 v-if="!tableData.length">No results to display</h2>
    </div>
  </div>
</template>

<script>
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';

export default {
  name: 'articletable',
  components: {
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
    getPageDisplay: function() {
      const display = [];
      const page = Number(this.page);
      const bottom = Math.max(1, page - 5);
      const top = Math.min(page + 5, this.articleData.pagination.total_pages);
      for (let i = bottom; i <= top; i++) {
        display.push(i);
      }
      return display;
    },
    nextPage: function() {
      if (Number(this.page) === this.articleData.pagination.total_pages) {
        return;
      }
      if (this.page) {
        this.updatePage(Number(this.page) + 1);
      } else {
        this.updatePage(2);
      }
    },
    previousPage: function() {
      if (!this.page) {
        return;
      }
      this.updatePage(Number(this.page) - 1);
    },
    updatePage: function(page) {
      if (page === Number(this.page)) {
        return;
      }

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

.page-indicator {
  display: inline-block;
  padding: 0 0.25rem;
  width: 1.5rem;
}

.next-page .link,
.prev-page .link,
.page-indicator.link {
  color: #007bff;
  cursor: pointer;
}

.next-page {
  text-align: right;
}

.loader {
  margin: auto;
  text-align: center;
}
</style>
