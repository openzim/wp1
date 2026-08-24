<template>
  <div class="flex items-center gap-2">
    <span v-if="label" class="wp1r-microlabel shrink-0">{{ label }}</span>
    <div class="relative min-w-0 flex-1">
      <input
        v-model="search"
        @input="onChange"
        v-on:keyup.down="focusList()"
        ref="input"
        class="search wp1r-input w-full"
        :class="controlSize"
        type="text"
        :placeholder="placeholder"
        :aria-label="label || 'Project name'"
      />
      <ul
        tabindex="0"
        ref="list"
        v-show="isOpen"
        class="results absolute left-0 right-0 top-full z-10 m-0 mt-1 max-h-80 list-none overflow-auto rounded border border-border bg-surface p-0 shadow-card"
      >
        <li
          v-for="(result, i) of results"
          :key="i"
          v-on:click="selectResult"
          v-on:keyup.enter="selectResult"
          v-on:keyup.down="focusNext"
          v-on:keyup.up="focusPrev"
          class="result cursor-pointer border-b border-border-row px-[10px] py-[7px] text-[13px] last:border-b-0 hover:bg-surface-muted focus:bg-accent-tint focus:outline-none"
          tabindex="0"
        >
          {{ result.name }}
        </li>
      </ul>
    </div>
    <button
      type="button"
      v-on:click="onButtonClick()"
      class="shrink-0 px-3"
      :class="[
        buttonVariant === 'secondary'
          ? 'wp1r-btn-secondary'
          : 'wp1r-btn-primary',
        controlSize,
      ]"
    >
      {{ buttonLabel }}
    </button>
  </div>
</template>

<script>
export default {
  name: 'auto-complete',
  props: {
    incomingSearch: String,
    // Optional inline microlabel rendered before the input (e.g. "Project").
    label: String,
    // 'md' (32px, compact pages) or 'lg' (34px, the Index hero search).
    size: { type: String, default: 'md' },
    buttonLabel: { type: String, default: 'Select project' },
    buttonVariant: { type: String, default: 'primary' },
    placeholder: { type: String, default: 'Project name' },
  },
  data: function () {
    return {
      isOpen: false,
      projects: [],
      results: [],
      search: '',
    };
  },
  computed: {
    controlSize: function () {
      return this.size === 'lg' ? 'h-[34px] text-[14px]' : 'h-8';
    },
  },
  created: async function () {
    this.projects = await this.getProjects();
    this.updateFromIncomingSearch(this.incomingSearch);
  },
  methods: {
    filterResults: function () {
      if (this.search === '' || !this.projects) {
        this.results = [];
        return;
      }
      this.results = this.projects.filter((project) => {
        return (
          project.name.toLowerCase().indexOf(this.search.toLowerCase()) !== -1
        );
      });
    },
    focusList: function () {
      if (!this.results.length) {
        this.results = this.projects;
      }
      this.isOpen = true;
      this.$refs.list.children[0].focus();
    },
    focusNext: function (event) {
      var nodes = Array.prototype.slice.call(this.$refs.list.children);
      var currentIndex = nodes.indexOf(event.target);
      if (currentIndex < this.results.length - 1) {
        this.$refs.list.children[currentIndex + 1].focus();
      }
    },
    focusPrev: function () {
      var nodes = Array.prototype.slice.call(this.$refs.list.children);
      var currentIndex = nodes.indexOf(event.target);
      if (currentIndex > 0) {
        this.$refs.list.children[currentIndex - 1].focus();
      } else {
        this.isOpen = false;
        this.$refs.input.focus();
      }
    },
    getProjects: async function () {
      if (this.projects.length !== 0) {
        return this.projects;
      }
      const response = await fetch(`${import.meta.env.VITE_API_URL}/projects/`);
      return await response.json();
    },
    onChange: function () {
      if (this.search === '') {
        this.isOpen = false;
      } else {
        this.isOpen = true;
      }
      this.filterResults();
    },
    makeSelection: function () {
      this.isOpen = false;
      this.filterResults();
      this.$emit('select-project', this.search);
    },
    onButtonClick: function () {
      if (this.results.length == 1) {
        this.search = this.results[0].name;
      }
      this.makeSelection();
    },
    selectResult: function (event) {
      this.search = event.target.innerText;
      this.makeSelection();
    },
    updateFromIncomingSearch: function (val) {
      if (!!val && val !== this.search) {
        const found = this.projects.filter((project) => {
          return project.name == val;
        });
        if (found.length === 1) {
          this.search = val;
          this.onChange();
          this.makeSelection();
        }
      }
    },
  },
  watch: {
    incomingSearch: function (val) {
      this.updateFromIncomingSearch(val);
    },
    // Returning to a bare picker page (index, compare) resets the control.
    $route: function (to) {
      if (to.path == '/compare' || to.path == '/') {
        this.search = '';
      }
    },
  },
};
</script>
