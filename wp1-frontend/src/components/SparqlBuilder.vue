<template>
  <BaseBuilder
    :listName="'SPARQL Selection'"
    :model="'wp1.selection.models.sparql'"
    :params="params"
    @onBeforeSubmit="onBeforeSubmit"
    @onValidationError="onValidationError"
    @onBuilderLoaded="onBuilderLoaded"
  >
    <template #create-desc>
      Use this tool to create an article selection list for the Wikipedia
      project of your choice, using a SPARQL query. The query can either be
      entered directly or provided via a Wikidata query service URL. Your
      selection will be saved in public cloud storage and can be accessed
      through URLs that will be provided once it has been saved.
    </template>
    <template #extra-params="{ success }">
      <div id="items" class="form-group m-4">
        <label for="items">Query</label>
        <textarea
          ref="query"
          v-on:blur="validationOnBlur"
          v-model="params.query"
          :placeholder="
            '#Rock bands that start with &quot;M&quot;\n' +
            'SELECT ?article ?bandLabel\n' +
            'WHERE\n' +
            '{\n' +
            '  ?article wdt:P31 wd:Q5741069 .\n' +
            '  ?article rdfs:label ?bandLabel .\n' +
            '  FILTER(LANG(?bandLabel) = &quot;en&quot;) .\n' +
            '  FILTER(STRSTARTS(?bandLabel, \'M\')) .\n}' +
            success
          "
          class="form-control my-list"
          :class="{ 'is-invalid': !success }"
          rows="13"
          required
        ></textarea>
        <div class="invalid-feedback">Please provide a valid query</div>
      </div>
      <div id="queryVariable" class="m-4">
        <label for="queryVariable">Query variable</label>
        <p class="explanation">
          The variable in your query that represents the Wikidata entity whose
          article URLs should be retrieved. This will default to
          <span style="white-space: nowrap">"?article"</span>, for when your
          query already selects a variable named "?article". Note: this variable
          must appear in the SELECT clause of your query.
        </p>
        <input
          v-on:blur="validationOnBlur"
          v-model="params.queryVariable"
          type="text"
          placeholder="?article"
          class="form-control my-list"
        />
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
  },
};
</script>

<style scoped></style>
