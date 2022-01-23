<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div class="row p-4">
      <div class="col-lg-10">
        <h2>Selections</h2>
        <p>(all times UTC)</p>
        <table id="list-table">
          <thead>
            <tr>
              <th>Selection Name</th>
              <th>Selection Created</th>
              <th>Selection Updated</th>
              <th>Project</th>
              <th>Download Updated</th>
              <th>Download</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in list" :key="item.s_id">
              <td>{{ item.name }}</td>
              <td>
                {{
                  new Date(item.created_at * 1000).toLocaleDateString() +
                    ' ' +
                    new Date(item.created_at * 1000).toLocaleTimeString()
                }}
              </td>
              <td>
                {{
                  new Date(item.updated_at * 1000).toLocaleDateString() +
                    ' ' +
                    new Date(item.updated_at * 1000).toLocaleTimeString()
                }}
              </td>
              <td>{{ item.project }}</td>
              <td v-if="item.s_updated_at">
                {{
                  new Date(item.s_updated_at * 1000).toLocaleDateString() +
                    ' ' +
                    new Date(item.s_updated_at * 1000).toLocaleTimeString()
                }}
              </td>
              <td v-else>
                -
              </td>
              <td v-if="item.s_url">
                <a :href="item.s_url">Download {{ item.s_extension }}</a>
              </td>
              <td v-else>
                -
              </td>
              <td>
                <router-link :to="{ path: `/selections/simple/${item.id}` }"
                  ><button type="button" class="btn btn-primary">
                    Edit
                  </button></router-link
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
import $ from 'jquery';
$.noConflict();
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
      this.$nextTick(function() {
        $('#list-table').DataTable();
      });
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
