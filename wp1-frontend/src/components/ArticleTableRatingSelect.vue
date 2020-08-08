<template>
  <div class="row">
    <div class="select-cont col-7">
      <div
        class="accordion"
        id="accordion-rs"
        role="tablist"
        aria-multiselectable="true"
      >
        <div class="card mb-2">
          <div class="card-header p-0" role="tab" id="collapse-rating-select">
            <a
              data-toggle="collapse"
              data-parent="#accordion-rs"
              href="#collapseRating"
              aria-expanded="true"
              aria-controls="collapseRating"
            >
              Select Quality/Importance
            </a>
          </div>

          <!-- Card body -->
          <div id="collapseRating" class="collapse" data-parent="#accordion-rs">
            <div class="card-body form-inline p-2">
              Quality
              <select class="custom-select" ref="qualitySelect">
                <option
                  v-for="(item, key) in categoryLinks.quality"
                  :value="key"
                  v-bind:key="key"
                  :selected="$route.query.quality == key"
                  >{{ item.text ? item.text : item }}</option
                >
              </select>
              Rating
              <select class="custom-select" ref="importanceSelect">
                <option
                  v-for="(item, key) in categoryLinks.importance"
                  :value="key"
                  v-bind:key="key"
                  :selected="$route.query.importance == key"
                  >{{ item.text ? item.text : item }}</option
                >
              </select>
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
  name: 'articletableratingselect',
  props: {
    projectId: String
  },
  data: function() {
    return {
      categoryLinks: {}
    };
  },
  created: function() {
    this.getCategoryLinks();
  },
  methods: {
    getCategoryLinks: async function() {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${this.projectId}/category_links/sorted`
      );
      this.categoryLinks = await response.json();
    },
    onButtonClick: function() {
      const quality = this.$refs.qualitySelect.value;
      const importance = this.$refs.importanceSelect.value;
      if (
        quality == this.$route.query.quality &&
        importance == this.$route.query.importance
      ) {
        return;
      }

      this.$emit('rating-select', { quality, importance });
    }
  }
};
</script>

<style scoped>
@import '../cards.scss';
</style>
