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
            <div class="input-group input mx-auto mb-3">
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

            <a :href="item.link" class="btn btn-primary m-2" download
              >Download .TSV</a
            >
            <a :href="item.link" class="btn btn-secondary" download
              >Download .XLS</a
            >
          </div>
          <div class="card-footer text-muted">
            {{ item.timstamp }}
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

export default {
  components: { SecondaryNav },
  name: 'MyLists',
  data: function() {
    return {
      list: [
        {
          name: 'My-List1',
          link: '<URL1>',
          timstamp: '2 days ago '
        },
        {
          name: 'My-List2',
          link: '<URL2>',
          timstamp: '2 days ago'
        },
        {
          name: 'My-List3',
          link: '<URL3>',
          timstamp: '2 days ago'
        },
        {
          name: 'My-List4',
          link: '<URL4>',
          timstamp: '2 days ago'
        }
      ]
    };
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
