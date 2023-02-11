<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
  </div>
  <div v-else>
    <LoginRequired></LoginRequired>
  </div>
</template>

<script>
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';

import SecondaryNav from './SecondaryNav.vue';
import LoginRequired from './LoginRequired.vue';

export default {
  name: 'CreateZimFile',
  components: { SecondaryNav, LoginRequired, PulseLoader },
  data: function () {
    return {};
  },
  created: function () {
    this.getBuilder();
  },
  methods: {
    getBuilder: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${this.builderId}`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }
      );
      if (response.status == 404) {
        this.notFound = true;
      } else if (!response.ok) {
        this.serverError = true;
      } else {
        this.notFound = false;
        this.builder = await response.json();
        this.$emit('onBuilderLoaded', this.builder);
      }
    },
  },
  computed: {
    isLoggedIn: function () {
      return this.$root.$data.isLoggedIn;
    },
    builderId: function () {
      return this.$route.params.builder_id;
    },
  },
  watch: {
    builderId: function () {
      this.getBuilder();
    },
  },
};
</script>

<style scoped></style>
