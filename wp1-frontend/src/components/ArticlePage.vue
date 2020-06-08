<template>
  <div>
    <div class="row">
      <div class="col">
        <h4>
          {{ currentProject }} articles
          <span v-if="$route.query.importance || $route.query.quality">
            -
          </span>
          <span v-if="$route.query.importance"
            >{{ displayClass($route.query.importance) }} importance</span
          >
          <span v-if="$route.query.quality"
            ><span v-if="$route.query.importance"> / </span
            >{{ displayClass($route.query.quality) }} quality</span
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
        ></ArticleTable>
      </div>
    </div>
  </div>
</template>

<script>
import ArticleTable from './ArticleTable.vue';

export default {
  name: 'articlepage',
  components: {
    ArticleTable
  },
  props: ['currentProject'],
  computed: {
    currentProjectId: function() {
      if (!this.currentProject) {
        return null;
      }
      return this.currentProject.replace(/ /g, '_');
    }
  },
  methods: {
    displayClass: function(cls) {
      return cls.split('-')[0];
    }
  },
  watch: {
    currentProject: function(val) {
      if (val !== this.$route.params.projectName) {
        this.$router.push({
          path: `/project/${val}/articles`,
          query: {
            importance: this.$route.query.importance,
            quality: this.$route.query.quality
          }
        });
      }
    }
  }
};
</script>

<style scoped></style>
