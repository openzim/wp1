<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div v-if="notFound">
      <div id="404" class="col-lg-6 m-4">
        <h2>404 Not Found</h2>
        Sorry, the builder (SPARQL query list) with that ID either doesn't exist
        or isn't owned by you.
      </div>
    </div>
    <div v-else-if="serverError">
      <h2>500 Server error</h2>
      Something went wrong and we couldn't retrieve the builder (SPARQL query
      list) with that ID. You might try again later.
    </div>
    <div v-else class="row">
      <div class="col-lg-6 col-md-9 m-4">
        <h2 v-if="!isEditing" class="ml-4">New SPARQL Selection</h2>
        <h2 v-else class="ml-4">Editing SPARQL Selection</h2>
        <div v-if="!isEditing" class="ml-4 mb-4">
          Use this tool to create an article selection list for the Wikipedia
          project of your choice, using a SPARQL query. The query can either be
          entered directly or provided via a Wikidata query service URL. Your
          selection will be saved in public cloud storage and can be accessed
          through URLs that will be provided once it has been saved.
        </div>

        <form
          ref="form"
          v-on:submit.prevent="onSubmit"
          class="needs-validation"
          novalidate
        >
          <div ref="form_group" class="form-group">
            <div id="project" class="m-4">
              <label>Project</label>
              <select v-model="builder.project" class="custom-select my-list">
                <option v-if="wikiProjects.length == 0" selected>
                  en.wikipedia.org
                </option>
                <option v-for="item in wikiProjects" v-bind:key="item">
                  {{ item }}
                </option>
              </select>
            </div>
            <div id="listName" class="m-4">
              <label for="listName">Selection Name</label>
              <input
                v-on:blur="validationOnBlur"
                v-model="builder.name"
                type="text"
                placeholder="My List"
                class="form-control my-list"
                required
              />
              <div class="invalid-feedback">
                Please provide a valid selection name
              </div>
            </div>
            <div id="items" class="form-group m-4">
              <label for="items">Query</label>
              <textarea
                v-on:blur="validationOnBlur"
                v-model="builder.params.query"
                :placeholder="
                  '#Rock bands that start with &quot;M&quot;\n' +
                  'SELECT ?article ?bandLabel\n' +
                  'WHERE\n' +
                  '{\n' +
                  '  ?article wdt:P31 wd:Q5741069 .\n' +
                  '  ?article rdfs:label ?bandLabel .\n' +
                  '  FILTER(LANG(?bandLabel) = &quot;en&quot;) .\n' +
                  '  FILTER(STRSTARTS(?bandLabel, \'M\')) .\n}'
                "
                class="form-control my-list"
                rows="13"
                required
              ></textarea>
              <div class="invalid-feedback">Please provide a valid query</div>
            </div>
            <div id="queryVariable" class="m-4">
              <label for="queryVariable">Query variable</label>
              <p class="explanation">
                The variable in your query that represents the Wikidata entity
                whose article URLs should be retrieved. This will default to
                <span style="white-space: nowrap">"?article"</span>, for when
                your query already selects a variable named "?article". Note:
                this variable must appear in the SELECT clause of your query.
              </p>
              <input
                v-on:blur="validationOnBlur"
                v-model="builder.params.queryVariable"
                type="text"
                placeholder="?article"
                class="form-control my-list"
              />
            </div>
          </div>
          <div
            v-if="this.success == false || this.deleteSuccess == false"
            id="invalid_articles"
            class="form-group m-4"
          >
            <div class="errors">{{ errors }}</div>
            <textarea
              v-if="
                this.success == false && this.invalid_article_names.length > 0
              "
              class="form-control my-list is-invalid"
              rows="6"
              ref="invalid"
              v-model="invalid_article_names"
            ></textarea>
          </div>
          <div v-if="isEditing">
            <div>
              <button
                id="updateListButton"
                type="submit"
                class="btn-primary ml-4"
              >
                Update List
              </button>
            </div>
            <div class="mt-4">
              <button
                v-on:click.prevent="onDelete"
                id="deleteListButton"
                type="button"
                class="btn-danger ml-4"
              >
                Delete List
              </button>
            </div>
          </div>
          <button
            v-else
            id="saveListButton"
            type="submit"
            class="btn-primary ml-4"
          >
            Save List
          </button>
        </form>
      </div>
    </div>
    <div v-if="!notFound" class="row">
      <div class="col-lg-6 col-md-9 m-4"></div>
    </div>
  </div>
  <div v-else>
    <LoginRequired></LoginRequired>
  </div>
