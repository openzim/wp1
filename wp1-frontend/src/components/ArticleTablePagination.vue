<template>
  <div class="flex items-center gap-1.5">
    <button
      type="button"
      class="wp1r-btn-secondary h-9 px-3 md:h-7 md:px-2.5"
      :disabled="currentPage === 1"
      v-on:click="previousPage()"
    >
      ← Prev
    </button>
    <span class="hidden items-center gap-1.5 md:flex">
      <button
        v-for="i in getPageDisplay()"
        :key="i"
        type="button"
        class="h-7 min-w-7 px-2"
        :class="
          i === currentPage
            ? 'wp1r-btn border-ink bg-ink text-white'
            : 'wp1r-btn-secondary'
        "
        v-on:click="updatePage(i)"
      >
        {{ i }}
      </button>
    </span>
    <span class="px-1 font-mono text-[12px] text-ink-3 md:hidden"
      >{{ currentPage }} / {{ totalPages }}</span
    >
    <button
      type="button"
      class="wp1r-btn-secondary h-9 px-3 md:h-7 md:px-2.5"
      :disabled="currentPage === totalPages"
      v-on:click="nextPage()"
    >
      Next →
    </button>
  </div>
</template>

<script>
export default {
  name: 'article-table-pagination',
  props: {
    page: String,
    totalPages: Number,
  },
  computed: {
    currentPage: function () {
      return Number(this.page || 1);
    },
  },
  methods: {
    getPageDisplay: function () {
      const display = [];
      const page = this.currentPage;
      const bottom = Math.max(1, page - 5);
      const top = Math.min(page + 5, this.totalPages);
      for (let i = bottom; i <= top; i++) {
        display.push(i);
      }
      return display;
    },
    nextPage: function () {
      if (this.currentPage === this.totalPages) {
        return;
      }
      this.updatePage(this.currentPage + 1);
    },
    previousPage: function () {
      if (this.currentPage === 1) {
        return;
      }
      this.updatePage(this.currentPage - 1);
    },
    updatePage: function (page) {
      if (page === this.currentPage) {
        return;
      }

      this.$emit('update-page', page);
    },
  },
};
</script>
