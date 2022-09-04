<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div class="row p-4">
      <div class="col-lg-10">
        <h2>Selections</h2>
        <p>(all times local)</p>
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
              <td v-else>-</td>
              <td v-if="item.s_url">
                <a :href="item.s_url">Download {{ item.s_extension }}</a>
              </td>
              <td v-else>
                <pulse-loader
                  class="loader"
                  :color="loaderColor"
                  :size="loaderSize"
                ></pulse-loader>
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

import PulseLoader from 'vue-spinner/src/PulseLoader.vue';

import SecondaryNav from './SecondaryNav.vue';
import LoginRequired from './LoginRequired.vue';

export default {
  components: { SecondaryNav, LoginRequired, PulseLoader },
  name: 'MyLists',
  data: function () {
    return {
      list: [],
      loaderColor: '#007bff',
      loaderSize: '.75rem',
      pollId: null,
    };
  },
  computed: {
    isLoggedIn: function () {
      return this.$root.$data.isLoggedIn;
    },
  },
  methods: {
    getLists: async function () {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/selection/simple/lists`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }
      );
      var data = await response.json();
      this.list = data.builders;
      this.$nextTick(function () {
        $('#list-table').DataTable({
          order: [[2, 'desc']],
        });
      });
    },
    pollForProgress: async function () {
      const url = `${process.env.VUE_APP_API_URL}/selection/simple/lists`;
      const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });
      const data = await response.data();
      const currentIdToIdx = {};
      this.data.forEach((item, idx) => {
        currentIdToIdx[item.b_id] = idx;
      });
      for (let i = 0; i < data.length; i++) {
        const item = data[i];
        const curIdx = currentIdToIdx[item.b_id];
        if (curIdx === undefined) {
          this.data.push(item);
        } else if (this.data[curIdx].s_url !== item.s_url) {
          this.$set(this.data, curIdx, {
            ...this.data[curIdx],
            s_url: item.s_url,
          });
        }
        currentIdToIdx[item.b_id] = null;
      }
      Object.entries(currentIdToIdx).forEach((id, idx) => {
        if (idx !== null) {
          this.data.splice(idx, 1);
        }
      });
    },
    startProgressPolling: function () {
      this.pollForProgress();
      this.pollId = setInterval(() => this.pollForProgress(), 4000);
    },
    stopProgressPolling: function () {
      clearInterval(this.pollId);
    },
  },
  created: function () {
    this.getLists();
  },
};
</script>

<style scoped>
@import '../cards.scss';
</style>
