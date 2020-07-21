<template>
  <div>
    <div class="row">
      <div class="col" v-if="notFound">
        <h4>The project with the name {{ currentProject }} was not found.</h4>
      </div>
      <div class="col" v-else>
        <h4>
          {{ currentProject }} articles
          <span v-if="$route.query.importance || $route.query.quality">
            -
          </span>
          <span v-if="$route.query.importance">
            <WikiLink
              v-if="hasImportanceLink()"
              :href="categoryLinks[$route.query.importance].href"
              :text="categoryLinks[$route.query.importance].text"
            ></WikiLink>
            <span v-if="!hasImportanceLink()">{{
              categoryLinks[$route.query.importance]
            }}</span>
            importance</span
          >
          <span v-if="$route.query.quality"
            ><span v-if="$route.query.importance"> / </span>
            <WikiLink
              v-if="hasQualityLink()"
              :href="categoryLinks[$route.query.quality].href"
              :text="categoryLinks[$route.query.quality].text"
            ></WikiLink>
            <span v-if="!hasQualityLink()">{{
              categoryLinks[$route.query.quality]
            }}</span>
            quality</span
          >
        </h4>
        <p><a :href="'#/project/' + currentProject">Back to table</a></p>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <ArticleTable
          :projectId="currentProjectId"
          :importance="$route.query.importance"
          :quality="$route.query.quality"
          :page="$route.query.page"
          :numRows="$route.query.numRows"
        ></ArticleTable>
      </div>
    </div>
  </div>
</template>

<script>
import ArticleTable from './ArticleTable.vue';
import WikiLink from './WikiLink.vue';

export default {
  name: 'articlepage',
  components: {
    ArticleTable,
    WikiLink
  },
  props: ['currentProject'],
  data: function() {
    return {
      notFound: false,
      categoryLinks: {}
    };
  },
  computed: {
    currentProjectId: function() {
      if (!this.currentProject) {
        return null;
      }
      return this.currentProject.replace(/ /g, '_');
    }
  },
  beforeRouteUpdate(to, from, next) {
    this.checkIfProjectExists(to.params.projectName.replace(/ /g, '_'));
    next();
  },
  created: function() {
    this.checkIfProjectExists(this.currentProjectId);
    if (!this.notFound) {
      this.getCategoryLinks();
    }
  },
  methods: {
    getCategoryLinks: async function() {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${this.currentProjectId}/category_links`
      );
      this.categoryLinks = await response.json();
    },
    hasImportanceLink: function() {
      return (
        this.categoryLinks &&
        this.categoryLinks[this.$route.query.importance] &&
        this.categoryLinks[this.$route.query.importance].href
      );
    },
    hasQualityLink: function() {
      return (
        this.categoryLinks &&
        this.categoryLinks[this.$route.query.quality] &&
        this.categoryLinks[this.$route.query.quality].href
      );
    },
    checkIfProjectExists: async function(projectId) {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${projectId}`
      );
      this.notFound = response.status === 404;
    }
  }
};
</script>

<style scoped>
h4 a:visited {
  color: #5d7791 !important;
}
</style>
