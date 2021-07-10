<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div class="row">
      <div class="col-lg-6 col-md-9 m-4">
        <div class="m-4">
          Use this tool to create an article selection list for the Wikipedia
          project of your choice. Your selection will be saved in public cloud
          storage and can be accessed through URLs that will be provided once it
          has been saved.
        </div>
        <form
          ref="form"
          v-on:submit.prevent="save"
          class="needs-validation"
          novalidate
        >
          <div ref="form_group" class="form-group">
            <div class="m-4">
              <label>Project</label>
              <select ref="project" class="custom-select my-list">
                <option selected>en.wikipedia.org</option>
                <option v-for="item in wikiProjects" v-bind:key="item">
                  {{ item }}
                </option>
              </select>
            </div>
            <div id="listName" class="m-4">
              <label for="listName">List Name</label>
              <input
                v-on:blur="validationOnBlur"
                type="text"
                ref="list_name"
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
                :placeholder="
                  'Eiffel_Tower\nStatue_of_Liberty\nFreedom_Monument_(Baghdad)\nGeorge-Étienne_Cartier_Monument'
                "
                class="form-control my-list"
                rows="13"
                ref="articles"
                v-model="valid_article_names"
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
            Following items are not valid for selection lists because they have
            {{ forbidden_chars }}
            <textarea
              class="form-control my-list is-invalid"
              rows="6"
              ref="invalid"
              v-model="invalid_article_names"
            ></textarea>
          </div>
          <button
            v-on:click="save"
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
  name: 'CreateSimpleLists',
  data: function() {
    return {
      wikiProjects: [],
      success: true,
      valid_article_names: '',
      invalid_article_names: '',
      forbidden_chars: ''
    };
  },
  computed: {
    isLoggedIn: function() {
      return this.$root.$data.isLoggedIn;
    }
  },
  created: function() {
    this.getWikiProjects();
  },
  methods: {
    getWikiProjects: async function() {
      const response = await fetch(`${process.env.VUE_APP_API_URL}/sites/`);
      var data = await response.json();
      this.wikiProjects = data.sites;
    },
    save: async function() {
      let parent = this;
      const form = parent.$refs.form;
      if (!form.checkValidity()) {
        parent.$refs.form_group.classList.add('was-validated');
        return;
      }
      const article_detail = {
        articles: parent.$refs.articles.value,
        list_name: parent.$refs.list_name.value,
        project: parent.$refs.project.value
      };
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/selection/simple`,
        {
          headers: { 'Content-Type': 'application/json' },
          method: 'post',
          credentials: 'include',
          body: JSON.stringify(article_detail)
        }
      );
      var data = await response.json();
      parent.success = data.success;
      if (parent.success) {
        parent.$router.push('/selection/user');
        return;
      }
      parent.$refs.form_group.classList.add('was-validated');
      parent.valid_article_names = data.items.valid.join('\n');
      parent.invalid_article_names = data.items.invalid.join('\n');
      parent.forbidden_chars = [...new Set(data.items.forbiden_chars)].join(
        ' , '
      );
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
