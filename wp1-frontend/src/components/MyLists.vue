<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div class="row ml-4">
      <div>
        <table class="table table-hover">
          <thead>
            <tr>
              <th scope="col">Name</th>
              <th scope="col">Created At</th>
              <th scope="col">Updated At</th>
              <th scope="col">Generated At</th>
              <th scope="col">Download</th>
            </tr>
          </thead>
          <tbody v-for="item in list" :key="item.id">
            <tr>
              <td :rowspan="item.selections.length || 1">{{ item.name }}</td>
              <td :rowspan="item.selections.length || 1">
                {{ item.created_at }}
              </td>
              <td :rowspan="item.selections.length || 1">
                {{ item.updated_at }}
              </td>
              <td v-if="item.selections.length">
                {{ item.selections[0].s_updated_at }}
              </td>
              <td v-if="item.selections.length">
                <a
                  :href="item.selections[0].url"
                  class="btn btn-primary mb-2 mr-2"
                  download
                  >Download {{ item.selections[0].extension }}</a
                >
              </td>
            </tr>
            <tr
              v-for="selection in item.selections.slice(1)"
              :key="selection.id"
            >
              <td v-if="item.selections.length">
                {{ selection.s_updated_at }}
              </td>
              <td v-if="item.selections.length">
                <a
                  :href="selection.url"
                  class="btn btn-primary mb-2 mr-2"
                  download
                  >Download {{ selection.extension }}</a
                >
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <div v-else>
    <LoginRequired></LoginRequired>
  </div>
</template>

<script>
import SecondaryNav from './SecondaryNav.vue';
import LoginRequired from './LoginRequired.vue';

export default {
  components: { SecondaryNav, LoginRequired },
  name: 'MyLists',
  data: function() {
    return {
      list: []
    };
  },
  computed: {
    isLoggedIn: function() {
      return this.$root.$data.isLoggedIn;
    }
  },
  methods: {
    copyText: function(id) {
      var copyText = document.getElementById(id);
      copyText.select();
      document.execCommand('copy');
      copyText.blur();
    },
    getLists: async function() {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/selection/simple/lists`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include'
        }
      );
      var data = await response.json();
      this.list = data.builders;
    }
  },
  created: function() {
    this.getLists();
  }
};
</script>

<style scoped>
@import '../cards.scss';
</style>
