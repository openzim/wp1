<template>
  <div class="wp1r flex flex-1 flex-col bg-page">
    <div
      class="mx-auto flex w-full max-w-[1200px] flex-1 flex-col border-x border-border bg-surface"
    >
      <div class="px-[18px] pb-16 pt-6 max-md:px-3">
        <h2 class="m-0 text-[19px] font-semibold tracking-[-0.015em]">
          Assessments by project
        </h2>
        <p
          class="mb-4 mt-1 max-w-[640px] text-[13.5px] leading-[1.55] text-ink-2"
        >
          The number of assessed and unassessed articles in each WikiProject,
          ordered by the number of unassessed articles.
        </p>
        <pulse-loader
          class="mt-6 text-center"
          :loading="loading"
          :color="loaderColor"
          :size="loaderSize"
        ></pulse-loader>
        <template v-if="!loading">
          <div class="flex items-center justify-between gap-3">
            <label
              class="flex h-[30px] w-[280px] max-w-full cursor-text items-center gap-1.5 rounded border border-border px-2 focus-within:border-accent"
            >
              <span aria-hidden="true" class="font-mono text-xs text-ink-4"
                >/</span
              >
              <input
                ref="search"
                v-model="query"
                type="text"
                placeholder="Filter projects…"
                aria-label="Filter projects"
                class="w-full border-0 bg-transparent p-0 text-[13px] outline-none focus:!outline-none"
              />
            </label>
            <span class="font-mono text-[12px] text-ink-3"
              >{{ assessments.length.toLocaleString() }} projects</span
            >
          </div>
          <div class="mt-2 overflow-hidden rounded border border-border">
            <table
              id="assessments-table"
              class="w-full border-collapse text-[13px]"
            >
              <thead>
                <tr
                  class="border-b border-border-strong bg-surface-muted text-left"
                >
                  <th
                    v-for="(col, index) in columns"
                    :key="col.label"
                    class="p-0"
                    :class="{ 'text-right': index > 0 }"
                    :aria-sort="ariaSort(index)"
                  >
                    <button
                      type="button"
                      class="group w-full cursor-pointer border-0 bg-transparent px-3 py-[8px] text-left hover:bg-border-row"
                      :class="{ 'text-right': index > 0 }"
                      v-on:click="sortBy(index)"
                    >
                      <span
                        class="wp1r-microlabel !text-[11px]"
                        :class="{ '!text-ink': sortColumn === index }"
                        >{{ col.label }}</span
                      >
                      <span
                        v-if="sortColumn === index"
                        class="text-ink"
                        aria-hidden="true"
                        >{{ sortDescending ? '↓' : '↑' }}</span
                      >
                      <span
                        v-else
                        class="invisible text-ink-4 group-hover:visible"
                        aria-hidden="true"
                        >↕</span
                      >
                    </button>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="row in pageRows"
                  :key="row[0]"
                  class="border-b border-border-row last:border-b-0 hover:bg-surface-muted"
                >
                  <td class="px-3 py-[7px]">
                    <router-link :to="`/project/${displayName(row[0])}`">{{
                      displayName(row[0])
                    }}</router-link>
                  </td>
                  <td class="px-3 py-[7px] text-right font-mono text-[12.5px]">
                    {{ row[1].toLocaleString() }}
                  </td>
                  <td class="px-3 py-[7px] text-right font-mono text-[12.5px]">
                    {{ row[2].toLocaleString() }}
                  </td>
                </tr>
                <tr v-if="filtered.length === 0">
                  <td
                    colspan="3"
                    class="px-3 py-6 text-center text-[13px] text-ink-4"
                  >
                    No projects match.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="mt-3 flex items-center justify-between">
            <span class="font-mono text-[12px] text-ink-3"
              >{{ pageStart.toLocaleString() }} –
              {{ pageEnd.toLocaleString() }} of
              {{ filtered.length.toLocaleString() }}</span
            >
            <ArticleTablePagination
              v-if="totalPages > 1"
              :page="String(page)"
              :totalPages="totalPages"
              v-on:update-page="page = $event"
            ></ArticleTablePagination>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import ArticleTablePagination from './ArticleTablePagination.vue';
import PulseLoader from './PulseLoader.vue';

const PAGE_SIZE = 25;

export default {
  name: 'assessments-by-project',
  components: {
    ArticleTablePagination,
    PulseLoader,
  },
  data: function () {
    return {
      assessments: [],
      loading: false,
      loaderColor: '#2456c9',
      loaderSize: '1rem',
      query: '',
      // Default order matches the API: most unassessed articles first.
      sortColumn: 1,
      sortDescending: true,
      page: 1,
      columns: [
        { label: 'Project' },
        { label: 'Unassessed' },
        { label: 'Assessed' },
      ],
    };
  },
  computed: {
    filtered: function () {
      const query = this.query.trim().toLowerCase();
      if (!query) {
        return this.sorted;
      }
      return this.sorted.filter(
        (row) => this.displayName(row[0]).toLowerCase().indexOf(query) !== -1
      );
    },
    sorted: function () {
      const column = this.sortColumn;
      const direction = this.sortDescending ? -1 : 1;
      return [...this.assessments].sort((a, b) => {
        if (column === 0) {
          return (
            direction *
            this.displayName(a[0]).localeCompare(this.displayName(b[0]))
          );
        }
        return direction * (a[column] - b[column]);
      });
    },
    totalPages: function () {
      return Math.max(1, Math.ceil(this.filtered.length / PAGE_SIZE));
    },
    pageRows: function () {
      const start = (this.page - 1) * PAGE_SIZE;
      return this.filtered.slice(start, start + PAGE_SIZE);
    },
    pageStart: function () {
      if (this.filtered.length === 0) {
        return 0;
      }
      return (this.page - 1) * PAGE_SIZE + 1;
    },
    pageEnd: function () {
      return Math.min(this.page * PAGE_SIZE, this.filtered.length);
    },
  },
  watch: {
    query: function () {
      this.page = 1;
    },
  },
  methods: {
    displayName: function (name) {
      return name.replace(/_/g, ' ');
    },
    sortBy: function (column) {
      if (this.sortColumn === column) {
        this.sortDescending = !this.sortDescending;
      } else {
        this.sortColumn = column;
        // Numbers default to descending (biggest first), names ascending.
        this.sortDescending = column !== 0;
      }
      this.page = 1;
    },
    ariaSort: function (column) {
      if (this.sortColumn !== column) {
        return 'none';
      }
      return this.sortDescending ? 'descending' : 'ascending';
    },
    onKeydown: function (event) {
      if (event.key !== '/' || event.defaultPrevented) {
        return;
      }
      const tag = (event.target.tagName || '').toLowerCase();
      if (['input', 'textarea', 'select'].includes(tag)) {
        return;
      }
      if (this.$refs.search) {
        event.preventDefault();
        this.$refs.search.focus();
      }
    },
  },
  mounted: function () {
    document.addEventListener('keydown', this.onKeydown);
  },
  beforeUnmount: function () {
    document.removeEventListener('keydown', this.onKeydown);
  },
  created: async function () {
    this.loading = true;
    try {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/assessments`
      );
      this.assessments = await response.json();
    } catch (err) {
      console.error(err);
    }
    this.loading = false;
  },
};
</script>
