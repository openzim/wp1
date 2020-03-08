<template>
  <a :href="href">{{ text }}</a>
</template>

<script>
export default {
  name: 'wikilink',
  props: {
    href: String,
    text: String
  }
};
</script>

<style scoped></style>
