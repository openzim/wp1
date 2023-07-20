<template>
  <BaseBuilder
    :key="$route.path"
    :listName="'Book Selection'"
    :model="'wp1.selection.models.book'"
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
        project of your choice, based off a Wikipedia Book that you already
        created. You must first "save" your book, then enter the URL of the
        saved book. Your selection will be saved in public cloud storage and can
        be accessed through URLs that will be provided once it has been saved.
      </p>
      <p class="mb-0">
        For more information on creating a Book selection, see the
        <a href="https://wp1.readthedocs.io/en/latest/user/selections/"
          >end user documentation</a
        >
      </p>
    </template>
    <template #extra-params>
      <div id="items" class="form-group m-4">
        <label for="items">URL</label>
        <input
          id="bookUrl"
          ref="bookUrl"
          class="form-control my-2"
          v-model="params.url"
        />
        <div class="invalid-feedback">Please provide a valid URL</div>
      </div>
    </template>
  </BaseBuilder>
</template>

<script>
import BaseBuilder from './BaseBuilder.vue';

export default {
  components: { BaseBuilder },
  name: 'BookBuilder',
  data: function () {
    return {
      url: '',
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
      this.params = builder.params;
    },
    onBeforeSubmit: function () {
      this.$refs.bookUrl.setCustomValidity('');
    },
    onValidationError: function () {
      this.$refs.bookUrl.setCustomValidity('URL not valid');
    },
  },
};
</script>

<style scoped></style>
