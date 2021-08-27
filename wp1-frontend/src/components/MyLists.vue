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
            <tr v-if="item.selections.length < 1">
              <td>{{ item.name }}</td>
              <td>{{ item.created_at }}</td>
              <td>{{ item.updated_at }}</td>
            </tr>
            <tr v-else v-for="selection in item.selections" :key="selection.id">
              <td>{{ item.name }}</td>
              <td>{{ item.created_at }}</td>
              <td>{{ item.updated_at }}</td>
              <td>{{ selection.s_updated_at }}</td>
              <td>
                <a class="btn btn-primary mb-2 mr-2" download
                  >Download {{ selection.content_type }}</a
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
      console.log(this.list);
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
