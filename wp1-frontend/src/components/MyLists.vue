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
              <th>ZIM updated</th>
              <th>Download ZIM</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in list" :key="item.s_id">
              <td>{{ item.name }}</td>
              <td :data-order="item.created_at">
                {{ localDate(item.created_at) }}
              </td>
              <td :data-order="item.updated_at">
                {{ localDate(item.updated_at) }}
              </td>
              <td>{{ item.project }}</td>
              <td v-if="item.s_updated_at" :data-order="item.s_updated_at">
                {{ localDate(item.s_updated_at) }}
              </td>
              <td v-else data-order="0">-</td>
              <td v-if="!isPending(item) && !hasSelectionError(item)">
                <a :href="item.s_url">Download {{ item.s_extension }}</a>
              </td>
              <td v-else-if="isPending(item)">
                <pulse-loader
                  class="loader"
                  :color="loaderColor"
                  :size="loaderSize"
                ></pulse-loader>
              </td>
              <td v-else-if="hasSelectionError(item)">
                <div v-if="item.s_status === 'FAILED'">
                  <span class="failed">PERMANENTLY FAILED</span>
                  <span
                    data-toggle="tooltip"
                    data-placement="top"
                    title="Creating the selection failed and cannot be retried"
                    ><i class="bi bi-info-circle"></i
                  ></span>
                </div>
                <div v-else-if="item.s_status === 'CAN_RETRY'">
                  <span class="failed">FAILED, RETRYABLE</span>
                  <span
                    data-toggle="tooltip"
                    data-placement="top"
                    title="Creating the selection failed, but can be retried on the edit page"
                    ><i class="bi bi-info-circle"></i
                  ></span>
                </div>
              </td>
              <td
                v-if="item.z_url"
                :class="{
                  'outdated-zim': hasOutdatedZim(item),
                  'deleted-zim': hasDeletedZim(item),
                }"
              >
                {{ localDate(item.z_updated_at) }}
              </td>
              <td v-else>-</td>
              <td
                v-if="item.z_url && !hasDeletedZim(item)"
                :class="{ 'outdated-zim': hasOutdatedZim(item) }"
              >
                <a :href="item.z_url">Download ZIM</a>
                <span
                  v-if="hasOutdatedZim(item)"
                  data-toggle="tooltip"
                  data-placement="top"
                  title="The ZIM file is out of date. A new one has automatically been requested."
                  ><i class="bi bi-info-circle"></i
                ></span>
              </td>
              <td v-else-if="zimFailed(item)">
                <span class="zim-failed"
                  ><router-link :to="zimPathFor(item)"
                    >Failed</router-link
                  ></span
                >
              </td>
              <td v-else-if="hasPendingZim(item)">
                <pulse-loader
                  class="loader"
                  :color="loaderColor"
                  :size="loaderSize"
                ></pulse-loader>
              </td>
              <td v-else-if="!isPending(item) && !hasSelectionError(item)">
                <router-link :to="zimPathFor(item)"
                  ><button type="button" class="btn btn-primary">
                    Create ZIM
                  </button></router-link
                >
                <span
                  v-if="hasDeletedZim(item)"
                  class="deleted-zim"
                  data-toggle="tooltip"
                  data-placement="top"
                  title="Your previous ZIM file has expired (2 weeks)."
                  ><i class="bi bi-info-circle"></i
                ></span>
              </td>
              <td v-else>-</td>
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
      return (
        (!item.s_url && !item.s_status) || item.updated_at > item.s_updated_at
      );
    },
    hasPendingZim: function (item) {
      return item.s_status === 'OK' && item.z_status === 'REQUESTED';
    },
    zimFailed: function (item) {
      return item.z_status === 'FAILED';
    },
    hasSelectionError: function (item) {
      return item.s_status !== null && item.s_status !== 'OK';
    },
    hasOutdatedZim: function (item) {
      return !!item.z_updated_at && item.z_updated_at < item.s_updated_at;
    },
    hasDeletedZim: function (item) {
      // ZIMs older than 2 weeks get deleted.
      return !!item.z_is_deleted;
    },
    localDate: function (secs) {
      const fmt = new Intl.DateTimeFormat('en-US', {
        dateStyle: 'short',
        timeStyle: 'short',
      });
      return fmt.format(new Date(secs * 1000));
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
        },
      );
      var data = await response.json();
      this.list = data.builders;
      if (createDataTable) {
        this.$nextTick(function () {
          $('#list-table').DataTable({
            columnDefs: [{ orderable: false, targets: [5, 7, 8] }],
            order: [[2, 'desc']],
            iDisplayLength: 25,
          });
        });
      } else {
        $('#list-table').DataTable().columns.adjust().draw();
      }

      let hasPendingSelections = false;
      let hasPendingZim = false;
      this.list.forEach((item) => {
        if (this.isPending(item)) {
          hasPendingSelections = true;
        }
        if (this.hasPendingZim(item)) {
          hasPendingZim = true;
        }
        if (this.hasOutdatedZim(item)) {
          // Outdated ZIMs are treated like pending, poll every 5 minutes.
          hasPendingZim = true;
        }
      });
      const pollTimeoutMs = hasPendingSelections
        ? 20000
        : hasPendingZim
        ? 300000
        : 0;

      if (pollTimeoutMs) {
        this.startProgressPolling(pollTimeoutMs);
      } else {
        this.stopProgressPolling();
      }
    },
    editPathFor: (item) => {
      const fragments = item.model.split('.');
      const modelFragment = fragments[fragments.length - 1];
      return { path: `/selections/${modelFragment}/${item.id}` };
    },
    zimPathFor: (item) => {
      return { path: `/selections/${item.id}/zim` };
    },
    startProgressPolling: function (pollTimeoutMs) {
      if (this.pollId) {
        return;
      }
      this.pollId = setInterval(() => this.getLists(), pollTimeoutMs);
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

.zim-failed a {
  color: #dc3545 !important;
}

.outdated-zim,
.outdated-zim a {
  color: #cc7204;
}

.deleted-zim {
  color: #dc3545;
}

.failed {
  display: inline-block;
  color: #dc3545;
  margin-right: 0.75em;
}

.bi {
  cursor: pointer;
}
</style>
