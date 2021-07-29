<template>
  <div class="row">
    <div class="select-cont col-8">
      <div
        class="accordion"
        id="accordion-nf"
        role="tablist"
        aria-multiselectable="true"
      >
        <div class="card card-select mb-2">
          <div
            class="card-header card-header-select p-0"
            role="tab"
            id="collapse-rating-select"
          >
            <a
              data-toggle="collapse"
              data-parent="#accordion-nf"
              href="#collapseNameFilter"
              aria-expanded="true"
              aria-controls="collapseRating"
            >
              Filter by article name
            </a>
          </div>

          <!-- Card body -->
          <div
            id="collapseNameFilter"
            :class="['collapse', startOpen() ? 'show' : '']"
            data-parent="#accordion-nf"
          >
            <div class="card-body card-body-select form-inline p-2">
              <div>
                Article name must contain:
                <input
                  ref="filterInput"
                  class="form-control m-2 mr-4"
                  :value="filterValue"
                />
              </div>
              <button
                v-on:click="onButtonClick()"
                id="updateName"
                class="btn btn-primary"
              >
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
  name: 'articletablenamefilter',
  props: {
    filterValue: String
  },
  methods: {
    startOpen: function() {
      return !!this.filterValue;
    },
    onButtonClick: function() {
      const filter = this.$refs.filterInput.value;
      if (filter == this.$route.query.articlePattern) {
        return;
      }

      this.$emit('name-filter', this.$refs.filterInput.value);
    }
  }
};
</script>

<style scoped>
@import '../cards.scss';
</style>
