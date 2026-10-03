<template>
  <div>
    <pulse-loader
      v-if="loading"
      class="mt-6 text-center"
      :loading="loading"
      :color="loaderColor"
      :size="loaderSize"
    ></pulse-loader>
    <div v-else-if="articleData">
      <ArticleFilterBar
        :projectId="projectId"
        :initialQuality="quality"
        :initialImportance="importance"
        :initialPattern="articlePattern"
        :numRows="articleData.pagination.display.num_rows"
        :startPage="page || '1'"
        :hideRatingSelect="!!hideRatingSelect"
        v-on:update-filters="onUpdateFilters($event)"
      ></ArticleFilterBar>

      <template v-if="tableData.length > 0">
        <div class="mt-3 flex flex-wrap items-center justify-between gap-2">
          <span class="font-mono text-[12px] text-ink-3"
            >Articles {{ articleData.pagination.display.start }} –
            {{ articleData.pagination.display.end }} of
            {{ articleData.pagination.total }} ·
            {{ articleData.pagination.total_pages }}
            page<template v-if="articleData.pagination.total_pages !== 1"
              >s</template
            ></span
          >
          <a v-if="!projectIdB" :href="tsvUrl" download class="text-[12.5px]"
            >Download all results as TSV</a
          >
        </div>
        <ArticleTablePagination
          v-if="articleData.pagination.total_pages > 1"
          class="mt-2"
          v-on:update-page="onUpdatePage($event)"
          :page="page"
          :totalPages="articleData.pagination.total_pages"
        >
        </ArticleTablePagination>

        <!-- Article table: wikitable identity, full-cell class fills. -->
        <div
          class="mx-auto mt-2 w-fit max-w-full overflow-x-auto rounded border border-border"
        >
          <table v-if="!projectIdB" class="wt text-[13px]">
            <thead>
              <tr class="wt-head text-left">
                <th class="w-10 px-2 py-[7px] text-right font-semibold">#</th>
                <th class="px-2 py-[7px] font-semibold">Article</th>
                <th class="px-2 py-[7px]"></th>
                <th class="px-2 py-[7px] text-center font-semibold">
                  Importance
                </th>
                <th class="px-2 py-[7px] font-semibold">Rated</th>
                <th class="px-2 py-[7px] text-center font-semibold">Quality</th>
                <th class="px-2 py-[7px] font-semibold">Rated</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in tableData" :key="index">
                <td
                  class="px-2 py-[6px] text-right font-mono text-[12px] text-ink-4"
                >
                  {{ articleData.pagination.display.start + index }}
                </td>
                <td
                  class="max-w-[180px] truncate px-2 py-[6px] md:max-w-[640px]"
                  :title="row.article"
                >
                  <a :href="row.article_link">{{ row.article }}</a>
                </td>
                <td
                  class="whitespace-nowrap px-2 py-[6px] font-mono text-[11px] text-ink-4"
                >
                  (<a :href="row.article_talk_link">t</a> ·
                  <a :href="row.article_history_link">h</a>)
                </td>
                <td
                  class="px-2 py-[6px] text-center"
                  :class="classFill(row.importance)"
                >
                  <a
                    v-if="classHref(row.importance)"
                    :href="classHref(row.importance)"
                    >{{ classLabel(row.importance) }}</a
                  >
                  <span v-else>{{ classLabel(row.importance) }}</span>
                </td>
                <td
                  class="whitespace-nowrap px-2 py-[6px] font-mono text-[12px] text-ink-3"
                >
                  <a
                    class="!text-inherit"
                    :href="timestampLink(row.article, row.importance_updated)"
                    >{{ formatTimestamp(row.importance_updated) }}</a
                  >
                  <span class="text-ink-4"
                    >(<a
                      class="!text-inherit"
                      :href="
                        timestampLink(row.article_talk, row.importance_updated)
                      "
                      >t</a
                    >)</span
                  >
                </td>
                <td
                  class="px-2 py-[6px] text-center"
                  :class="classFill(row.quality)"
                >
                  <ClassIcon
                    :label="classLabel(row.quality)"
                    :size="13"
                  ></ClassIcon>
                  <a
                    v-if="classHref(row.quality)"
                    :href="classHref(row.quality)"
                    >{{ classLabel(row.quality) }}</a
                  >
                  <span v-else>{{ classLabel(row.quality) }}</span>
                </td>
                <td
                  class="whitespace-nowrap px-2 py-[6px] font-mono text-[12px] text-ink-3"
                >
                  <a
                    class="!text-inherit"
                    :href="timestampLink(row.article, row.quality_updated)"
                    >{{ formatTimestamp(row.quality_updated) }}</a
                  >
                  <span class="text-ink-4"
                    >(<a
                      class="!text-inherit"
                      :href="
                        timestampLink(row.article_talk, row.quality_updated)
                      "
                      >t</a
                    >)</span
                  >
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Compare mode: two rating column-groups separated by a
               borderless white channel so project fills never touch. -->
          <table v-else class="wt text-[13px]">
            <thead>
              <tr class="wt-head">
                <th colspan="3" class="px-2 py-[6px]"></th>
                <th colspan="2" class="px-2 py-[6px] text-center font-semibold">
                  {{ projectId.replace(/_/g, ' ') }}
                </th>
                <th class="wt-gap"></th>
                <th colspan="2" class="px-2 py-[6px] text-center font-semibold">
                  {{ projectIdB.replace(/_/g, ' ') }}
                </th>
              </tr>
              <tr class="wt-head text-left">
                <th class="w-10 px-2 py-[7px] text-right font-semibold">#</th>
                <th class="px-2 py-[7px] font-semibold">Article</th>
                <th class="px-2 py-[7px]"></th>
                <th class="px-2 py-[7px] text-center font-semibold">Imp</th>
                <th class="px-2 py-[7px] text-center font-semibold">Qual</th>
                <th class="wt-gap"></th>
                <th class="px-2 py-[7px] text-center font-semibold">Imp</th>
                <th class="px-2 py-[7px] text-center font-semibold">Qual</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in tableData" :key="index">
                <td
                  class="px-2 py-[6px] text-right font-mono text-[12px] text-ink-4"
                >
                  {{ articleData.pagination.display.start + index }}
                </td>
                <td
                  class="max-w-[180px] truncate px-2 py-[6px] md:max-w-[560px]"
                  :title="row[0].article"
                >
                  <a :href="row[0].article_link">{{ row[0].article }}</a>
                </td>
                <td
                  class="whitespace-nowrap px-2 py-[6px] font-mono text-[11px] text-ink-4"
                >
                  (<a :href="row[0].article_talk_link">t</a> ·
                  <a :href="row[0].article_history_link">h</a>)
                </td>
                <td
                  class="px-2 py-[6px] text-center"
                  :class="classFill(row[0].importance)"
                >
                  {{ classLabel(row[0].importance) }}
                </td>
                <td
                  class="px-2 py-[6px] text-center"
                  :class="classFill(row[0].quality)"
                >
                  <ClassIcon
                    :label="classLabel(row[0].quality)"
                    :size="13"
                  ></ClassIcon
                  >{{ classLabel(row[0].quality) }}
                </td>
                <td class="wt-gap"></td>
                <td
                  class="px-2 py-[6px] text-center"
                  :class="classFill(row[1].importance)"
                >
                  {{ classLabel(row[1].importance) }}
                </td>
                <td
                  class="px-2 py-[6px] text-center"
                  :class="classFill(row[1].quality)"
                >
                  <ClassIcon
                    :label="classLabel(row[1].quality)"
                    :size="13"
                  ></ClassIcon
                  >{{ classLabel(row[1].quality) }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="mt-3 flex flex-wrap items-center justify-between gap-2">
          <span class="font-mono text-[12px] text-ink-3"
            >Articles {{ articleData.pagination.display.start }} –
            {{ articleData.pagination.display.end }} of
            {{ articleData.pagination.total }}</span
          >
          <ArticleTablePagination
            v-if="articleData.pagination.total_pages > 1"
            v-on:update-page="onUpdatePage($event)"
            :page="page"
            :totalPages="articleData.pagination.total_pages"
          >
          </ArticleTablePagination>
        </div>
      </template>

      <div v-else class="py-10 text-center text-[14px] text-ink-3">
        No results to display
      </div>
    </div>
  </div>
</template>

<script>
import ArticleFilterBar from './ArticleFilterBar.vue';
import ArticleTablePagination from './ArticleTablePagination.vue';
import ClassIcon from './ClassIcon.vue';
import PulseLoader from './PulseLoader.vue';

import { fillClass } from '../lib/labels.js';

export default {
  name: 'article-table',
  components: {
    ArticleFilterBar,
    ArticleTablePagination,
    ClassIcon,
    PulseLoader,
  },
  data: function () {
    return {
      articleData: null,
      categoryLinks: {},
      loading: false,
      loaderColor: '#2456c9',
      loaderSize: '1rem',
    };
  },
  props: [
    'projectId',
    'projectIdB',
    'importance',
    'quality',
    'importanceB',
    'qualityB',
    'page',
    'numRows',
    'articlePattern',
    'hideRatingSelect',
  ],
  computed: {
    tableData: function () {
      if (this.articleData === null) {
        return [];
      }
      return this.articleData['articles'];
    },
    tsvUrl: function () {
      const url = this.articlesUrl(false);
      url.searchParams.append('format', 'tsv');
      return url.toString();
    },
  },
  created: function () {
    this.updateTable();
  },
  watch: {
    projectId: async function (projectId) {
      if (!projectId) {
        this.articleData = null;
        return;
      }
      await this.updateTable();
    },
    projectIdB: async function () {
      await this.updateTable();
    },
    importance: async function () {
      await this.updateTable();
    },
    quality: async function () {
      await this.updateTable();
    },
    importanceB: async function () {
      await this.updateTable();
    },
    qualityB: async function () {
      await this.updateTable();
    },
    page: async function () {
      await this.updateTable();
    },
    numRows: async function () {
      await this.updateTable();
    },
    articlePattern: async function () {
      await this.updateTable();
    },
  },
  methods: {
    onUpdateFilters: function (selection) {
      this.$emit('update-filters', selection);
    },
    onUpdatePage: function (page) {
      this.$emit('update-page', page);
    },
    articlesUrl: function (includePagination) {
      const url = new URL(
        `${import.meta.env.VITE_API_URL}/projects/${this.projectId}/articles`
      );
      const params = {};
      if (this.importance) {
        params.importance = this.importance;
      }
      if (this.quality) {
        params.quality = this.quality;
      }
      if (this.projectIdB) {
        params.projectB = this.projectIdB;
      }
      if (this.importanceB) {
        params.importanceB = this.importanceB;
      }
      if (this.qualityB) {
        params.qualityB = this.qualityB;
      }
      if (this.articlePattern) {
        params.articlePattern = this.articlePattern;
      }
      if (includePagination) {
        if (this.page) {
          params.page = this.page;
        }
        if (this.numRows) {
          params.numRows = this.numRows;
        }
      }
      Object.keys(params).forEach((key) =>
        url.searchParams.append(key, params[key])
      );
      return url;
    },
    classLabel: function (qualOrImp) {
      if (!this.categoryLinks[qualOrImp]) {
        return '';
      }
      return (
        this.categoryLinks[qualOrImp].text || this.categoryLinks[qualOrImp]
      );
    },
    classHref: function (qualOrImp) {
      const link = this.categoryLinks[qualOrImp];
      return (link && link.href) || null;
    },
    classFill: function (qualOrImp) {
      return fillClass(this.classLabel(qualOrImp));
    },
    getCategoryLinks: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${
          this.projectId
        }/category_links`
      );
      this.categoryLinks = await response.json();
    },
    updateTable: async function () {
      const url = this.articlesUrl(true);

      let finishedRequest = false;
      setTimeout(() => {
        if (!finishedRequest) {
          this.loading = true;
        }
      }, 100);
      const response = await fetch(url);
      finishedRequest = true;
      if (response.ok) {
        this.articleData = await response.json();
      } else {
        this.articleData = null;
      }
      this.loading = false;
      await this.getCategoryLinks();
    },
    formatTimestamp: function (ts) {
      return ts.split('T')[0];
    },
    timestampLink: function (articleName, ts) {
      return `${
        import.meta.env.VITE_API_URL
      }/articles/redirect?name=${encodeURIComponent(
        articleName
      )}&timestamp=${encodeURIComponent(ts)}`;
    },
  },
};
</script>

<style>
@import '../labels.css';
</style>
