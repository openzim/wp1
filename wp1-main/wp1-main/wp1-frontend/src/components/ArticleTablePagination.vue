<template>
  <div>
    <p class="prev-page col-3 m-0">
      <span :class="page === '1' || !page ? '' : ' link'"
        ><a v-on:click="previousPage()">previous page</a></span
      >
    </p>
    <p class="pages-cont col-6">
      <span v-if="totalPages > 1">
        <span
          v-for="i in getPageDisplay()"
          :key="i"
          :class="
            'page-indicator' +
              (i === Number(page) || (i === 1 && !page) ? '' : ' link')
          "
          ><a v-on:click="updatePage(i)">{{ i }}</a></span
        >
      </span>
    </p>
    <p class="next-page col-3 m-0">
      <span :class="Number(page) === totalPages ? '' : ' link'"
        ><a v-on:click="nextPage()">next page</a></span
      >
    </p>
  </div>
</template>

<script>
export default {
  name: 'article-table-pagination',
  components: {},
  props: {
    page: String,
    totalPages: Number
  },
  methods: {
    getPageDisplay: function() {
      const display = [];
      const page = Number(this.page || 1);
      const bottom = Math.max(1, page - 5);
      const top = Math.min(page + 5, this.totalPages);
      for (let i = bottom; i <= top; i++) {
        display.push(i);
      }
      return display;
    },
    nextPage: function() {
      if (Number(this.page) === this.totalPages) {
        return;
      }
      if (this.page) {
        this.updatePage(Number(this.page) + 1);
      } else {
        this.updatePage(2);
      }
    },
    previousPage: function() {
      if (!this.page) {
        return;
      }
      this.updatePage(Number(this.page) - 1);
    },
    updatePage: function(page) {
      if (page === Number(this.page)) {
        return;
      }

      this.$emit('update-page', page);
    }
  }
};
</script>

<style scoped>
.pages-cont {
  margin: auto;
  text-align: center;
}

.page-indicator {
  display: inline-block;
  padding: 0 0.25rem;
  width: 1.5rem;
}

.next-page .link,
.prev-page .link,
.page-indicator.link {
  color: #007bff;
  cursor: pointer;
}

.next-page {
  text-align: right;
}
</style>
