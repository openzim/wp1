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
              <td v-if="!isPending(item) && !hasSelectionError(item)">
                <a :href="item.s_url">Download {{ item.s_extension }}</a>
              </td>
              <td v-else-if="!hasSelectionError(item)">
                <pulse-loader
                  class="loader"
                  :color="loaderColor"
                  :size="loaderSize"
                ></pulse-loader>
              </td>
              <td v-else>
                <div v-if="item.s_status === 'FAILED'">
                  <span class="failed">PERMANENTLY FAILED</span>
                  <span
                    data-toggle="tooltip"
                    data-placement="top"
                    title="Materializing failed and cannot be retried"
                    ><i class="bi bi-info-circle"></i
                  ></span>
                </div>
                <div v-else-if="item.s_status === 'CAN_RETRY'">
                  <span class="failed">FAILED, RETRYABLE</span>
                  <span
                    data-toggle="tooltip"
                    data-placement="top"
                    title="Materializing failed, but can be retried on the edit page"
                    >[i]</span
                  >
                </div>
              </td>
              <td>
                <router-link :to="editPathFor(item)"
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
    isPending: function (item) {
      return !item.s_url || item.updated_at > item.s_updated_at;
    },
    hasSelectionError: function (item) {
      return item.s_status !== null;
    },
    getLists: async function () {
      let createDataTable = false;
      if (this.list.length === 0) {
        createDataTable = true;
      }

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/selection/simple/lists`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }
      );
      var data = await response.json();
      this.list = data.builders;
      if (createDataTable) {
        this.$nextTick(function () {
          $('#list-table').DataTable({
            order: [[2, 'desc']],
          });
        });
      }

      let hasPending = false;
      this.list.forEach((item) => {
        if (this.isPending(item)) {
          hasPending = true;
        }
      });
      if (hasPending) {
        this.startProgressPolling();
      } else {
        this.stopProgressPolling();
      }
    },
    editPathFor: (item) => {
      const fragments = item.model.split('.');
      const modelFragment = fragments[fragments.length - 1];
      return { path: `/selections/${modelFragment}/${item.id}` };
    },
    startProgressPolling: function () {
      if (this.pollId) {
        return;
      }
      this.pollId = setInterval(() => this.getLists(), 3000);
    },
    stopProgressPolling: function () {
      clearInterval(this.pollId);
    },
  },
  created: function () {
    this.getLists();
    $(function () {
      $('[data-toggle="tooltip"]').tooltip();
    });
  },
};
</script>

<style scoped>
@import '../cards.scss';

.failed {
  display: inline-block;
  color: #dc3545;
  margin-right: 0.75em;
}

.bi {
  cursor: pointer;
}
</style>
