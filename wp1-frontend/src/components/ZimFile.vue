<template>
  <div v-if="isLoggedIn">
    <div>
      <SecondaryNav></SecondaryNav>
    </div>
    <div v-if="notFound">
      <div id="404" class="col-lg-6 m-4">
        <h2>404 Not Found</h2>
        Sorry, the list with that ID either doesn't exist or isn't owned by you.
      </div>
    </div>
    <div v-else-if="serverError">
      <h2>500 Server error</h2>
      Something went wrong and we couldn't retrieve the list with that ID. You
      might try again later.
    </div>
    <div v-else-if="ready">
      <div class="row">
        <div class="col-lg-6 col-md-9 mx-4">
          <h2>Create ZIM file</h2>
          <p v-if="status === 'NOT_REQUESTED'">
            Use this form to create a ZIM file from your selection, so that you
            can browse the articles it contains offline. The
            &quot;Description&quot; and &quot;Long Description&quot; fields are
            required, but generic defaults will be used if they're not provided.
          </p>
          <p>
            Once you request a ZIM file, it will be queued for creation. This
            page and the My Selections page will automatically update with a URL
            to download your ZIM file once it is ready.
          </p>
          <p v-if="isDeleted && status == 'FILE_READY'" class="errors">
            Your ZIM file has expired and needs to be re-created. ZIM file
            download links are only valid for 2 weeks. You can re-create your
            ZIM file with the button below.
          </p>
          <p v-else-if="status === 'REQUESTED'">
            Your ZIM file has been requested and is being processed. This page
            will update with the URL to download it once it is ready. It will
            also keep you updated on any errors that may occur.
          </p>
          <p v-else-if="status === 'FILE_READY'">
            Your ZIM file is ready! Click the button below to download it. You
            can also always download it from the My Selections page.
          </p>
          <p v-else-if="status === 'FAILED'" class="errors">
            There was an error creating your ZIM file. More information may be
            available <a :href="errorUrl">via the Zimfarm API</a>. If you feel
            this was a transient or external error, you can try requesting your
            ZIM file again below.
          </p>
        </div>
      </div>
      <div
        v-if="
          status === 'NOT_REQUESTED' ||
          status === 'FAILED' ||
          (status != 'REQUESTED' && isDeleted)
        "
        class="row"
      >
        <div class="col-lg-6 col-md-9 mx-4">
          <form
            ref="form"
            v-on:submit.prevent="onSubmit"
            class="needs-validation"
            novalidate
          >
            <div id="desc-group" ref="form_group" class="form-group">
              <label for="desc">Description</label>
              <input
                id="desc"
                ref="desc"
                v-on:blur="validationOnBlur"
                v-model="description"
                class="form-control"
                maxlength="80"
                placeholder="ZIM file created from a WP1 Selection"
                required
              />
              <div class="invalid-feedback">Please provide a description</div>
            </div>
            <div class="form-group">
              <label for="longdesc">Long Description</label>
              <textarea
                id="longdesc"
                ref="longdesc"
                v-model="longDescription"
                rows="6"
                class="form-control"
                maxlength="4000"
                placeholder="ZIM file created from a WP1 Selection"
              ></textarea>
            </div>
            <div v-if="!success" class="error-list errors">
              <p>The following errors occurred:</p>
              <ul>
                <li v-for="msg in errors" v-bind:key="msg">
                  {{ msg }}
                </li>
              </ul>
            </div>
          </form>
          <div>
            <button
              id="request"
              v-on:click.prevent="onSubmit"
              class="btn btn-primary"
              type="button"
              :disabled="processing"
            >
              Request ZIM file
            </button>
            <pulse-loader
              id="loader"
              class="loader"
              :loading="processing || showLoader"
              :color="loaderColor"
              :size="loaderSize"
            ></pulse-loader>
          </div>
        </div>
      </div>
      <div v-else class="row">
        <div class="col-lg-6 col-md-9 mx-4">
          <a :href="zimPathFor()"
            ><button
              id="download"
              type="button"
              class="btn btn-primary"
              :disabled="status !== 'FILE_READY'"
            >
              Download ZIM
            </button></a
          >
          <pulse-loader
            id="loader"
            class="loader"
            :loading="processing || showLoader"
            :color="loaderColor"
            :size="loaderSize"
          ></pulse-loader>
        </div>
      </div>
    </div>
  </div>
  <div v-else>
    <LoginRequired></LoginRequired>
  </div>
