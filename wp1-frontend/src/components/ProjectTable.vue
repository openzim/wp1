<template>
  <table>
    <tbody>
      <tr>
        <td>{{ tableData }}</td>
      </tr>
    </tbody>
  </table>
</template>

<script>
export default {
  name: 'projecttable',
  props: {
    projectId: String
  },
  data: function() {
    return {
      tableData: null
    };
  },
  watch: {
    projectId: async function(projectId) {
      if (!projectId) {
        this.tableData = null;
        return;
      }
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${projectId}/table`
      );
      const json = await response.json();
      this.tableData = json.table_data;
    }
  },
  methods: {}
};
</script>

<style scoped></style>
