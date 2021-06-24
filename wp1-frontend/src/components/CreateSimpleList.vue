<template>
  <div>
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div class="row">
      <form>
        <div class="col-lg-6 col-md-9 m-4">
          <div>
            <div class="m-4" style="font-weight: 550;">
              Use this tool to create an article selection list for the
              Wikipedia project of your choice. Your selection will be saved in
              public cloud storage and can be accessed through URLs that will be
              provided once it has been saved.
            </div>
            <div class="m-4">
              <label for="Project">Project</label>
              <select class="custom-select my-list">
                <option selected>en.wikipedia.org</option>
                <option v-for="item in wikiProjects" v-bind:key="item">
                  {{ item.replace('https://', '') }}
                </option>
              </select>
            </div>
            <div class="m-4">
              <label for="listName">List Name</label>
              <input
                id="listName"
                placeholder="My List"
                class="form-control my-list"
                required="true"
              />
            </div>
            <div class="form-group m-4">
              <label for="Items">Items</label>
              <textarea
                placeholder="Article names with either 'Spaces between words' or 'Underscores_between_words'"
                class="form-control my-list"
                rows="13"
                required="true"
              ></textarea>
            </div>
            <button id="saveListButton" type="submit" class="btn-primary ml-4">
              Save List
            </button>
          </div>
        </div>
      </form>
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
      wikiProjects: ['en.wikipedia.org']
    };
  },
  created: function() {
    this.getWikiProjects();
  },
  methods: {
    getWikiProjects: async function() {
      const response = await fetch(`${process.env.VUE_APP_API_URL}/sites/`);
      const data = await response.json();
      this.wikiProjects = data.sites;
    }
  }
};
</script>

<style scoped>
.my-list {
  border: 1px solid #000;
}
</style>
