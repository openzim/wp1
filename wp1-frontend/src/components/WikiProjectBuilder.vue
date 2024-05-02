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
        Your selection will be saved in public cloud storage and can be accessed
        through URLs that will be provided once it has been saved.
      </p>
    </template>
    <template #extra-params>
      <div id="lists" class="form-group m-4">
        <label for="add-items">WikiProjects to include</label>
        <textarea
          id="add-items"
          ref="addItems"
          class="form-control my-2"
          v-model="addText"
          rows="5"
          required
        ></textarea>

        <div class="invalid-feedback">
          Please provide WikiProjects to include
        </div>

        <label for="subtract-items">WikiProjects to exclude</label>
        <textarea
          id="subtract-items"
          ref="subtractItems"
          class="form-control my-2"
          v-model="subtractText"
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
      addText: '',
      subtractText: '',
      invalidItems: '',
      params: {},
    };
  },
  methods: {
    onBuilderLoaded: function (builder) {
      this.addText = builder.params.add.join('\n');
      this.subtractText = builder.params.subtract.join('\n');
    },
    onBeforeSubmit: function () {
      this.$refs.addItems.setCustomValidity('');
    },
    onValidationError: function (data) {
      this.invalidItems = data.items.invalid.join('\n');
    },
    projectFilter: function (projectName) {
      return projectName == 'en.wikipedia.org';
    },
  },
  watch: {
    addText: function () {
      const add = this.subtractText.split('\n');
      if (add.length === 1 && add[0] === '') {
        this.params.add = [];
        return;
      }
      this.params.add = this.addText.split('\n') || [];
    },
    subtractText: function () {
      const subtract = this.subtractText.split('\n');
      if (subtract.length === 1 && subtract[0] === '') {
        this.params.subtract = [];
        return;
      }
      this.params.subtract = this.subtractText.split('\n');
    },
  },
};
</script>

<style scoped></style>
