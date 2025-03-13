<template>
  <div v-show="!!numProjects">
    There are currently {{ numProjects }} projects being tracked and updated
    each day.
  </div>
</template>

<script>
export default {
  name: 'stats',
  data: function () {
    return {
      numProjects: null,
    };
  },
  created: async function () {
    this.numProjects = await this.getProjectCount();
  },
  methods: {
    getProjectCount: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/count`
      );
      const data = await response.json();
      return data.count;
    },
  },
};
</script>

<style scoped></style>
