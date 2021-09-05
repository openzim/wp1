<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div class="row">
      <div class="col-lg-6 col-md-9 m-4">
        <div class="ml-4 mb-4">
          Use this tool to create an article selection list for the Wikipedia
          project of your choice. Your selection will be saved in public cloud
          storage and can be accessed through URLs that will be provided once it
          has been saved.
        </div>
        <form
          ref="form"
          v-on:submit.prevent="onSubmit"
          class="needs-validation"
          novalidate
        >
          <div ref="form_group" class="form-group">
            <div class="m-4">
              <label>Project</label>
              <select v-model="builder.project" class="custom-select my-list">
                <option v-if="wikiProjects.length == 0" selected
                  >en.wikipedia.org</option
                >
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
                Please provide a valid List Name.
              </div>
            </div>
            <div id="items" class="form-group m-4">
              <label for="Items">Items</label>
              <textarea
                v-on:blur="validationOnBlur"
                v-model="builder.articles"
                :placeholder="
                  'Eiffel_Tower\nStatue_of_Liberty\nFreedom_Monument_(Baghdad)\nGeorge-Étienne_Cartier_Monument'
                "
                class="form-control my-list"
                rows="13"
                required
              ></textarea>
              <div class="invalid-feedback">
                Please provide valid items.
              </div>
            </div>
          </div>
          <div
            v-if="this.success == false"
            id="invalid_articles"
            class="form-group m-4"
          >
            {{ errors }}
            <textarea
              class="form-control my-list is-invalid"
              rows="6"
              ref="invalid"
              v-model="invalid_article_names"
            ></textarea>
          </div>
          <button
            v-if="isEditing"
            id="updateListButton"
            type="submit"
            class="btn-primary ml-4"
          >
            Update List
          </button>
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
  name: 'SimpleList',
  data: function() {
    return {
      isEditing: false,
      wikiProjects: [],
      success: true,
      valid_article_names: '',
      invalid_article_names: '',
      errors: '',
      builder: {
        articles: '',
        name: '',
        project: 'en.wikipedia.org'
      }
    };
  },
  computed: {
    isLoggedIn: function() {
      return this.$root.$data.isLoggedIn;
    }
  },
  created: function() {
    this.getWikiProjects();
    this.isEditing = !!this.$route.params.builder_id;
    if (this.isEditing) {
      this.getBuilder();
    }
  },
  methods: {
    getWikiProjects: async function() {
      const response = await fetch(`${process.env.VUE_APP_API_URL}/sites/`);
      var data = await response.json();
      this.wikiProjects = data.sites;
    },
    getBuilder: async function() {
      window.console.log(this.$route.params.builder_id);
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/builders/${this.$route.params.builder_id}`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include'
        }
      );
      this.builder = await response.json();
    },
    onSubmit: async function() {
      const form = this.$refs.form;
      if (!form.checkValidity()) {
        this.$refs.form_group.classList.add('was-validated');
        return;
      }

      let postUrl = '';
      if (this.isEditing) {
        postUrl = `${process.env.VUE_APP_API_URL}/builders/${this.$route.params.builder_id}`;
      } else {
        postUrl = `${process.env.VUE_APP_API_URL}/selections/simple`;
      }

      const response = await fetch(postUrl, {
        headers: { 'Content-Type': 'application/json' },
        method: 'post',
        credentials: 'include',
        body: JSON.stringify(this.builder)
      });
      var data = await response.json();
      this.success = data.success;
      if (this.success) {
        this.$router.push('/selections/user');
        return;
      }
      this.$refs.form_group.classList.add('was-validated');
      this.builder.articles = data.items.valid.join('\n');
      this.invalid_article_names = data.items.invalid.join('\n');
      this.errors = data.items.errors.join(', ');
    },
    validationOnBlur: function(event) {
      if (event.target.value) {
        event.target.classList.remove('is-invalid');
      } else {
        event.target.classList.add('is-invalid');
      }
    }
  }
};
</script>

<style scoped></style>