</template>

<script>
import SecondaryNav from './SecondaryNav.vue';
import LoginRequired from './LoginRequired';

export default {
  components: { SecondaryNav, LoginRequired },
  name: 'SparqlList',
  data: function () {
    return {
      notFound: false,
      serverError: false,
      wikiProjects: [],
      success: true,
      deleteSuccess: true,
      valid_article_names: '',
      invalid_article_names: '',
      errors: '',
      builder: {
        params: {
          query: '',
          queryVariable: '',
        },
        name: '',
        project: 'en.wikipedia.org',
        model: 'wp1.selection.models.sparql',
      },
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$root.$data.isLoggedIn;
    },
    isEditing: function () {
      return !!this.builderId;
    },
    builderId: function () {
      return this.$route.params.builder_id;
    },
  },
  created: function () {
    this.getWikiProjects();
    if (this.isEditing) {
      this.getBuilder();
    }
  },
  watch: {
    builderId: function () {
      this.getBuilder();
    },
  },
  methods: {
    getWikiProjects: async function () {
      const response = await fetch(`${process.env.VUE_APP_API_URL}/sites/`);
      var data = await response.json();
      this.wikiProjects = data.sites;
    },
    getBuilder: async function () {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/builders/${this.$route.params.builder_id}`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }
      );
      if (response.status == 404) {
        this.notFound = true;
      } else if (!response.ok) {
        this.serverError = true;
      } else {
        this.notFound = false;
        this.builder = await response.json();
      }
    },
    onSubmit: async function () {
      const form = this.$refs.form;
      if (!form.checkValidity()) {
        this.$refs.form_group.classList.add('was-validated');
        return;
      }

      let postUrl = '';
      if (this.isEditing) {
        postUrl = `${process.env.VUE_APP_API_URL}/builders/${this.$route.params.builder_id}`;
      } else {
        postUrl = `${process.env.VUE_APP_API_URL}/builders/`;
      }

      const response = await fetch(postUrl, {
        headers: { 'Content-Type': 'application/json' },
        method: 'post',
        credentials: 'include',
        body: JSON.stringify(this.builder),
      });

      if (!response.ok) {
        this.success = false;
        this.errors = 'An unknown server error has occurred.';
        return;
      }

      var data = await response.json();
      this.success = data.success;
      if (this.success) {
        this.$router.push('/selections/user');
        return;
      }

      // Otherwise there were errors with the POST
      this.$refs.form_group.classList.add('was-validated');
      this.builder.articles = data.items.valid.join('\n');
      this.invalid_article_names = data.items.invalid.join('\n');
      this.errors = data.items.errors.join(', ');
    },
    validationOnBlur: function (event) {
      if (event.target.value) {
        event.target.classList.remove('is-invalid');
      } else {
        event.target.classList.add('is-invalid');
      }
    },
    onDelete: async function () {
      if (
        !window.confirm(
          'Really delete this list? The definition and all downloadable selections will be permanently deleted.'
        )
      ) {
        return;
      }

      const postUrl = `${process.env.VUE_APP_API_URL}/builders/${this.$route.params.builder_id}/delete`;
      const response = await fetch(postUrl, {
        method: 'post',
        credentials: 'include',
      });

      if (response.status == 200) {
        this.$router.push('/selections/user');
        return;
      } else if (response.status == 404 || response.status == 401) {
        this.deleteSuccess = false;
        this.errors =
          "Could not delete this list. Check that the list still exists and you're logged in as its owner.";
        return;
      }
    },
  },
};
</script>

<style scoped>
.errors {
  color: red;
}

.explanation {
  color: #777;
}
</style>
