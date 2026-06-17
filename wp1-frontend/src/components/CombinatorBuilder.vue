<template>
  <BaseBuilder
    :key="$route.path"
    :listName="'Combinator Selection'"
    :model="'wp1.selection.models.combinator'"
    :params="params"
    :builderId="$route.params.builder_id"
    :invalidItems="invalidItems"
    @onBuilderLoaded="onBuilderLoaded"
    @onBeforeSubmit="onBeforeSubmit"
    @onValidationError="onValidationError"
  >
    <template #create-desc>
      <p>
        Use this tool to combine existing selections. Choose builders to
        include, optionally choose builders to exclude, and select whether each
        group uses all articles or only articles shared by every builder in that
        group.
      </p>
    </template>

    <template #extra-params="{ builder }">
      <div id="combinator-groups" class="form-group m-4 my-2">
        <div class="card mb-4 combinator-card">
          <div class="card-header bg-success text-white">
            <h5 class="mb-0">Include</h5>
          </div>
          <div class="card-body">
            <div class="form-group mb-3">
              <label for="include-operation"
                >Combine included builders using</label
              >
              <select
                id="include-operation"
                v-model="includeOperation"
                class="custom-select my-list"
              >
                <option value="union">All articles from any builder</option>
                <option value="intersection">
                  Only articles shared by every builder
                </option>
              </select>
            </div>

            <div id="include-items" class="form-group mb-3">
              <label for="include-builder-select">Builders to include</label>
              <div class="input-group">
                <select
                  id="include-builder-select"
                  ref="includeSelect"
                  v-model="includeDropdown"
                  class="custom-select my-list"
                  :class="{ 'is-invalid': includeValidationMessage }"
                >
                  <option value="">Select a builder to add</option>
                  <option
                    v-for="item in availableIncludeBuilders(builder.project)"
                    :key="'include-option-' + item.id"
                    :value="item.id"
                  >
                    {{ builderOptionLabel(item) }}
                  </option>
                </select>
                <div class="input-group-append">
                  <button
                    id="add-include-builder"
                    type="button"
                    class="btn btn-success"
                    :disabled="!includeDropdown"
                    @click="addSelectedBuilder('include')"
                  >
                    Add
                  </button>
                </div>
                <div class="invalid-feedback">
                  {{
                    includeValidationMessage ||
                    'Please add at least one builder to include'
                  }}
                </div>
              </div>
              <div v-if="!buildersFetchFinished" class="text-muted small mt-2">
                Loading builders...
              </div>
              <div
                v-else-if="buildersLoadError"
                class="alert alert-danger mt-2 mb-0"
                role="alert"
              >
                {{ buildersLoadError }}
              </div>
              <div
                v-else-if="hasNoEligibleBuilders(builder.project)"
                class="alert alert-warning mt-2 mb-0"
                role="alert"
              >
                No eligible builders are available for
                {{ builder.project }}.
              </div>
            </div>

            <div
              id="include-builders"
              class="selected-builders"
              v-if="includeBuilders.length > 0"
            >
              <span
                v-for="builderId in includeBuilders"
                :key="'include-builder-' + builderId"
                class="badge badge-success combinator-badge"
              >
                {{ builderLabel(builderId) }}
                <button
                  type="button"
                  class="remove-builder"
                  @click="removeSelectedBuilder('include', builderId)"
                  aria-label="Remove included builder"
                >
                  &times;
                </button>
              </span>
            </div>
            <div v-else class="text-muted">No builders selected</div>
          </div>
        </div>

        <div class="card mb-4 combinator-card">
          <div class="card-header bg-danger text-white">
            <h5 class="mb-0">
              Exclude <span class="font-weight-normal">(optional)</span>
            </h5>
          </div>
          <div class="card-body">
            <div class="form-group mb-3">
              <label for="exclude-operation"
                >Combine excluded builders using</label
              >
              <select
                id="exclude-operation"
                v-model="excludeOperation"
                class="custom-select my-list"
              >
                <option value="union">All articles from any builder</option>
                <option value="intersection">
                  Only articles shared by every builder
                </option>
              </select>
            </div>

            <div id="exclude-items" class="form-group mb-3">
              <label for="exclude-builder-select">Builders to exclude</label>
              <div class="input-group">
                <select
                  id="exclude-builder-select"
                  ref="excludeSelect"
                  v-model="excludeDropdown"
                  class="custom-select my-list"
                  :class="{ 'is-invalid': excludeValidationMessage }"
                >
                  <option value="">Select a builder to add</option>
                  <option
                    v-for="item in availableExcludeBuilders(builder.project)"
                    :key="'exclude-option-' + item.id"
                    :value="item.id"
                  >
                    {{ builderOptionLabel(item) }}
                  </option>
                </select>
                <div class="input-group-append">
                  <button
                    id="add-exclude-builder"
                    type="button"
                    class="btn btn-danger"
                    :disabled="!excludeDropdown"
                    @click="addSelectedBuilder('exclude')"
                  >
                    Add
                  </button>
                </div>
                <div class="invalid-feedback">
                  {{ excludeValidationMessage }}
                </div>
              </div>
            </div>

            <div
              id="exclude-builders"
              class="selected-builders"
              v-if="excludeBuilders.length > 0"
            >
              <span
                v-for="builderId in excludeBuilders"
                :key="'exclude-builder-' + builderId"
                class="badge badge-danger combinator-badge"
              >
                {{ builderLabel(builderId) }}
                <button
                  type="button"
                  class="remove-builder"
                  @click="removeSelectedBuilder('exclude', builderId)"
                  aria-label="Remove excluded builder"
                >
                  &times;
                </button>
              </span>
            </div>
            <div v-else class="text-muted">
              No builders selected. Nothing will be excluded.
            </div>
          </div>
        </div>

        <div class="combinator-preview p-3 rounded border">
          <h5 class="mb-2">Expression preview</h5>
          <code>{{ expressionPreview }}</code>
        </div>
      </div>
    </template>
  </BaseBuilder>
