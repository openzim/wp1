<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div v-if="notFound">
      <div id="404" class="col-lg-6 m-4">
        <h2>404 Not Found</h2>
        Sorry, the list with that ID either doesn't exist or isn't owned by you.
      </div>
    </div>
    <div v-else-if="serverError">
      <h2>500 Server error</h2>
      Something went wrong and we couldn't retrieve the list with that ID. You
      might try again later.
    </div>
    <div v-else>
      <div class="row">
        <div class="col-lg-6 col-md-9 mx-4">
          <h2 v-if="!isEditing" class="ml-4">New {{ listName }}</h2>
          <h2 v-else class="ml-4">Editing {{ listName }}</h2>
          <div v-if="!isEditing" class="ml-4">
            <slot name="create-desc"></slot>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-lg-6 col-md-9 mt-2 mb-0 mx-4">
          <div v-if="hasMaterializeErrors" class="mx-4 materialize-error p-4">
            <h4 class="materialize-header">
              There was an error creating your selection
            </h4>
            <div
              v-for="item in builder.selection_errors"
              v-bind:key="item.error_messages[0]"
            >
              <div>
                The following errors occurred when creating the .{{ item.ext }}
                version:
              </div>
              <ul class="materialize-error-list">
                <li v-for="msg in item.error_messages" v-bind:key="msg">
                  {{ msg }}
                </li>
              </ul>
            </div>
            <div v-if="materializeRetryable">
              <div>You can attempt to retry processing this Builder.</div>
            </div>
            <div v-else>
              <div>
                Unfortunately, this error cannot be retried. Please update your
                selection.
              </div>
              <div>
                For more information on creating a selection, see the
                <a href="https://wp1.readthedocs.io/en/latest/user/selections/"
                  >end user documentation</a
                >
              </div>
            </div>
            <div class="py-2">
              <button
                v-on:click="onSubmit"
                class="btn btn-light"
                type="button"
                :disabled="!materializeRetryable || processing"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="row">
        <div class="col-lg-6 col-md-9 mx-4">
          <form
            ref="form"
            v-on:submit.prevent="onSubmit"
            class="needs-validation"
            novalidate
          >
            <div ref="form_group" class="form-group">
              <div id="project" class="mb-4 mx-4">
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
                <label for="listName">List Name</label>
                <input
                  v-on:blur="validationOnBlur"
                  v-model="builder.name"
                  type="text"
                  placeholder="My List"
                  class="form-control my-list"
                  required
                />
                <div class="invalid-feedback">
                  Please provide a valid list name
                </div>
              </div>
              <slot name="extra-params" :success="success"></slot>
            </div>
            <div
              v-if="this.success == false || this.deleteSuccess == false"
              id="invalid_articles"
              class="form-group m-4"
            >
              <div class="errors">{{ errors }}</div>
              <textarea
                v-if="this.success == false && this.computedInvalidItems"
                class="form-control my-list is-invalid"
                rows="6"
                ref="invalid"
                v-model="computedInvalidItems"
              ></textarea>
            </div>
            <div v-if="isEditing">
              <div>
                <button
                  id="updateListButton"
                  type="submit"
                  :disabled="processing"
                  class="btn btn-primary ml-4"
                >
                  Update List
                </button>
                <pulse-loader
                  id="updateLoader"
                  v-if="processing"
                  class="loader"
                  style="display: inline-block"
                  :color="loaderColor"
                  :size="loaderSize"
                ></pulse-loader>
              </div>
              <div class="mt-4">
                <button
                  v-on:click.prevent="onDelete"
                  id="deleteListButton"
                  type="button"
                  class="btn btn-danger ml-4"
                >
                  Delete List
                </button>
              </div>
            </div>
            <div v-else>
              <button
                id="saveListButton"
                :disabled="processing"
                type="submit"
                class="btn-primary ml-4"
              >
                Save List
              </button>
              <pulse-loader
                id="saveLoader"
                v-if="processing"
                class="loader"
                style="display: inline-block"
                :color="loaderColor"
                :size="loaderSize"
              ></pulse-loader>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  <div v-else>
    <LoginRequired></LoginRequired>
  </div>
</template>

<script>
import $ from 'jquery';
$.noConflict();

import PulseLoader from 'vue-spinner/src/PulseLoader.vue';

import SecondaryNav from './SecondaryNav.vue';
import LoginRequired from './LoginRequired.vue';

export default {
  components: { SecondaryNav, LoginRequired, PulseLoader },
  name: 'BaseBuilder',
  props: {
    builderId: String,
    invalidItems: String,
    listName: String,
    model: String,
    params: Object,
    serializeParams: Function,
  },
  data: function () {
    return {
      notFound: false,
      serverError: false,
      wikiProjects: [],
      processing: false,
      loaderColor: '#007bff',
      loaderSize: '.75rem',
      success: true,
      deleteSuccess: true,
      errors: '',
      builder: {
        name: '',
        project: 'en.wikipedia.org',
        selection_errors: [],
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
    computedInvalidItems: function () {
      return this.invalidItems;
    },
    hasMaterializeErrors: function () {
      return (
        this.isEditing &&
        this.builder.selection_errors &&
        this.builder.selection_errors.length > 0
      );
    },
    materializeRetryable: function () {
      return (
        this.isEditing &&
        !this.builder.selection_errors.some((item) => item.status == 'FAILED')
      );
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
      const response = await fetch(`${import.meta.env.VITE_API_URL}/sites/`);
      var data = await response.json();
      this.wikiProjects = data.sites;
    },
    getBuilder: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${
          this.$route.params.builder_id
        }`,
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
        this.$emit('onBuilderLoaded', this.builder);
      }
    },
    onSubmit: async function () {
      this.$emit('onBeforeSubmit');
      const form = this.$refs.form;
      if (!form.checkValidity()) {
        this.$refs.form_group.classList.add('was-validated');
        return;
      }

      let postUrl = '';
      if (this.isEditing) {
        postUrl = `${import.meta.env.VITE_API_URL}/builders/${
          this.$route.params.builder_id
        }`;
      } else {
        postUrl = `${import.meta.env.VITE_API_URL}/builders/`;
      }

      this.processing = true;
      const response = await fetch(postUrl, {
        headers: { 'Content-Type': 'application/json' },
        method: 'post',
        credentials: 'include',
        body: JSON.stringify({
          ...this.builder,
          model: this.model,
          params: this.params,
        }),
      });

      this.processing = false;

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
      this.errors = data.items.errors.join(', ');
      this.$emit('onValidationError', data);
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

      const postUrl = `${import.meta.env.VITE_API_URL}/builders/${
        this.$route.params.builder_id
      }/delete`;
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
  color: #dc3545;
}

.materialize-error {
  background-color: pink;
}
.loader {
  margin-left: 1rem;
}
</style>
