<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div class="container">
      <h1>Coming soon -- User Selections</h1>
    </div>
  </div>
  <div v-else>
    <LoginRequired></LoginRequired>
  </div>
</template>

<script>
import SecondaryNav from './SecondaryNav.vue';
import LoginRequired from './LoginRequired';

export default {
  components: { SecondaryNav, LoginRequired },
  name: 'MyLists'
};
</script>

<style scoped></style>
