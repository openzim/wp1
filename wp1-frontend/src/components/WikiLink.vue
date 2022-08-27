<template>
  <a :href="href">{{ text }}</a>
</template>

<script>
export default {
  name: 'wiki-link',
  props: {
    href: String,
    text: String
  }
};
</script>

<style scoped></style>
