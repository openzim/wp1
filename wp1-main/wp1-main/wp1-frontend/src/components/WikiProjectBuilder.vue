<template>
  <BaseBuilder
    :key="$route.path"
    :listName="'WikiProject Selection'"
    :model="'wp1.selection.models.wikiproject'"
    :params="params"
    :builderId="$route.params.builder_id"
    :invalidItems="invalidItems"
    :projectFilter="projectFilter"
    @onBuilderLoaded="onBuilderLoaded"
    @onBeforeSubmit="onBeforeSubmit"
    @onValidationError="onValidationError"
  >
    <template #create-desc>
      <p>
        Use this tool to create an article selection list for English Wikipedia
        only (other languages not supported), based off the articles included in
        the specified
        <a href="https://en.wikipedia.org/wiki/WikiProject">WikiProjects</a>.
        Your selection will be saved online and will be accessible through a URL
        that will be provided once it has been saved.
      </p>
    </template>
    <template #extra-params>
      <div id="lists" class="form-group m-4">
        <label for="include-items">WikiProjects to include</label>
        <textarea
          id="include-items"
          ref="includeItems"
          class="form-control my-2"
          v-model="includeText"
          rows="5"
          required
        ></textarea>

        <div class="invalid-feedback">
          Please provide WikiProjects to include
        </div>

        <label for="exclude-items">WikiProjects to exclude</label>
        <textarea
          id="exclude-items"
          ref="excludeItems"
          class="form-control my-2"
          v-model="excludeText"
          rows="5"
        ></textarea>
      </div>
    </template>
  </BaseBuilder>
</template>

<script>
import BaseBuilder from './BaseBuilder.vue';

export default {
  components: { BaseBuilder },
  name: 'WikiProjectBuilder',
  data: function () {
    return {
      includeText: '',
      excludeText: '',
      invalidItems: '',
      params: {},
    };
  },
  methods: {
    onBuilderLoaded: function (builder) {
      this.includeText = builder.params.include.join('\n');
      this.excludeText = builder.params.exclude.join('\n');
    },
    onBeforeSubmit: function () {
      this.$refs.includeItems.setCustomValidity('');
    },
    onValidationError: function (data) {
      this.invalidItems = data.items.invalid.join('\n');
    },
    projectFilter: function (projectName) {
      return projectName == 'en.wikipedia.org';
    },
  },
  watch: {
    includeText: function () {
      const include = this.includeText.split('\n');
      if (include.length === 1 && include[0] === '') {
        this.params.include = [];
        return;
      }
      this.params.include = this.includeText.split('\n') || [];
    },
    excludeText: function () {
      const exclude = this.excludeText.split('\n');
      if (exclude.length === 1 && exclude[0] === '') {
        this.params.exclude = [];
        return;
      }
      this.params.exclude = this.excludeText.split('\n');
    },
  },
};
</script>

<style scoped></style>
