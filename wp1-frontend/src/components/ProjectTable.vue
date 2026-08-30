<template>
  <div>
    <pulse-loader
      class="mt-6 text-center"
      :loading="loading"
      :color="loaderColor"
      :size="loaderSize"
    ></pulse-loader>
    <!-- The heading block shares the centered table's width so it aligns
         with the card's left edge. -->
    <div v-if="tableData" class="mx-auto w-fit max-w-full">
      <h2 class="mb-1 mt-6 text-[19px] font-semibold tracking-[-0.015em]">
        {{ currentProject }}
      </h2>
      <div class="font-mono text-[12px] text-ink-3">
        {{ tableData.total.toLocaleString() }} articles
      </div>

      <!-- Matrix card: the canonical Wikipedia wikitable inside. -->
      <div
        class="mt-4 w-fit max-w-full rounded border border-border bg-surface"
      >
        <div class="overflow-x-auto">
          <table class="wt text-[13px]">
            <thead>
              <tr>
                <th
                  rowspan="2"
                  class="wt-head px-3 py-1.5 text-center align-bottom font-semibold"
                >
                  Quality
                </th>
                <th
                  v-if="!tableData.is_single_col"
                  :colspan="tableData.ordered_cols.length"
                  class="wt-head px-3 py-1.5 text-center font-semibold"
                >
                  Importance
                </th>
                <th
                  rowspan="2"
                  class="wt-head px-3 py-1.5 text-center align-bottom font-semibold"
                >
                  Total
                </th>
              </tr>
              <tr>
                <th
                  v-for="col in tableData.ordered_cols"
                  :key="col"
                  class="px-3 py-1 text-center font-semibold"
                  :class="fillClass(tableData.col_labels[col]) || 'wt-head'"
                >
                  <WikiLink
                    v-if="tableData.col_labels[col].href"
                    :href="tableData.col_labels[col].href"
                    :text="tableData.col_labels[col].text"
                  ></WikiLink>
                  <span v-else>{{ tableData.col_labels[col] }}</span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in tableData.ordered_rows" :key="row">
                <th
                  class="px-3 py-[4px] text-center"
                  :class="[
                    fillClass(tableData.row_labels[row]),
                    isBoldRow(row) ? 'font-semibold' : 'font-normal',
                  ]"
                >
                  <ClassIcon
                    :label="labelText(tableData.row_labels[row])"
                  ></ClassIcon>
                  <WikiLink
                    v-if="tableData.row_labels[row].href"
                    :href="tableData.row_labels[row].href"
                    :text="tableData.row_labels[row].text"
                  ></WikiLink>
                  <span v-else>{{ tableData.row_labels[row] }}</span>
                </th>
                <td
                  v-for="col in tableData.ordered_cols"
                  :key="col"
                  class="px-3 py-[4px] text-right"
                  :class="{
                    'font-semibold': isBoldRow(row),
                    'hover:bg-accent-tint-2': tableData.data[row][col],
                  }"
                >
                  <router-link
                    v-if="tableData.data[row][col]"
                    class="wt-link"
                    :to="{
                      path: `/project/${currentProject}/articles`,
                      query: { quality: row, importance: col },
                    }"
                    >{{
                      tableData.data[row][col].toLocaleString()
                    }}</router-link
                  >
                </td>
                <td
                  class="px-3 py-[4px] text-right font-semibold hover:bg-accent-tint-2"
                >
                  <router-link
                    class="wt-link"
                    :to="{
                      path: `/project/${currentProject}/articles`,
                      query: { quality: row },
                    }"
                    >{{
                      tableData.row_totals[row].toLocaleString()
                    }}</router-link
                  >
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr>
                <th class="wt-head px-3 py-[4px] text-center font-semibold">
                  Total
                </th>
                <td
                  v-for="col in tableData.ordered_cols"
                  :key="col"
                  class="wt-head px-3 py-[4px] text-right font-semibold"
                >
                  <router-link
                    class="wt-link"
                    :to="{
                      path: `/project/${currentProject}/articles`,
                      query: { importance: col },
                    }"
                    >{{
                      tableData.col_totals[col].toLocaleString()
                    }}</router-link
                  >
                </td>
                <td class="wt-head px-3 py-[4px] text-right font-semibold">
                  {{ tableData.total.toLocaleString() }}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
        <div
          class="border-t border-border-subtle px-[14px] py-[9px] font-mono text-[11.5px] text-ink-3"
        >
          Last updated {{ localDate(tableData.timestamp) }} · all times local
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ClassIcon from './ClassIcon.vue';
import WikiLink from './WikiLink.vue';
import PulseLoader from './PulseLoader.vue';

import { localDate } from '../lib/util.js';
import { fillClass } from '../lib/labels.js';

export default {
  name: 'project-table',
  components: {
    ClassIcon,
    WikiLink,
    PulseLoader,
  },
  props: {
    projectId: String,
  },
  data: function () {
    return {
      tableData: null,
      loading: false,
      loaderColor: '#2456c9',
      loaderSize: '1rem',
    };
  },
  computed: {
    currentProject: function () {
      if (!this.projectId) {
        return null;
      }
      return this.projectId.replace(/_/g, ' ');
    },
  },
  watch: {
    projectId: async function (projectId) {
      this.tableData = null;
      if (!projectId) {
        return;
      }

      this.loading = true;
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${projectId}/table`
      );
      const json = await response.json();
      this.loading = false;

      this.tableData = json.table_data;
    },
  },
  methods: {
    labelText: function (cls) {
      if (cls && cls.text) {
        return cls.text;
      }
      return cls;
    },
    fillClass: function (cls) {
      return fillClass(this.labelText(cls));
    },
    // The synthetic Other/Assessed rows render bold, matching the WP 1.0
    // bot's table on Wikipedia.
    isBoldRow: function (row) {
      const text = this.labelText(this.tableData.row_labels[row]);
      return text === 'Other' || text === 'Assessed';
    },
    localDate: function (secs) {
      return localDate(secs);
    },
  },
};
</script>

<style>
@import '../labels.css';
</style>
