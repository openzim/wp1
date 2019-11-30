<template>
  <div>
    <div class="input-group">
      <input v-model="search" @input="onChange" v-on:keyup.down="focusList()"
             ref="input" class="form-control auto-input" type="text"
             placeholder="Project name"/>
    </div>
      <ul tabindex="0" ref="list" class="results" v-show="isOpen">
        <li v-for="(result, i) of results" :key="i"
            v-on:click="selectResult" v-on:keyup.enter="selectResult"
            v-on:keyup.down="focusNext" v-on:keyup.up="focusPrev"
            class="result" tabindex="0">
          {{result.name}}
        </li>
      </ul>
  </div>
</template>

<script>

export default {
  name: 'autocomplete',
  data: function() {
    return {
      isOpen: false,
      projects: [],
      results: [],
      search: '',
    }
  },
  created: async function() {
    this.projects = await this.getProjects();
  },
  methods: {
    filterResults: function() {
      window.console.log(this.projects);
      if (this.search === '' || !this.projects) {
        this.results = [];
        return;
      }
      this.results = this.projects.filter(project => {
        return project.name.toLowerCase().indexOf(
          this.search.toLowerCase()) > -1
      });
    },
    focusList: function() {
      if (!this.results.length) {
        return;
      }
      this.isOpen = true;
      this.$refs.list.children[0].focus();
    },
    focusNext: function(event) {
      var nodes = Array.prototype.slice.call(this.$refs.list.children);
      var currentIndex = nodes.indexOf(event.target);
      if (currentIndex < this.results.length - 1) {
        this.$refs.list.children[currentIndex + 1].focus();
      }
    },
    focusPrev: function() {
      var nodes = Array.prototype.slice.call(this.$refs.list.children);
      var currentIndex = nodes.indexOf(event.target);
      if (currentIndex > 0) {
        this.$refs.list.children[currentIndex - 1].focus();
      } else {
        this.isOpen = false;
        this.$refs.input.focus();
      }
    },
    getProjects: async function() {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/`);
      return await response.json();
    },
    onChange: function() {
      if (this.search === '') {
        this.isOpen = false;
      } else {
        this.isOpen = true;
      }
      this.filterResults();
    },
    selectResult: function(event) {
      this.search = event.target.innerText;
      this.isOpen = false;
      this.filterResults();
    }
  }
}
</script>

<style scoped>
  .auto-input {
    border-bottom-right-radius: 0;
    border-bottom-left-radius: 0;
  }

  .results {
    border: 1px solid #ddd;
    border-top: none;
    box-style: border-box;
    cursor: pointer;
    list-style: none;
    padding: 0;
    text-align: left;
  }

  .result {
    padding: .375rem .75rem;
  }

  .result:hover,
  .result:focus {
    background-color: #ddd;
    outline: none;
  }
</style>
