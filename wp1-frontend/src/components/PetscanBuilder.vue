<template>
  <BaseBuilder
    :key="$route.path"
    :listName="'Petscan Selection'"
    :model="'wp1.selection.models.petscan'"
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
        project of your choice, based off a
        <a href="https://petscan.wmflabs.org/">Petscan</a> URL. Your selection
        will be saved in public cloud storage and can be accessed through URLs
        that will be provided once it has been saved.
      </p>
      <p class="mb-0">
        For more information on creating a
        <a href="https://petscan.wmflabs.org/">Petscan</a> selection, see the
        <a href="https://wp1.readthedocs.io/en/latest/user/selections/"
          >end user documentation</a
        >
        or the
        <a href="https://meta.wikimedia.org/wiki/PetScan/en"
          >Petscan User Manual</a
        >.
      </p>
    </template>
    <template #extra-params>
      <div id="items" class="form-group m-4">
        <label for="items">URL</label>
        <input
          id="petscanUrl"
          ref="petscanUrl"
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
  name: 'PetscanBuilder',
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
      this.$refs.petscanUrl.setCustomValidity('');
    },
    onValidationError: function () {
      this.$refs.petscanUrl.setCustomValidity('URL not valid');
    },
  },
};
</script>

<style scoped></style>
