<template>
  <div class="row">
    <div v-if="layout != 'alternate'" class="select-cont col-xl-7">
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
          <div
            id="collapseRating"
            :class="['collapse', startOpen() ? 'show' : '']"
            data-parent="#accordion-rs"
          >
            <div class="card-body form-inline p-2">
              <div class="card-form">
                Quality
                <select class="custom-select" ref="qualitySelect">
                  <option
                    v-for="(item, key) in categoryLinks.quality"
                    :value="key"
                    v-bind:key="key"
                    :selected="selectedQuality == key"
                    >{{ item.text ? item.text : item }}</option
                  >
                </select>
                Importance
                <select class="custom-select" ref="importanceSelect">
                  <option
                    v-for="(item, key) in categoryLinks.importance"
                    :value="key"
                    v-bind:key="key"
                    :selected="selectedImportance == key"
                    >{{ item.text ? item.text : item }}</option
                  >
                </select>
              </div>
              <button v-on:click="onButtonClick()" class="btn-primary ml-4">
                Update View
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="col">
      <div class="form-inline">
        Quality
        <select
          :disabled="!projectId"
          @change="onSelectChange()"
          class="custom-select"
          ref="qualitySelect"
        >
          <option
            v-for="(item, key) in categoryLinks.quality"
            :value="key"
            v-bind:key="key"
            :selected="selectedQuality == key"
            >{{ item.text ? item.text : item }}</option
          >
        </select>
        Importance
        <select
          :disabled="!projectId"
          @change="onSelectChange()"
          class="custom-select"
          ref="importanceSelect"
        >
          <option
            v-for="(item, key) in categoryLinks.importance"
            :value="key"
            v-bind:key="key"
            :selected="selectedImportance == key"
            >{{ item.text ? item.text : item }}</option
          >
        </select>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'articletableratingselect',
  props: ['initialQuality', 'initialImportance', 'projectId', 'layout'],
  data: function() {
    return {
      categoryLinks: {}
    };
  },
  created: function() {
    this.getCategoryLinks();
  },
  computed: {
    selectedQuality: function() {
      return this.initialQuality || '';
    },
    selectedImportance: function() {
      return this.initialImportance || '';
    }
  },
  watch: {
    projectId: async function() {
      await this.getCategoryLinks();
      this.onSelectChange();
    },
    $route: function(to) {
      if (to.path == '/compare') {
        this.categoryLinks = {};
      }
    }
  },
  methods: {
    startOpen: function() {
      return !!this.$route.query.quality || !!this.$route.query.importance;
    },
    getCategoryLinks: async function() {
      if (!this.projectId) {
        return;
      }
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${this.projectId}/category_links/sorted`
      );
      const links = await response.json();
      links.quality[''] = 'None Selected';
      links.importance[''] = 'None Selected';
      this.categoryLinks = links;
    },

    // Only used for alternate view on Compare pages.
    onSelectChange: function() {
      const quality = this.$refs.qualitySelect.value;
      const importance = this.$refs.importanceSelect.value;

      this.$emit('rating-select', { quality, importance });
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

.custom-select {
  margin: 0 0.5rem;
  max-width: 8.45rem;
}
</style>
