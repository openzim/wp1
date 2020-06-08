<template>
  <div>
    <div v-if="loading">
      <pulse-loader
        class="loader"
        :loading="loading"
        :color="loaderColor"
        :size="loaderSize"
      ></pulse-loader>
    </div>
    <div v-else>
      <p v-if="articleData" class="pages-cont">
        {{ articleData.pagination.total }} articles

        <span v-if="articleData.pagination.total_pages > 1">
          - Pages:
          <span
            v-for="i in Math.min(articleData.pagination.total_pages, 15)"
            :key="i"
            :class="
              'page-indicator' +
                (i === Number(page) || (i === 1 && !page) ? '' : ' link')
            "
            ><a v-on:click="updatePage(i)">{{ i }}</a></span
          >
          <span v-if="articleData.pagination.total_pages > 15">
            ...(more results truncated)
          </span>
        </span>
      </p>

      <hr />

      <table>
        <tr v-for="row in tableData" :key="row.article">
          <td>
            <a :href="row.article_link">{{ row.article }}</a>
          </td>
          <td :class="row.importance">{{ row.importance }}</td>
          <td>{{ row.importance_updated }}</td>
          <td :class="row.quality">{{ row.quality }}</td>
          <td>{{ row.quality_updated }}</td>
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
    updatePage: function(page) {
      if (page === this.page) {
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
}

.page-indicator.link {
  color: #007bff;
  cursor: pointer;
}

.loader {
  margin: auto;
  text-align: center;
}
</style>
