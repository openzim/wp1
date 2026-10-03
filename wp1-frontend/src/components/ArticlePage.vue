<template>
  <div class="wp1r flex flex-1 flex-col bg-page">
    <div
      class="mx-auto flex w-full max-w-[1200px] flex-1 flex-col border-x border-border bg-surface"
    >
      <div class="px-[18px] pb-16 pt-6 max-md:px-3">
        <div v-if="notFound">
          <h2 class="m-0 text-[19px] font-semibold tracking-[-0.015em]">
            The project with the name {{ currentProject }} was not found.
          </h2>
        </div>
        <div v-else>
          <router-link
            class="text-[13px]"
            :to="`/project/${currentProject.replace(/_/g, ' ')}`"
            >← {{ currentProject }} table</router-link
          >
          <div class="mt-2 flex flex-wrap items-baseline gap-x-2 gap-y-1">
            <h2 class="m-0 text-[19px] font-semibold tracking-[-0.015em]">
              {{ currentProject }} articles
            </h2>
            <template v-if="$route.query.importance">
              <a
                v-if="hasImportanceLink()"
                class="wp1r-badge border-accent-border bg-accent-tint text-[11px] !normal-case !tracking-normal !text-accent-hover"
                :href="categoryLinks[$route.query.importance].href"
                >{{ categoryLinks[$route.query.importance].text }} importance</a
              >
              <span
                v-else
                class="wp1r-badge text-[11px] !normal-case !tracking-normal"
                >{{ categoryLinks[$route.query.importance] }} importance</span
              >
            </template>
            <template v-if="$route.query.quality">
              <a
                v-if="hasQualityLink()"
                class="wp1r-badge border-accent-border bg-accent-tint text-[11px] !normal-case !tracking-normal !text-accent-hover"
                :href="categoryLinks[$route.query.quality].href"
                >{{ categoryLinks[$route.query.quality].text }} quality</a
              >
              <span
                v-else
                class="wp1r-badge text-[11px] !normal-case !tracking-normal"
                >{{ categoryLinks[$route.query.quality] }} quality</span
              >
            </template>
          </div>
          <ArticleTable
            :projectId="currentProjectId"
            :importance="$route.query.importance"
            :quality="$route.query.quality"
            :page="$route.query.page"
            :numRows="$route.query.numRows"
            :articlePattern="$route.query.articlePattern"
            v-on:update-filters="onUpdateFilters($event)"
            v-on:update-page="onUpdatePage($event)"
          ></ArticleTable>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ArticleTable from './ArticleTable.vue';

export default {
  name: 'article-page',
  components: {
    ArticleTable,
  },
  props: ['currentProject'],
  data: function () {
    return {
      notFound: false,
      categoryLinks: {},
    };
  },
  computed: {
    currentProjectId: function () {
      if (!this.currentProject) {
        return null;
      }
      return this.currentProject.replace(/ /g, '_');
    },
  },
  beforeRouteUpdate(to, from, next) {
    this.checkIfProjectExists(to.params.projectName.replace(/ /g, '_'));
    next();
  },
  created: function () {
    this.checkIfProjectExists(this.currentProjectId);
    if (!this.notFound) {
      this.getCategoryLinks();
    }
  },
  methods: {
    getCategoryLinks: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${
          this.currentProjectId
        }/category_links`
      );
      this.categoryLinks = await response.json();
    },
    hasImportanceLink: function () {
      return (
        this.categoryLinks &&
        this.categoryLinks[this.$route.query.importance] &&
        this.categoryLinks[this.$route.query.importance].href
      );
    },
    hasQualityLink: function () {
      return (
        this.categoryLinks &&
        this.categoryLinks[this.$route.query.quality] &&
        this.categoryLinks[this.$route.query.quality].href
      );
    },
    checkIfProjectExists: async function (projectId) {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${projectId}`
      );
      this.notFound = response.status === 404;
    },
    // The filter bar's single commit: every filter and pagination field is
    // pushed to the query at once.
    onUpdateFilters: function (selection) {
      const query = this.$route.query;
      if (
        (query.quality || '') === selection.quality &&
        (query.importance || '') === selection.importance &&
        (query.articlePattern || '') === selection.articlePattern &&
        String(query.numRows || 100) === String(selection.rows) &&
        String(query.page || 1) === String(selection.page)
      ) {
        return;
      }
      this.$router.push({
        path: `/project/${this.currentProject}/articles`,
        query: {
          quality: selection.quality || undefined,
          importance: selection.importance || undefined,
          page: String(selection.page) === '1' ? undefined : selection.page,
          numRows:
            String(selection.rows) === '100' ? undefined : selection.rows,
          articlePattern: selection.articlePattern || undefined,
        },
      });
    },
    onUpdatePage: function (page) {
      if (this.$route.query.page === page.toString()) {
        return;
      }
      this.$router.push({
        path: `/project/${this.currentProject}/articles`,
        query: {
          quality: this.$route.query.quality,
          importance: this.$route.query.importance,
          page: page.toString(),
          numRows: this.$route.query.numRows,
          articlePattern: this.$route.query.articlePattern,
        },
      });
    },
  },
};
</script>