</template>

<script>
import PulseLoader from 'vue-spinner/src/PulseLoader.vue';

import SecondaryNav from './SecondaryNav.vue';
import LoginRequired from './LoginRequired.vue';

export default {
  name: 'ZimFile',
  components: { SecondaryNav, LoginRequired, PulseLoader },
  data: function () {
    return {
      description: '',
      errors: [],
      errorMessages: [],
      errorUrl: '',
      isDeleted: false,
      loaderColor: '#007bff',
      loaderSize: '1rem',
      longDescription: '',
      notFound: false,
      pollId: null,
      processing: false,
      ready: false,
      serverError: false,
      status: null,
      success: true,
    };
  },
  created: async function () {
    await this.getBuilder();
    await this.getStatus();
    this.ready = true;
  },
  methods: {
    getBuilder: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${this.builderId}`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }
      );
      if (response.status == 404) {
        this.notFound = true;
      } else if (!response.ok) {
        this.serverError = true;
      } else {
        this.notFound = false;
        this.builder = await response.json();
        this.$emit('onBuilderLoaded', this.builder);
      }
    },
    getStatus: async function () {
      const url = `${import.meta.env.VITE_API_URL}/builders/${
        this.builderId
      }/zim/status`;
      const response = await fetch(url);

      if (!response.ok) {
        this.success = false;
        this.errors = 'An unknown server error has occurred.';
      }

      const data = await response.json();
      this.status = data.status;
      this.description = data.description;
      this.longDescription = data.long_description;
      this.isDeleted = data.is_deleted;
      if (this.status === 'FILE_READY') {
        this.stopProgressPolling();
      } else if (this.status === 'FAILED') {
        this.errorUrl = data.error_url;
      } else if (this.status !== 'NOT_REQUESTED') {
        this.startProgressPolling();
      }
    },
    onSubmit: async function () {
      const form = this.$refs.form;
      if (!form.checkValidity()) {
        this.$refs.form_group.classList.add('was-validated');
        return;
      }

      const postUrl = `${import.meta.env.VITE_API_URL}/builders/${
        this.builderId
      }/zim`;

      this.processing = true;
      const response = await fetch(postUrl, {
        headers: { 'Content-Type': 'application/json' },
        method: 'post',
        credentials: 'include',
        body: JSON.stringify({
          description: this.description,
          long_description: this.longDescription,
        }),
      });
      this.processing = false;

      if (!response.ok) {
        this.success = false;
        const data = await response.json();
        this.errors = data.error_messages;
        return;
      }

      await this.getStatus();
    },
    zimPathFor: function () {
      return `${import.meta.env.VITE_API_URL}/builders/${
        this.builderId
      }/zim/latest`;
    },
    startProgressPolling: function () {
      if (this.pollId) {
        return;
      }
      this.pollId = setInterval(() => this.getStatus(), 30000);
    },
    stopProgressPolling: function () {
      clearInterval(this.pollId);
    },
    validationOnBlur: function (event) {
      if (event.target.value) {
        event.target.classList.remove('is-invalid');
      } else {
        event.target.classList.add('is-invalid');
      }
    },
  },
  computed: {
    isLoggedIn: function () {
      return this.$root.$data.isLoggedIn;
    },
    builderId: function () {
      return this.$route.params.builder_id;
    },
    showLoader: function () {
      return (
        this.processing ||
        this.status === 'REQUESTED' ||
        this.status === 'ENDED'
      );
    },
  },
  watch: {
    builderId: function () {
      this.getBuilder();
    },
  },
};
</script>

<style scoped>
.errors {
  color: #dc3545;
}
.error-list {
  background-color: pink;
}
.loader {
  position: relative;
  top: 5px;
  display: inline-block;
  margin: 0 20px;
  text-align: center;
}
</style>
