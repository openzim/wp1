<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div class="row">
      <div class=" col-lg-6">
        <div v-for="item in list" :key="item.name" class="card text-center m-5">
          <div class="card-header">
            {{ item.name }}
          </div>
          <div class="card-body ">
            <h5 class="card-title">{{ item.project }}</h5>
            <div class="input-group col-sm-5 mx-auto mb-3">
              <input :id="item.name" :value="item.link" class="form-control" />
              <div class="input-group-append">
                <button
                  class="btn btn-outline-secondary"
                  v-on:click="copyText(item.name)"
                >
                  Copy
                </button>
              </div>
            </div>
            <div class="col-sm-8 mx-auto">
              <a :href="item.link" class="btn btn-primary m-2" download
                >Download .TSV</a
              >
              <a :href="item.link" class="btn btn-secondary" download
                >Download .XLS</a
              >
            </div>
          </div>
          <div class="card-footer text-muted">
            {{ item.timestamp }}
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
      list: [
        {
          name: 'My-List1',
          project: 'Project1',
          link: '<URL1>',
          timestamp: '2 days ago '
        },
        {
          name: 'My-List2',
          project: 'Project2',
          link: '<URL2>',
          timestamp: '2 days ago'
        },
        {
          name: 'My-List3',
          project: 'Project3',
          link: '<URL3>',
          timestamp: '2 days ago'
        },
        {
          name: 'My-List4',
          project: 'Project4',
          link: '<URL4>',
          timestamp: '2 days ago'
        }
      ]
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
    }
  }
};
</script>

<style scoped>
@import '../cards.scss';
</style>
