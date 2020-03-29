<template>
  <div>
    <p
      v-if="articleData && articleData.pagination.total_pages > 1"
      class="pages-cont"
    >
      Pages:
      <span
        v-for="i in articleData.pagination.total_pages"
        :key="i"
        :class="
          'page-indicator' +
            (i === Number(page) || (i === 1 && !page) ? '' : ' link')
        "
        ><a v-on:click="updatePage(i)">{{ i }}</a></span
      >
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
</template>

<script>
export default {
  name: 'articletable',
  data: function() {
    return {
      articleData: null
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
  watch: {
    projectId: async function(projectId) {
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

      const response = await fetch(url);
      this.articleData = await response.json();
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
          page: page
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
  padding: 0.5rem;
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
</style>
