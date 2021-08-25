<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div class="row">
      <div>
        <div v-for="item in list" :key="item.id" class="card text-center m-5">
          <div class="card-header">
            {{ item.name }}
          </div>
          <div class="card-body ">
            <h5 class="card-title">{{ item.project }}</h5>
            <table v-if="item.selections.length" class="card-table table">
              <thead>
                <tr>
                  <th scope="col">Name</th>
                  <th scope="col">Created At</th>
                  <th scope="col">Updated At</th>
                  <th scope="col">Generated At</th>
                  <th scope="col">Update</th>
                  <th scope="col">Download</th>
                </tr>
              </thead>
              <tbody v-for="selection in item.selections" :key="selection.s_id">
                <tr>
                  <td>selection_name</td>
                  <td>created at</td>
                  <td>updated at</td>
                  <td>generated at</td>
                  <td>
                    <button class="btn btn-primary ml-3">
                      Update
                    </button>
                  </td>
                  <td>
                    <a :href="item.url" class="btn btn-primary ml-3" download
                      >Download {{ selection.content_type }}</a
                    >
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
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
