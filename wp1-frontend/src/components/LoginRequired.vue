<template>
  <div
    class="mx-auto flex w-full max-w-[560px] flex-col gap-4 px-6 pb-24 pt-20"
  >
    <div class="wp1r-microlabel">Wikipedia 1.0 Server</div>
    <h2 class="m-0 text-[20px] font-semibold tracking-[-0.015em]">
      Sign in required
    </h2>
    <p class="m-0 text-[14px] leading-[1.55] text-ink-2">
      This tool is tied to your Wikipedia account. Sign in to continue.
    </p>
    <div>
      <a :href="loginInitiateUrl" class="wp1r-btn-primary h-[34px] px-4"
        >Sign in with Wikipedia</a
      >
    </div>
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
