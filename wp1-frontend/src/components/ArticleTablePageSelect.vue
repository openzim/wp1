<template>
  <div class="row">
    <div class="select-cont col-7">
      <div
        class="accordion"
        id="accordion-ps"
        role="tablist"
        aria-multiselectable="true"
      >
        <div class="card mb-2">
          <div class="card-header p-0" role="tab" id="collapse-page-select">
            <a
              data-toggle="collapse"
              data-parent="#accordion-ps"
              href="#collapsePage"
              aria-expanded="true"
              aria-controls="collapsePage"
            >
              Custom pagination
            </a>
          </div>

          <!-- Card body -->
          <div
            id="collapsePage"
            :class="['collapse', startOpen() ? 'show' : '']"
            role="tabpanel"
            aria-labelledby="headingOne1"
            data-parent="#accordion-ps"
          >
            <div class="card-body form-inline p-2">
              <div class="card-form">
                Show
                <input
                  id="row-input"
                  :class="[
                    'num-select',
                    'form-control',
                    'm-2',
                    { 'is-invalid': errorRows }
                  ]"
                  v-model="rows"
                />
                rows starting with page
                <input
                  id="page-input"
                  :class="[
                    'num-select',
                    'form-control',
                    'm-2',
                    { 'is-invalid': errorPage }
                  ]"
                  v-model="page"
                />
              </div>

              <button v-on:click="onButtonClick()" class="btn-primary ml-4">
                Update View
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'articletablepageselect',
  props: {
    numRows: Number,
    startPage: String
  },
  data: function() {
    return {
      rows: this.numRows,
      page: this.startPage
    };
  },
  computed: {
    errorRows: function() {
      return (
        this.rows === '' || isNaN(this.rows) || this.rows > 500 || this.rows < 0
      );
    },
    errorPage: function() {
      return isNaN(this.page) || this.page < 1;
    }
  },
  methods: {
    startOpen: function() {
      return this.numRows != 100 || this.startPage > 1;
    },
    isValid: function() {
      return !this.errorRows && !this.errorPage;
    },
    onButtonClick: function() {
      if (!this.isValid()) {
        return;
      }
      this.$emit('page-select', {
        rows: this.rows,
        page: this.page
      });
    }
  },
  watch: {
    $route: function(to) {
      this.rows = to.query.numRows || 100;
      this.page = to.query.page || 1;
    }
  }
};
</script>

<style scoped>
@import '../cards.scss';

.num-select {
  width: 6rem;
  text-align: center;
}
</style>