</template>

<script>
import BaseBuilder from './BaseBuilder.vue';
//one of the metabuilders , so we filter the dropdown
//enhance later to include any metaBuilder
const COMBINATOR_MODEL = 'wp1.selection.models.combinator';

export default {
  components: { BaseBuilder },
  name: 'CombinatorBuilder',
  data: function () {
    return {
      allBuilders: [],
      buildersLoadError: '',
      buildersFetchFinished: false,
      invalidItems: '',
      includeBuilders: [],
      includeDropdown: '',
      includeOperation: 'union',
      includeValidationMessage: '',
      excludeBuilders: [],
      excludeDropdown: '',
      excludeOperation: 'union',
      excludeValidationMessage: '',
      params: this.defaultParams(),
    };
  },
  computed: {
    currentBuilderId: function () {
      return this.$route.params.builder_id
        ? String(this.$route.params.builder_id)
        : null;
    },
    expressionPreview: function () {
      if (this.includeBuilders.length === 0) {
        return 'Add at least one included builder';
      }

      var includeNames = this.includeBuilders.map(this.previewName);
      var expression =
        '(' +
        includeNames.join(this.operationText(this.includeOperation)) +
        ')';

      if (this.excludeBuilders.length > 0) {
        expression +=
          ' - (' +
          this.excludeBuilders
            .map(this.previewName)
            .join(this.operationText(this.excludeOperation)) +
          ')';
      }

      return expression;
    },
  },
  created: function () {
    this.fetchBuilders();
    this.updateParams();
  },
  methods: {
    defaultParams: function () {
      return {
        include: {
          builders: [],
          operation: 'union',
        },
        exclude: {
          builders: [],
          operation: 'union',
        },
      };
    },
    fetchBuilders: async function () {
      this.buildersLoadError = '';
      this.buildersFetchFinished = false;

      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/selection/simple/lists`,
          {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
          }
        );
        if (!response.ok) {
          this.buildersLoadError =
            'Unable to load builders. Please try again later.';
          return;
        }

        const data = await response.json();
        this.allBuilders = data.builders.map((builder) => ({
          ...builder,
          id: String(builder.id),
        }));
      } catch (e) {
        this.buildersLoadError =
          'Unable to load builders. Please try again later.';
      } finally {
        this.buildersFetchFinished = true;
      }
    },
    onBuilderLoaded: function (builder) {
      var include = builder.params.include || {};
      var exclude = builder.params.exclude || {};

      this.includeBuilders = (include.builders || []).map(String);
      this.includeOperation = include.operation || 'union';
      this.excludeBuilders = (exclude.builders || []).map(String);
      this.excludeOperation = exclude.operation || 'union';
      this.updateParams();
    },
    onBeforeSubmit: function (builder) {
      var project =
        builder && builder.project ? builder.project : 'en.wikipedia.org';
      var includeProjectErrors = this.buildersOutsideProject(
        this.includeBuilders,
        project
      );
      var excludeProjectErrors = this.buildersOutsideProject(
        this.excludeBuilders,
        project
      );

      this.includeValidationMessage = '';
      this.excludeValidationMessage = '';

      if (this.includeBuilders.length === 0) {
        this.includeValidationMessage =
          'Please add at least one builder to include';
      } else if (includeProjectErrors.length) {
        this.includeValidationMessage = this.projectMismatchMessage(
          'Included',
          includeProjectErrors,
          project
        );
      }

      if (excludeProjectErrors.length) {
        this.excludeValidationMessage = this.projectMismatchMessage(
          'Excluded',
          excludeProjectErrors,
          project
        );
      }

      this.setSelectValidity('includeSelect', this.includeValidationMessage);
      this.setSelectValidity('excludeSelect', this.excludeValidationMessage);
      this.updateParams();
    },
    onValidationError: function (data) {
      this.invalidItems = data.items.invalid.join('\n');
      this.includeValidationMessage = 'Combinator configuration is not valid';
      this.setSelectValidity('includeSelect', this.includeValidationMessage);
    },
    // TODO : just refactor into one function
    availableIncludeBuilders: function (project) {
      return this.availableBuildersFor(project, this.includeBuilders);
    },
    availableExcludeBuilders: function (project) {
      return this.availableBuildersFor(project, this.excludeBuilders);
    },
    hasNoEligibleBuilders: function (project) {
      return (
        this.buildersFetchFinished &&
        !this.buildersLoadError &&
        this.availableIncludeBuilders(project).length === 0
      );
    },
    availableBuildersFor: function (project, selectedIds) {
      return this.allBuilders.filter((builder) => {
        return (
          builder.id !== this.currentBuilderId &&
          builder.model !== COMBINATOR_MODEL &&
          builder.project === project &&
          !selectedIds.includes(builder.id)
        );
      });
    },
    builderById: function (builderId) {
      return this.allBuilders.find((builder) => builder.id === builderId);
    },
    builderLabel: function (builderId) {
      var builder = this.builderById(builderId);
      if (!builder) {
        return builderId.substring(0, 8);
      }
      return `${builder.name} (${this.modelName(builder.model)})`;
    },
    builderOptionLabel: function (builder) {
      return `${builder.name} (${this.modelName(
        builder.model
      )}, ${this.statusText(builder)})`;
    },
    // better namming
    modelName: function (model) {
      var fragment = model.split('.').pop();
      var labels = {
        book: 'Book',
        petscan: 'Petscan',
        simple: 'Simple',
        sparql: 'SPARQL',
        wikiproject: 'WikiProject',
      };
      return labels[fragment] || fragment;
    },
    statusText: function (builder) {
      if (builder.s_status === 'FAILED') {
        return 'failed';
      }
      if (builder.s_status === 'CAN_RETRY') {
        return 'retryable failure';
      }
      if (builder.s_status === 'OK' || builder.s_url) {
        return 'ready';
      }
      return 'not materialized';
    },
    previewName: function (builderId) {
      var builder = this.builderById(builderId);
      if (!builder) {
        return builderId.substring(0, 8);
      }
      return `"${builder.name}"`;
    },
    operationText: function (operation) {
      return operation === 'intersection' ? ' INTERSECTION ' : ' UNION ';
    },
    addSelectedBuilder: function (group) {
      var dropdownKey = `${group}Dropdown`;
      var buildersKey = `${group}Builders`;
      var validationKey = `${group}ValidationMessage`;
      var selectRef = `${group}Select`;
      var builderId = this[dropdownKey];

      if (builderId && !this[buildersKey].includes(builderId)) {
        this[buildersKey].push(builderId);
        this[dropdownKey] = '';
        this[validationKey] = '';
        this.setSelectValidity(selectRef, '');
        this.updateParams();
      }
    },
    removeSelectedBuilder: function (group, builderId) {
      var buildersKey = `${group}Builders`;
      this[buildersKey] = this[buildersKey].filter((id) => id !== builderId);
      this.updateParams();
    },
    buildersOutsideProject: function (builderIds, project) {
      return builderIds
        .map(this.builderById)
        .filter((builder) => builder && builder.project !== project);
    },
    projectMismatchMessage: function (groupName, builders, project) {
      var names = builders
        .map((builder) => `${builder.name} (${builder.project})`)
        .join(', ');
      return `${groupName} builders must use ${project}. Remove or replace: ${names}`;
    },
    setSelectValidity: function (refName, message) {
      if (this.$refs[refName]) {
        this.$refs[refName].setCustomValidity(message);
      }
    },
    updateParams: function () {
      this.params = {
        include: {
          builders: [...this.includeBuilders],
          operation: this.includeOperation,
        },
        exclude: {
          builders: [...this.excludeBuilders],
          operation: this.excludeOperation,
        },
      };
    },
  },
  watch: {
    includeOperation: function () {
      this.updateParams();
    },
    excludeOperation: function () {
      this.updateParams();
    },
  },
};
</script>

<style scoped>
.combinator-card {
  width: 100%;
}

.selected-builders {
  display: flex;
  flex-wrap: wrap;
}

.combinator-badge {
  align-items: center;
  display: inline-flex;
  font-size: 0.9em;
  margin: 0 0.5rem 0.5rem 0;
  padding: 0.5rem;
}

.remove-builder {
  background: none;
  border: 0;
  color: white;
  font-size: 1rem;
  line-height: 1;
  margin-left: 0.5rem;
  padding: 0;
}

.combinator-preview {
  background: #f8f9fa;
  width: 100%;
}

.combinator-preview code {
  color: #d63384;
  font-size: 1.05em;
}
</style>
