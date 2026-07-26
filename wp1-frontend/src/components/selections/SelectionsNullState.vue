<template>
  <div class="flex flex-col gap-4 p-[22px]">
    <h1 class="m-0 text-xl font-semibold tracking-[-0.015em]">Selections</h1>
    <p v-if="signedOut" class="m-0 text-[13.5px] leading-[1.55] text-ink-2">
      Selections are lists of Wikipedia articles you can turn into an offline
      ZIM file. They're tied to your Wikipedia account, so sign in to see and
      create them.
    </p>
    <p v-else class="m-0 text-[13.5px] leading-[1.55] text-ink-2">
      You haven't created a selection yet. Selections are lists of Wikipedia
      articles you can turn into an offline ZIM file.
    </p>
    <div
      class="rounded-[5px] border border-border-strong bg-surface-muted p-3.5"
    >
      <div class="wp1r-microlabel mb-2.5">What you can build</div>
      <div class="grid gap-x-6 gap-y-2 sm:grid-cols-2">
        <div
          v-for="source in sources"
          :key="source.key"
          class="text-[13px] leading-[1.5] text-ink-2"
        >
          <span class="font-medium text-ink">{{ source.label }}</span>
          — {{ source.blurb }}
        </div>
      </div>
    </div>
    <div class="flex flex-wrap items-center gap-3.5">
      <a
        v-if="signedOut"
        :href="loginUrl"
        class="wp1r-btn-primary h-[34px] px-4"
        >Sign in with Wikipedia</a
      >
      <router-link
        v-else
        to="/selections/new"
        class="wp1r-btn-primary h-[34px] px-4"
        >New selection</router-link
      >
    </div>
  </div>
</template>

<script>
import { SOURCES } from '../../lib/selections.js';

export default {
  name: 'SelectionsNullState',
  props: {
    // 'signed-out' explains + offers login; 'empty' is the signed-in
    // zero-selections variant.
    mode: { type: String, default: 'signed-out' },
  },
  data: function () {
    return {
      sources: SOURCES,
    };
  },
  computed: {
    signedOut: function () {
      return this.mode === 'signed-out';
    },
    loginUrl: function () {
      return (
        `${import.meta.env.VITE_API_URL}/oauth/initiate?next=` +
        this.$route.path.toString().substr(1)
      );
    },
  },
};
</script>
