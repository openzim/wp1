<template>
  <div class="row">
    <div class="select-cont col-6">
      <div
        class="accordion"
        id="accordion-ps"
        role="tablist"
        aria-multiselectable="true"
      >
        <div class="card">
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
            <div class="card-body p-2">
              Show <input class="num-select" v-model="numRows" /> rows starting
              with page <input class="num-select" v-model="startPage" />
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
  methods: {
    onButtonClick: function() {
      this.$emit('page-select', {
        numRows: this.numRows,
        startPage: this.startPage
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

.num-select {
  width: 2.2rem;
}
</style>
