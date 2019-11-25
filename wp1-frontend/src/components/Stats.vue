<template>
  <div>
    There are currently {{numProjects}} projects being tracked and updated each
    day.
  </div>
</template>

<script>

export default {
  name: 'stats',
  data: function() {
    return {
      'numProjects': 2497
    }
  },
}
</script>

<style scoped>

</style>
