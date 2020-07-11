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
              href="#collapseOne1"
              aria-expanded="true"
              aria-controls="collapseOne1"
            >
              Custom pagination <i class="fas fa-angle-down rotate-icon"></i>
            </a>
          </div>

          <!-- Card body -->
          <div
            id="collapseOne1"
            class="collapse"
            role="tabpanel"
            aria-labelledby="headingOne1"
            data-parent="#accordionEx"
          >
            <div class="card-body form-inline p-2">
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
      return isNaN(this.page) || this.page < 0;
    }
  },
  methods: {
    isValid: function() {
      return !this.errorRows && !this.errorPage;
    },
    onButtonClick: function() {
      if (!this.isValid()) {
        return;
      }
      this.$emit('page-select', {
        numRows: this.rows,
        startPage: this.page
      });
    }
  }
};
</script>

<style scoped>
.card-header {
  background-color: transparent;
}

.card {
  border: none;
}

.card-body {
  border-bottom: 1px solid rgba(0, 0, 0, 0.125);
  border-top: 1px solid rgba(0, 0, 0, 0.125);
}

.card-header {
  border: none;
}

.num-select {
  width: 6rem;
  text-align: center;
}
</style>
