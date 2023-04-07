<template>
  <BaseBuilder
    :key="$route.path"
    :listName="'SPARQL Selection'"
    :model="'wp1.selection.models.sparql'"
    :params="params"
    :builderId="$route.params.builder_id"
    @onBeforeSubmit="onBeforeSubmit"
    @onValidationError="onValidationError"
    @onBuilderLoaded="onBuilderLoaded"
  >
    <template #create-desc>
      <p>
        Use this tool to create an article selection list for the Wikipedia
        project of your choice, using a SPARQL query. The query can either be
        entered directly or provided via a Wikidata query service URL. Your
        selection will be saved in public cloud storage and can be accessed
        through URLs that will be provided once it has been saved.
      </p>
      <p class="mb-0">
        For more information on creating a SPARQL selection, see the
        <a href="https://wp1.readthedocs.io/en/latest/user/selections/"
          >end user documentation</a
        >
      </p>
    </template>
    <template #extra-params="{ success }">
      <div
        class="accordion"
        id="accordion-rs"
        role="tablist"
        aria-multiselectable="true"
      >
        <div class="card card-select mt-2 mx-4">
          <div
            class="card-header card-header-select p-0"
            role="tab"
            id="collapse-rating-select"
          >
            <a
              id="toggleUpdateQuery"
              data-toggle="collapse"
              data-parent="#accordion-rs"
              href="#collapseUrlQuery"
              aria-expanded="true"
              aria-controls="collapseRating"
            >
              Optional: Update the query using a WikiData Query URL
            </a>
          </div>

          <!-- Card body -->
          <div
            id="collapseUrlQuery"
            class="collapse"
            data-parent="#accordion-rs"
          >
            <div class="card-body card-body-select px-0 py-2">
              <div class="col-lg-12 p-0">
                <p>
                  You can use a WikiData Query URL to create or update the query
                  that this SPARQL selection uses. Input the URL in the box
                  below and click "Update".
                </p>
                <p>
                  A WikiData Query URL is taken from
                  <a href="https://query.wikidata.org/">the query service</a>
                  and looks like
                  <code
                    >https://query.wikidata.org/#%23Goats%0ASELECT%20%3Fitem%20%3FitemLabel%20%0AWHERE...</code
                  >
                </p>
                <p v-if="queryUpdateError" class="error">
                  Could not extract SPARQL query from that URL. Make sure it is
                  a URL from query.wikidata.org.
                </p>
              </div>
              <div class="col-lg-9 p-0 pr-4 update-input-cont">
                <input
                  id="updateQueryInput"
                  class="form-control my-2"
                  v-model="queryUpdateValue"
                />
              </div>
              <div class="col-lg-3 px-0 py-2 update-btn-cont">
                <button
                  id="updateQuery"
                  type="button"
                  class="btn btn-primary"
                  v-on:click="updateQuery"
                >
                  Update
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div id="items" class="form-group m-4">
        <label for="items">Query</label>
        <textarea
          ref="query"
          v-on:blur="validationOnBlur"
          v-model="params.query"
          :placeholder="
            '#Rock bands that start with &quot;M&quot;\n' +
            'SELECT ?band ?bandLabel ?article\n' +
            'WHERE\n' +
            '{\n' +
            '  ?band wdt:P31 wd:Q5741069 .\n' +
            '  ?band rdfs:label ?bandLabel .\n' +
            '  { ?article schema:about ?band. ?article schema:isPartOf <https://en.wikipedia.org/>. }\n' +
            '  FILTER(LANG(?bandLabel) = &quot;en&quot;) .\n' +
            '  FILTER(STRSTARTS(?bandLabel, \'M\')) .\n}'
          "
          class="form-control my-list"
          :class="{ 'is-invalid': !success }"
          rows="13"
          required
        ></textarea>
        <div class="invalid-feedback">Please provide a valid query</div>
      </div>
    </template>
  </BaseBuilder>
</template>

<script>
import BaseBuilder from './BaseBuilder.vue';

export default {
  components: { BaseBuilder },
  name: 'SparqlBuilder',
  data: function () {
    return {
      params: {},
      queryUpdateValue: '',
      queryUpdateError: false,
    };
  },
  methods: {
    validationOnBlur: function (event) {
      if (event.target.value) {
        event.target.classList.remove('is-invalid');
      } else {
        event.target.classList.add('is-invalid');
      }
    },
    onBuilderLoaded: function (builder) {
      this.params = builder.params;
    },
    onBeforeSubmit: function () {
      this.$refs.query.setCustomValidity('');
    },
    onValidationError: function () {
      this.$refs.query.setCustomValidity('List not valid');
    },
    updateQuery: function () {
      this.queryUpdateError = false;
      const url = this.queryUpdateValue;
      if (url.indexOf('wikidata.org') == -1) {
        this.queryUpdateError = true;
        return;
      }
      const parts = url.split('#');
      if (parts.length < 2) {
        this.queryUpdateError = true;
        return;
      }
      this.$refs.query.value = unescape(parts[1]);
      this.$refs.query.dispatchEvent(new Event('input'));
    },
  },
};
</script>

<style scoped>
@import '../cards.scss';

.update-input-cont {
  flex: 0 0 82%;
  max-width: 82%;
}
.update-btn-cont {
  flex: 0 0 18%;
  max-width: 18%;
}

.error {
  color: #dc3545;
}
</style>
