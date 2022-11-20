<template>
  <div>
    <h2 class="row justify-content-center pt-5">Please Log In To Continue</h2>
    <a class="row justify-content-center pt-2" :href="this.loginInitiateUrl"
      ><button type="button" class="btn btn-primary">Login</button></a
    >
  </div>
</template>

<script>
export default {
  name: 'LoginRequired',
  data: function () {
    return {
      loginInitiateUrl:
        `${import.meta.env.VITE_API_URL}/oauth/initiate?next=` +
        this.$route.path.toString().substr(1),
    };
  },
};
</script>
