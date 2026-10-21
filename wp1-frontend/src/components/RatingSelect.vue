<!-- Per-project Quality/Importance selects used by the Compare page.
     Auto-emits on change; disabled until a project is chosen. -->
<template>
  <div class="flex flex-wrap items-center gap-3">
    <span class="flex items-center gap-1.5">
      <label :for="qualityId" class="wp1r-microlabel">Quality</label>
      <select
        :id="qualityId"
        :aria-label="qualityAriaLabel"
        :disabled="!projectId"
        @change="onSelectChange()"
        class="wp1r-select h-7 pl-2 disabled:cursor-not-allowed disabled:opacity-50"
        ref="qualitySelect"
      >
        <option
          v-for="(item, key) in categoryLinks.quality"
          :value="key"
          v-bind:key="key"
          :selected="selectedQuality == key"
        >
          {{ item.text ? item.text : item }}
        </option>
      </select>
    </span>
    <span class="flex items-center gap-1.5">
      <label :for="importanceId" class="wp1r-microlabel">Importance</label>
      <select
        :id="importanceId"
        :aria-label="importanceAriaLabel"
        :disabled="!projectId"
        @change="onSelectChange()"
        class="wp1r-select h-7 pl-2 disabled:cursor-not-allowed disabled:opacity-50"
        ref="importanceSelect"
      >
        <option
          v-for="(item, key) in categoryLinks.importance"
          :value="key"
          v-bind:key="key"
          :selected="selectedImportance == key"
        >
          {{ item.text ? item.text : item }}
        </option>
      </select>
    </span>
  </div>
</template>

<script>
export default {
  name: 'rating-select',
  props: [
    'initialQuality',
    'initialImportance',
    'projectId',
    'idPrefix',
    'labelPrefix',
  ],
  data: function () {
    return {
      categoryLinks: {},
    };
  },
  created: function () {
    this.getCategoryLinks();
  },
  computed: {
    selectedQuality: function () {
      return this.initialQuality || '';
    },
    selectedImportance: function () {
      return this.initialImportance || '';
    },
    qualityId: function () {
      return this.idPrefix ? `${this.idPrefix}-quality` : 'quality-select';
    },
    importanceId: function () {
      return this.idPrefix ? `${this.idPrefix}-importance` : 'importance-select';
    },
    qualityAriaLabel: function () {
      return this.labelPrefix ? `${this.labelPrefix} Quality` : 'Quality';
    },
    importanceAriaLabel: function () {
      return this.labelPrefix
        ? `${this.labelPrefix} Importance`
        : 'Importance';
    },
  },
  watch: {
    projectId: async function () {
      await this.getCategoryLinks();
      this.onSelectChange();
    },
    $route: function (to) {
      if (to.path == '/compare') {
        this.categoryLinks = {};
      }
    },
  },
  methods: {
    getCategoryLinks: async function () {
      if (!this.projectId) {
        return;
      }
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${
          this.projectId
        }/category_links/sorted`
      );
      const links = await response.json();
      links.quality[''] = 'None Selected';
      links.importance[''] = 'None Selected';
      this.categoryLinks = links;
    },
    onSelectChange: function () {
      const quality = this.$refs.qualitySelect.value;
      const importance = this.$refs.importanceSelect.value;

      this.$emit('rating-select', { quality, importance });
    },
  },
};
</script>
