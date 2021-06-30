<template>
  <div>
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
        <form class="needs-validation" novalidate>
          <div class="m-4">
            <label>Project</label>
            <select ref="select" class="custom-select my-list">
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
              ref="article_name"
              v-model="valid_article_names"
              required
            ></textarea>
            <div class="invalid-feedback">
              Please provide valid items.
            </div>
          </div>
          <div
            v-if="this.success == false"
            id="invalid_articles"
            class="form-group m-4"
          >
            Following items are not valid for selection lists beacuse they have
            {{ forbidden_chars }}
            <textarea
              class="form-control my-list is-invalid"
              rows="6"
              v-model="invalid_article_names"
            ></textarea>
          </div>
          <button
            v-on:click="validateForm"
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
</template>

<script>
import SecondaryNav from './SecondaryNav.vue';
export default {
  components: { SecondaryNav },
  name: 'MyLists',
  data: function() {
    return {
      wikiProjects: [],
      success: true,
      valid_article_names: '',
      invalid_article_names: '',
      forbidden_chars: ''
    };
  },
  created: function() {
    this.getWikiProjects();
  },
  methods: {
    getWikiProjects: async function() {
      const response = await fetch(`${process.env.VUE_APP_API_URL}/sites/`);
      var data = await response.json();
      this.wikiProjects = data.sites;
      var index = this.wikiProjects.indexOf('https://en.wikipedia.org');
      this.wikiProjects.splice(index, 1);
      this.wikiProjects.forEach((element, index) => {
        this.wikiProjects[index] = element.replace('https://', '');
      });
    },
    validateForm: function() {
      let parent = this;
      const form = document.querySelectorAll('.needs-validation')[0];
      form.addEventListener(
        'submit',
        async function(event) {
          if (!form.checkValidity()) {
            event.preventDefault();
            event.stopPropagation();
            form.classList.add('was-validated');
            return;
          }
          const article_detail = {
            article_name: parent.$refs.article_name.value,
            list_name: parent.$refs.list_name.value,
            project_name: parent.$refs.select.value
          };
          const response = await fetch(
            `${process.env.VUE_APP_API_URL}/selection/`,
            {
              headers: { 'Content-Type': 'application/json' },
              method: 'post',
              body: JSON.stringify(article_detail)
            }
          );
          var data = await response.json();
          parent.success = data.success;
          if (parent.success) {
            parent.$router.push('/selection/user');
            return;
          }
          event.preventDefault();
          event.stopPropagation();
          form.classList.remove('was-validated');
          parent.valid_article_names = data.items.valid.join('\n');
          parent.invalid_article_names = data.items.invalid.join('\n');
          parent.forbidden_chars = [...new Set(data.items.forbiden_chars)].join(
            ' , '
          );
        },
        false
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
