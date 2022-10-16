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
    <div v-else class="row">
      <div class="col-lg-6 col-md-9 m-4">
        <h2 v-if="!isEditing" class="ml-4">New {{ listName }}</h2>
        <h2 v-else class="ml-4">Editing {{ listName }}</h2>
        <div v-if="!isEditing" class="ml-4 mb-4">
          <slot name="create-desc"></slot>
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
  name: 'BaseBuilder',
  props: {
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
      success: true,
      deleteSuccess: true,
      errors: '',
      builder: {
        name: '',
        project: 'en.wikipedia.org',
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
    computedInvalidItems: function () {
      return this.invalidItems;
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
        },
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
        postUrl = `${process.env.VUE_APP_API_URL}/builders/${this.$route.params.builder_id}`;
      } else {
        postUrl = `${process.env.VUE_APP_API_URL}/builders/`;
      }

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
          'Really delete this list? The definition and all downloadable selections will be permanently deleted.',
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
  color: #dc3545;
}
</style>