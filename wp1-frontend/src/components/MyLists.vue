<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div class="row">
      <div class=" col-lg-6">
        <div v-for="item in list" :key="item.id" class="card text-center m-5">
          <div class="card-header">
            {{ item.name }}
          </div>
          <div class="card-body ">
            <h5 class="card-title">{{ item.project }}</h5>
            <div
              v-for="selection in item.selections"
              :key="selection.s_id"
              class="input-group col-sm-9 mx-auto mb-3"
            >
              <input
                :id="selection.s_id"
                :value="selection.selection_url"
                class="form-control"
              />
              <div class="input-group-append">
                <button
                  class="btn btn-outline-secondary"
                  v-on:click="copyText(selection.s_id)"
                >
                  Copy
                </button>
              </div>
              <a :href="item.url" class="btn btn-primary ml-3" download
                >Download {{ selection.extension }}</a
              >
            </div>
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
