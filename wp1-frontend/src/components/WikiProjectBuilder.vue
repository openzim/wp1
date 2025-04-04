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
      <div id="lists" class="form-group m-4 my-2">
        <div class="my-2">
          <label for="include-items">WikiProjects to include</label>
            <Autocomplete
              id="include-items"
              ref="includeAutocomplete"
              :hideInstructions="true"
              @select-project="addIncludeProject"
            />
            <div id="include-projects" class="mt-2 d-flex flex-wrap" v-if="includeProjects.length > 0">
              <div 
                v-for="(project, index) in includeProjects" 
                :key="'include-'+index"
                class="d-flex bg-light align-items-center m-2 p-2 shadow-sm border rounded"
              >
                {{ project }}
                <button class="btn btn-sm ms-1 p-1 text-danger rounded-circle" type="button" @click="removeIncludeProject(index)" title="Remove project">
                  <i class="bi bi-x-circle-fill"></i>
                </button>
              </div>
          </div>
        </div>

        <div class="my-2">
          <label for="exclude-items">WikiProjects to exclude</label>
            <Autocomplete
              id="exclude-items"
              ref="excludeAutocomplete"
              :hideInstructions="true"
              @select-project="addExcludeProject"
            />
          <div id="exclude-projects" class="mt-2 d-flex flex-wrap" v-if="excludeProjects.length > 0">
            <div 
              v-for="(project, index) in excludeProjects" 
              :key="'exclude-'+index"
              class="d-flex bg-dark text-white align-items-center m-2 p-2 shadow-sm border rounded"
            >
              {{ project }}
              <button class="btn btn-sm ms-1 p-1 text-danger rounded-circle" type="button" @click="removeExcludeProject(index)" title="Remove project">
                <i class="bi bi-x-circle-fill"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>
  </BaseBuilder>
</template>

<script>
import BaseBuilder from './BaseBuilder.vue';
import Autocomplete from './Autocomplete.vue';

export default {
  components: { BaseBuilder, Autocomplete },
  name: 'WikiProjectBuilder',
  data: function () {
    return {
      includeProjects: [],
      excludeProjects: [],
      invalidItems: '',
      params: {
        include: [],
        exclude: []
      },
    };
  },
  methods: {
    onBuilderLoaded: function (builder) {
      this.includeProjects = [...builder.params.include];
      this.excludeProjects = [...builder.params.exclude];
      this.updateParams();
    },
    onBeforeSubmit: function () {
      if (this.$refs.includeAutocomplete && this.$refs.includeAutocomplete.$refs.input) {
        if (this.includeProjects.length === 0) {
          this.$refs.includeAutocomplete.$refs.input.setCustomValidity('Please provide WikiProjects to include');
        } else {
          this.$refs.includeAutocomplete.$refs.input.setCustomValidity('');
        }
      }
      return this.includeProjects.length > 0;
    },
    onValidationError: function (data) {
      this.invalidItems = data.items.invalid.join('\n');
    },
    projectFilter: function (projectName) {
      return projectName == 'en.wikipedia.org';
    },
    addIncludeProject: function (project) {
      if (!this.includeProjects.includes(project)) {
        this.includeProjects.push(project);
        this.updateParams();
      }
      this.$refs.includeAutocomplete.search = '';
    },
    removeIncludeProject: function (index) {
      this.includeProjects.splice(index, 1);
      this.updateParams();
    },
    addExcludeProject: function (project) {
      if (!this.excludeProjects.includes(project)) {
        this.excludeProjects.push(project);
        this.updateParams();
      }
      this.$refs.excludeAutocomplete.search = '';
    },
    removeExcludeProject: function (index) {
      this.excludeProjects.splice(index, 1);
      this.updateParams();
    },
    updateParams: function () {
      this.params.include = [...this.includeProjects];
      this.params.exclude = [...this.excludeProjects];
    }
  }
};
</script>

<style scoped></style>
