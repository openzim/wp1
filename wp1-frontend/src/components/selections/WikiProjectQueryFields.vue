<template>
  <div class="flex flex-col gap-3.5">
    <div id="query-wikiproject">
      <label class="mb-1 block text-xs font-medium text-ink-2"
        >WikiProject</label
      >
      <div v-if="modelValue.wikiproject" class="flex flex-wrap gap-1.5">
        <span
          class="inline-flex items-center gap-1.5 rounded-[3px] border border-border-strong bg-surface px-2 py-1 text-[13px]"
        >
          {{ modelValue.wikiproject }}
          <button
            type="button"
            class="flex h-6 w-6 shrink-0 cursor-pointer items-center justify-center border-0 bg-transparent p-0 leading-none text-ink-4 hover:text-danger"
            :aria-label="'Remove ' + modelValue.wikiproject"
            @click="setProject('')"
          >
            ×
          </button>
        </span>
      </div>
      <ProjectAutocomplete v-else @select="setProject" />
    </div>
    <div class="grid gap-3.5 sm:grid-cols-3">
      <div>
        <label
          for="query-quality"
          class="mb-1 block text-xs font-medium text-ink-2"
          >Quality</label
        >
        <select
          id="query-quality"
          :value="modelValue.quality"
          class="wp1r-select h-8 w-full"
          @change="update('quality', $event.target.value)"
        >
          <option value="">Any</option>
          <option v-for="cls in qualityOptions" :key="cls" :value="cls">
            {{ cls }}
          </option>
        </select>
      </div>
      <div>
        <label
          for="query-importance"
          class="mb-1 block text-xs font-medium text-ink-2"
          >Importance</label
        >
        <select
          id="query-importance"
          :value="modelValue.importance"
          class="wp1r-select h-8 w-full"
          @change="update('importance', $event.target.value)"
        >
          <option value="">Any</option>
          <option v-for="cls in importanceOptions" :key="cls" :value="cls">
            {{ cls }}
          </option>
        </select>
      </div>
      <div>
        <label
          for="query-pattern"
          class="mb-1 block text-xs font-medium text-ink-2"
          >Title contains</label
        >
        <input
          id="query-pattern"
          :value="modelValue.pattern"
          type="text"
          class="wp1r-input h-8 w-full"
          placeholder="Any"
          @input="update('pattern', $event.target.value)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import ProjectAutocomplete from './ProjectAutocomplete.vue';

export default {
  name: 'WikiProjectQueryFields',
  components: { ProjectAutocomplete },
  props: {
    modelValue: { type: Object, required: true },
  },
  emits: ['update:modelValue'],
  data: function () {
    return {
      qualities: [],
      importances: [],
    };
  },
  computed: {
    qualityOptions: function () {
      return this.withCurrent(this.qualities, this.modelValue.quality);
    },
    importanceOptions: function () {
      return this.withCurrent(this.importances, this.modelValue.importance);
    },
  },
  watch: {
    'modelValue.wikiproject': function () {
      this.fetchClasses();
    },
  },
  created: function () {
    this.fetchClasses();
  },
  methods: {
    withCurrent: function (options, current) {
      return current && !options.includes(current)
        ? [current, ...options]
        : options;
    },
    update: function (key, value) {
      this.$emit('update:modelValue', { ...this.modelValue, [key]: value });
    },
    setProject: function (project) {
      this.$emit('update:modelValue', {
        ...this.modelValue,
        wikiproject: project,
        quality: '',
        importance: '',
      });
    },
    fetchClasses: async function () {
      this.qualities = [];
      this.importances = [];
      const project = this.modelValue.wikiproject;
      if (!project) {
        return;
      }
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${encodeURIComponent(
          project.replace(/ /g, '_')
        )}/table`
      );
      if (!response.ok || project !== this.modelValue.wikiproject) {
        return;
      }
      const data = (await response.json()).table_data;
      this.qualities = data.ordered_rows;
      this.importances = data.ordered_cols;
    },
  },
};
</script>
