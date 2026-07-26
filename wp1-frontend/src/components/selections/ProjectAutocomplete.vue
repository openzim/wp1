<template>
  <div class="relative">
    <input
      ref="input"
      v-model="search"
      type="text"
      class="wp1r-input h-8 w-full"
      :placeholder="placeholder"
      autocomplete="off"
      @input="onChange"
      @keydown.down.prevent="focusList"
      @keydown.enter.prevent="onEnter"
    />
    <ul
      v-show="isOpen && results.length"
      ref="list"
      class="absolute z-10 m-0 max-h-72 w-full list-none overflow-auto rounded-b border border-t-0 border-border bg-surface p-0 shadow-card"
    >
      <li
        v-for="(result, i) of results.slice(0, 50)"
        :key="i"
        tabindex="0"
        class="cursor-pointer px-[9px] py-1.5 text-[13px] hover:bg-surface-muted focus:bg-accent-tint focus:outline-none"
        @click="selectResult(result.name)"
        @keydown.enter.prevent="selectResult(result.name)"
        @keydown.down.prevent="focusNext"
        @keydown.up.prevent="focusPrev"
      >
        {{ result.name }}
      </li>
    </ul>
  </div>
</template>

<script>
// Tailwind-styled sibling of Autocomplete.vue for the redesigned Selections
// screens. Same data source (/v1/projects/), same select-on-pick contract.
export default {
  name: 'ProjectAutocomplete',
  props: {
    placeholder: { type: String, default: 'WikiProject name' },
  },
  data: function () {
    return {
      isOpen: false,
      projects: [],
      results: [],
      search: '',
    };
  },
  created: async function () {
    const response = await fetch(`${import.meta.env.VITE_API_URL}/projects/`);
    this.projects = await response.json();
  },
  methods: {
    filterResults: function () {
      if (this.search === '' || !this.projects) {
        this.results = [];
        return;
      }
      this.results = this.projects.filter(
        (project) =>
          project.name.toLowerCase().indexOf(this.search.toLowerCase()) !== -1
      );
    },
    onChange: function () {
      this.filterResults();
      this.isOpen = this.search !== '';
    },
    onEnter: function () {
      if (this.results.length >= 1) {
        this.selectResult(this.results[0].name);
      }
    },
    selectResult: function (name) {
      this.search = '';
      this.results = [];
      this.isOpen = false;
      this.$emit('select', name);
      this.$refs.input.focus();
    },
    focusList: function () {
      if (this.results.length) {
        this.isOpen = true;
        this.$nextTick(() => this.$refs.list.children[0].focus());
      }
    },
    focusNext: function (event) {
      const next = event.target.nextElementSibling;
      if (next) {
        next.focus();
      }
    },
    focusPrev: function (event) {
      const prev = event.target.previousElementSibling;
      if (prev) {
        prev.focus();
      } else {
        this.$refs.input.focus();
      }
    },
  },
};
</script>
