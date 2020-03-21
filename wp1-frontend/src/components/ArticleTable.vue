<template>
  <div>
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
      tableData: null
    };
  },
  props: {
    projectId: String,
    importance: String,
    quality: String
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
      Object.keys(params).forEach(key =>
        url.searchParams.append(key, params[key])
      );

      const response = await fetch(url);
      this.tableData = await response.json();
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
</style>
