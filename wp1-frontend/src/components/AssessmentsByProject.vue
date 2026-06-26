<template>
  <div class="container">
    <div class="row p-4">
      <div class="col-lg-10">
        <p>
          The number of assessed and unassessed articles in each WikiProject,
          ordered by the number of unassessed articles.
        </p>
        <pulse-loader
          class="loader"
          :loading="loading"
          :color="loaderColor"
          :size="loaderSize"
        ></pulse-loader>
        <table v-if="!loading" id="assessments-table">
          <thead>
            <tr>
              <th>Project</th>
              <th>Unassessed</th>
              <th>Assessed</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in assessments" :key="row[0]">
              <td>
                <router-link :to="`/project/${displayName(row[0])}`">{{
                  displayName(row[0])
                }}</router-link>
              </td>
              <td class="num" :data-order="row[1]">
                {{ row[1].toLocaleString() }}
              </td>
              <td class="num" :data-order="row[2]">
                {{ row[2].toLocaleString() }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import $ from 'jquery';
$.noConflict();

import PulseLoader from 'vue-spinner/src/PulseLoader.vue';

export default {
  name: 'assessments-by-project',
  components: {
    PulseLoader,
  },
  data: function () {
    return {
      assessments: [],
      loading: false,
      loaderColor: '#007bff',
      loaderSize: '1rem',
    };
  },
  methods: {
    displayName: function (name) {
      return name.replace(/_/g, ' ');
    },
  },
  created: async function () {
    this.loading = true;
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/assessments`
      );
      this.assessments = await response.json();
    } catch (err) {
      console.error(err);
    }
    this.loading = false;
    this.$nextTick(function () {
      $('#assessments-table').DataTable({
        // Default sort matches the API: most unassessed articles first.
        order: [[1, 'desc']],
        iDisplayLength: 25,
      });
    });
  },
};
</script>

<style scoped>
.loader {
  margin: auto;
  text-align: center;
}

.num {
  text-align: right;
}
</style>
