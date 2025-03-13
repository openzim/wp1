<template>
  <div>
    <p v-if="!hideInstructions">
      Use the autocomplete search box below to search for a project in order to
      display its summary table.
    </p>
    <div v-if="this.$route.path.startsWith('/update')">
      <p>
        To begin a manual update, use the autocomplete search box below to find
        the project you wish to update.
      </p>
      <p>
        <b
          >Note: This tool can only perform manual updates once per hour at
          most. It also cannot perform an update until all pending updates are
          complete.</b
        >
      </p>
    </div>
    <div class="input-group">
      <input
        v-model="search"
        @input="onChange"
        v-on:keyup.down="focusList()"
        ref="input"
        class="form-control auto-input search"
        type="text"
        placeholder="Project name"
      />
      <button v-on:click="onButtonClick()" class="btn btn-primary">
        Select Project
      </button>
    </div>
    <ul tabindex="0" ref="list" class="results" v-show="isOpen">
      <li
        v-for="(result, i) of results"
        :key="i"
        v-on:click="selectResult"
        v-on:keyup.enter="selectResult"
        v-on:keyup.down="focusNext"
        v-on:keyup.up="focusPrev"
        class="result"
        tabindex="0"
      >
        {{ result.name }}
      </li>
    </ul>
  </div>
</template>

<script>
export default {
  name: 'auto-complete',
  props: ['incomingSearch', 'hideInstructions'],
  data: function () {
    return {
      isOpen: false,
      projects: [],
      results: [],
      search: '',
    };
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
    $route: function (to) {
      if (to.path == '/compare') {
        this.search = '';
      }
    },
  },
};
</script>

<style scoped>
.auto-input {
  border-bottom-right-radius: 0;
  border-bottom-left-radius: 0;
}

.results {
  border: 1px solid #ddd;
  border-top: none;
  box-sizing: border-box;
  cursor: pointer;
  list-style: none;
  max-height: 20rem;
  overflow: auto;
  padding: 0;
  text-align: left;
  z-index: 1;
  background: white;
  position: absolute;
  width: 95%;
}

.result {
  padding: 0.375rem 0.75rem;
}

.result:hover,
.result:focus {
  background-color: #ddd;
  outline: none;
}
</style>
