<template>
  <div class="mt-4">
    <!-- Mobile: the bar collapses behind a disclosure button. -->
    <button
      type="button"
      class="wp1r-btn-secondary h-9 w-full justify-between px-3 md:hidden"
      :aria-expanded="open ? 'true' : 'false'"
      v-on:click="open = !open"
    >
      <span>Filters</span>
      <span class="font-mono text-[11px] text-ink-3"
        >{{ activeCount }} active {{ open ? '▴' : '▾' }}</span
      >
    </button>
    <div
      class="rounded border border-border bg-surface-muted px-3 py-2.5 max-md:mt-2"
      :class="{ 'max-md:hidden': !open }"
    >
      <div class="flex flex-wrap items-center gap-x-4 gap-y-2">
        <span
          v-if="!hideRatingSelect"
          class="flex items-center gap-1.5 max-md:w-full"
        >
          <label class="wp1r-microlabel" for="qualitySelect">Quality</label>
          <select
            id="qualitySelect"
            class="wp1r-select h-7 pl-2 max-md:flex-1"
            v-model="quality"
            v-on:keyup.enter="onUpdateClick()"
          >
            <option
              v-for="(item, key) in categoryLinks.quality"
              :value="key"
              v-bind:key="key"
            >
              {{ item.text ? item.text : item }}
            </option>
          </select>
        </span>
        <span
          v-if="!hideRatingSelect"
          class="flex items-center gap-1.5 max-md:w-full"
        >
          <label class="wp1r-microlabel" for="importanceSelect"
            >Importance</label
          >
          <select
            id="importanceSelect"
            class="wp1r-select h-7 pl-2 max-md:flex-1"
            v-model="importance"
            v-on:keyup.enter="onUpdateClick()"
          >
            <option
              v-for="(item, key) in categoryLinks.importance"
              :value="key"
              v-bind:key="key"
            >
              {{ item.text ? item.text : item }}
            </option>
          </select>
        </span>
        <span class="flex items-center gap-1.5 max-md:w-full">
          <label class="wp1r-microlabel" for="updateName">Name contains</label>
          <input
            id="updateName"
            class="wp1r-input h-7 w-40 max-md:flex-1"
            v-model="pattern"
            v-on:keyup.enter="onUpdateClick()"
          />
        </span>
        <span class="flex items-center gap-1.5">
          <label class="wp1r-microlabel" for="row-input">Show</label>
          <input
            id="row-input"
            class="wp1r-input h-7 w-14 text-center"
            :class="{ '!border-danger ring-1 ring-danger-border': errorRows }"
            v-model="rows"
            v-on:keyup.enter="onUpdateClick()"
          />
          <label class="wp1r-microlabel" for="page-input">rows · page</label>
          <input
            id="page-input"
            class="wp1r-input h-7 w-12 text-center"
            :class="{ '!border-danger ring-1 ring-danger-border': errorPage }"
            v-model="page"
            v-on:keyup.enter="onUpdateClick()"
          />
        </span>
        <button
          type="button"
          id="updateRating"
          class="wp1r-btn-primary h-7 px-3"
          v-on:click="onUpdateClick()"
        >
          Update view
        </button>
        <button
          v-if="!hideRatingSelect"
          type="button"
          id="randomArticle"
          class="wp1r-btn-secondary h-7 px-2.5"
          title="Open a random article matching these filters"
          v-on:click="onRandomClick()"
        >
          Random
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'article-filter-bar',
  props: {
    projectId: String,
    initialQuality: String,
    initialImportance: String,
    initialPattern: String,
    numRows: Number,
    startPage: String,
    // Compare mode: no per-project rating filters or random button here.
    hideRatingSelect: Boolean,
  },
  data: function () {
    return {
      categoryLinks: {},
      quality: this.initialQuality || '',
      importance: this.initialImportance || '',
      pattern: this.initialPattern || '',
      rows: this.numRows,
      page: this.startPage || '1',
      open: false,
    };
  },
  created: function () {
    this.getCategoryLinks();
  },
  computed: {
    errorRows: function () {
      return (
        this.rows === '' || isNaN(this.rows) || this.rows > 500 || this.rows < 0
      );
    },
    errorPage: function () {
      return isNaN(this.page) || this.page < 1;
    },
    activeCount: function () {
      let count = 0;
      if (this.quality) {
        count++;
      }
      if (this.importance) {
        count++;
      }
      if (this.pattern) {
        count++;
      }
      if (Number(this.rows) !== 100) {
        count++;
      }
      if (Number(this.page) > 1) {
        count++;
      }
      return count;
    },
  },
  watch: {
    projectId: async function () {
      await this.getCategoryLinks();
    },
    $route: function (to) {
      this.quality = to.query.quality || '';
      this.importance = to.query.importance || '';
      this.pattern = to.query.articlePattern || '';
      this.rows = to.query.numRows || 100;
      this.page = to.query.page || '1';
    },
  },
  methods: {
    getCategoryLinks: async function () {
      if (!this.projectId || this.hideRatingSelect) {
        return;
      }
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${
          this.projectId
        }/category_links/sorted`
      );
      const links = await response.json();
      links.quality[''] = 'None Selected';
      links.importance[''] = 'None Selected';
      this.categoryLinks = links;
    },
    // The single commit: pushes every field to the query at once. Invalid
    // pagination fields block it (they carry a danger ring already).
    onUpdateClick: function () {
      if (this.errorRows || this.errorPage) {
        return;
      }
      this.$emit('update-filters', {
        quality: this.quality,
        importance: this.importance,
        articlePattern: this.pattern,
        rows: this.rows,
        page: this.page,
      });
    },
    onRandomClick: async function () {
      const url = new URL(
        `${import.meta.env.VITE_API_URL}/projects/${
          this.projectId
        }/articles/random`
      );
      if (this.quality) {
        url.searchParams.set('quality', this.quality);
      }
      if (this.importance) {
        url.searchParams.set('importance', this.importance);
      }

      const response = await fetch(url);
      if (response.status === 204) {
        return;
      }
      const data = await response.json();

      window.open(data);
    },
  },
};
</script>
