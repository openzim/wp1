<template>
  <div ref="root" class="relative" @focusout="onFocusOut">
    <input
      :id="inputId"
      ref="input"
      v-model="search"
      type="text"
      role="combobox"
      class="wp1r-input w-full"
      :class="inputClass"
      :aria-label="ariaLabel"
      :aria-expanded="isOpen && results.length > 0"
      :aria-controls="listId"
      autocomplete="off"
      spellcheck="false"
      @focus="$event.target.select()"
      @click="open"
      @input="onInput"
      @keydown.down.prevent="focusList"
      @keydown.enter.prevent="onEnter"
      @keydown.esc="close"
    />
    <ul
      v-show="isOpen && results.length"
      :id="listId"
      ref="list"
      role="listbox"
      class="absolute z-10 m-0 max-h-72 w-full min-w-[220px] list-none overflow-auto rounded-b border border-t-0 border-border bg-surface p-0 shadow-card"
    >
      <li
        v-for="site of results"
        :key="site"
        role="option"
        tabindex="0"
        :aria-selected="site === modelValue"
        class="flex cursor-pointer items-baseline justify-between gap-3 px-[9px] py-1.5 text-[13px] hover:bg-surface-muted focus:bg-accent-tint focus:outline-none"
        @click="selectSite(site)"
        @keydown.enter.prevent="selectSite(site)"
        @keydown.esc="closeAndRefocus"
        @keydown.down.prevent="focusNext"
        @keydown.up.prevent="focusPrev"
      >
        <span>{{ site }}</span>
        <span class="font-mono text-xs text-ink-3">{{ dbnames[site] }}</span>
      </li>
    </ul>
  </div>
</template>

<script>
// Only emits projects from the list, so typed text never becomes the project.
export default {
  name: 'SitePicker',
  props: {
    modelValue: { type: String, required: true },
    sites: { type: Array, required: true },
    dbnames: { type: Object, default: () => ({}) },
    inputId: { type: String, required: true },
    ariaLabel: { type: String, default: null },
    inputClass: { type: String, default: 'h-8' },
  },
  emits: ['update:modelValue'],
  data: function () {
    return {
      isOpen: false,
      query: '',
      search: this.modelValue,
    };
  },
  computed: {
    listId: function () {
      return `${this.inputId}-options`;
    },
    results: function () {
      const query = this.query.trim().toLowerCase();
      if (!query) {
        return this.sites;
      }
      return this.sites.filter(
        (site) =>
          site.toLowerCase().includes(query) ||
          (this.dbnames[site] || '').toLowerCase().includes(query)
      );
    },
  },
  watch: {
    modelValue: function () {
      this.search = this.modelValue;
    },
  },
  methods: {
    open: function () {
      this.query = '';
      this.isOpen = true;
    },
    onInput: function () {
      this.query = this.search;
      this.isOpen = true;
    },
    onEnter: function () {
      if (this.isOpen && this.results.length) {
        this.selectSite(this.results[0]);
      }
    },
    onFocusOut: function (event) {
      if (!this.$refs.root.contains(event.relatedTarget)) {
        this.close();
      }
    },
    close: function () {
      this.isOpen = false;
      this.search = this.modelValue;
    },
    closeAndRefocus: function () {
      this.close();
      this.$refs.input.focus();
    },
    selectSite: function (site) {
      this.$emit('update:modelValue', site);
      this.search = site;
      this.isOpen = false;
      this.$refs.input.focus();
    },
    focusList: function () {
      if (!this.isOpen) {
        this.open();
      }
      if (!this.results.length) {
        return;
      }
      this.$nextTick(() => this.$refs.list.children[0].focus());
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
