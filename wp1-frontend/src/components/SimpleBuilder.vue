<template>
  <BaseBuilder
    :key="$route.path"
    :listName="'Simple Selection'"
    :model="'wp1.selection.models.simple'"
    :params="params"
    :builderId="$route.params.builder_id"
    :invalidItems="invalidItems"
    @onBuilderLoaded="onBuilderLoaded"
    @onBeforeSubmit="onBeforeSubmit"
    @onValidationError="onValidationError"
  >
    <template #create-desc>
      <p>
        Use this tool to create an article selection list for the Wikipedia
        project of your choice. Your selection will be saved in public cloud
        storage and can be accessed through URLs that will be provided once it
        has been saved.
      </p>
      <p class="mb-0">
        For more information on creating a Simple selection, see the
        <a href="https://wp1.readthedocs.io/en/latest/user/selections/"
          >end user documentation</a
        >
      </p>
    </template>
    <template #extra-params="{ success }">
      <div id="items" class="form-group m-4">
        <label for="items">Items</label>
        <textarea
          ref="list"
          v-on:blur="validationOnBlur"
          v-model="articles"
          :placeholder="
            'Eiffel_Tower\nStatue_of_Liberty\nFreedom_Monument_(Baghdad)\n' +
            'George-Étienne_Cartier_Monument\n\n# Whitespace and comments ' +
            'starting with # are ignored' +
            '\n'
          "
          class="form-control my-list"
          :class="{ 'is-invalid': !success }"
          rows="13"
          required
        ></textarea>
        <div class="invalid-feedback">Please provide valid items</div>
      </div>
    </template>
  </BaseBuilder>
</template>

<script>
import BaseBuilder from './BaseBuilder.vue';

export default {
  components: { BaseBuilder },
  name: 'SimpleBuilder',
  data: function () {
    return {
      articles: '',
      invalidItems: '',
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
      this.articles = builder.params.list.join('\n');
    },
    onBeforeSubmit: function () {
      this.$refs.list.setCustomValidity('');
    },
    onValidationError: function (data) {
      this.invalidItems = data.items.invalid.join('\n');
      this.$refs.list.setCustomValidity('List not valid');
    },
  },
  watch: {
    articles: function () {
      this.params = { list: this.articles.split('\n') };
    },
  },
};
</script>

<style scoped></style>
