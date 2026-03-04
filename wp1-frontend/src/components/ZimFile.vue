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
    <div v-else-if="serverError || noArticleCount">
      <h2>500 Server error</h2>
      Something went wrong and we couldn't retrieve the list with that ID. You
      might try again later.
    </div>
    <div v-else-if="ready">
      <div class="row">
        <div class="col-lg-6 col-md-9 mx-4">
          <h3>Create ZIM file</h3>

          <!-- Active Schedule Warning -->
          <div
            v-if="isScheduleWarningRequired"
            class="alert alert-warning"
            role="alert"
          >
            <h5 class="alert-heading">📅 Active Schedule Found</h5>
            <p>
              You already have a ZIM scheduled for every
              <strong
                >{{ activeSchedule.interval_months }} month{{
                  activeSchedule.interval_months > 1 ? 's' : ''
                }}</strong
              >.
              <span v-if="activeSchedule.next_generation_date">
                The next ZIM will be generated on
                <strong>{{
                  formatDate(activeSchedule.next_generation_date)
                }}</strong
                >.
              </span>
            </p>
            <p class="mb-2">
              You can delete that schedule and request a new ZIM immediately or
              create a new schedule.
            </p>
            <button
              @click="deleteSchedule"
              class="btn btn-outline-danger btn-sm"
              :disabled="deletingSchedule"
            >
              <span v-if="deletingSchedule">Deleting...</span>
              <span v-else>Delete Schedule</span>
            </button>
          </div>

          <div v-else-if="status === 'NOT_REQUESTED'">
            <p>
              Use this form to create a ZIM file from your selection, so that
              you can browse the articles it contains offline. The
              &quot;Description&quot; and &quot;Long Description&quot; fields
              are required, but generic defaults will be used if they're not
              provided.
            </p>
            <div v-if="tooManyArticles()" class="article-limit-exceeded errors">
              <h2>Too many articles</h2>
              <p>
                Oh no! It seems that you have hit the limit for the maximum
                number of articles ({{ this.articleCount.toLocaleString() }} /
                {{ this.maxArticleCount.toLocaleString() }}). Could it be that
                such a big selection could be useful to others? How about
                <a href="https://github.com/openzim/zim-requests"
                  >opening a zim-request</a
                >
                so that we can look into it, and add it straight to the Kiwix
                library?
              </p>
            </div>
          </div>
          <p v-else>
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
          !activeSchedule &&
          (status === 'NOT_REQUESTED' ||
            status === 'FAILED' ||
            (status != 'REQUESTED' && isDeleted))
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
            <div
              id="zimtitle-group"
              ref="zimtitle_form_group"
              class="form-group"
            >
              <label for="zimtitle">Title</label>
              <input
                id="zimtitle"
                ref="zimtitle"
                v-on:blur="validationOnBlur"
                v-on:input="validateInput('zimTitle', maxTitleLength)"
                v-model="zimTitle"
                class="form-control"
                placeholder="ZIM title"
                required
              />
              <small
                class="form-text"
                :class="{
                  'text-muted': graphemeCount(zimTitle) < maxTitleLength,
                  'text-warning': graphemeCount(zimTitle) === maxTitleLength,
                }"
              >
                {{ displayGraphemeLimitText(zimTitle, maxTitleLength) }}
              </small>
              <div class="invalid-feedback">Please provide a title</div>
            </div>
            <div id="desc-group" ref="form_group" class="form-group">
              <label for="desc">Description</label>
              <input
                id="desc"
                ref="desc"
                v-on:blur="validationOnBlur"
                v-on:input="validateInput('description', maxDescriptionLength)"
                v-model="description"
                class="form-control"
                placeholder="ZIM file created from a WP1 Selection"
                required
              />
              <small
                class="form-text"
                :class="{
                  'text-muted':
                    graphemeCount(description) < maxDescriptionLength,
                  'text-warning':
                    graphemeCount(description) === maxDescriptionLength,
                }"
              >
                {{
                  displayGraphemeLimitText(description, maxDescriptionLength)
                }}
              </small>
              <div class="invalid-feedback">Please provide a description</div>
            </div>
            <div id="long-desc-group" class="form-group">
              <label for="longdesc">Long Description</label>
              <textarea
                id="longdesc"
                ref="longdesc"
                v-model="longDescription"
                v-on:input="
                  validateInput('longDescription', maxLongDescriptionLength)
                "
                rows="6"
                class="form-control"
                :class="{ 'is-invalid': !isLongDescriptionValid }"
                placeholder="ZIM file created from a WP1 Selection"
              ></textarea>
              <small
                class="form-text"
                :class="{
                  'text-muted':
                    graphemeCount(longDescription) < maxLongDescriptionLength,
                  'text-warning':
                    graphemeCount(longDescription) === maxLongDescriptionLength,
                }"
              >
                {{
                  displayGraphemeLimitText(
                    longDescription,
                    maxLongDescriptionLength
                  )
                }}
              </small>
              <div class="invalid-feedback">
                Long description must differ from description and not be shorter
              </div>
            </div>
            <!-- Scheduling options -->
            <div class="form-group form-check mt-3">
              <input
                type="checkbox"
                class="form-check-input"
                id="enableScheduling"
                v-model="schedulingEnabled"
              />
              <label class="form-check-label" for="enableScheduling"
                >Schedule repeated ZIM generations</label
              >
            </div>

            <div v-if="schedulingEnabled" class="border rounded p-3 mb-3">
              <div class="form-group">
                <label for="repetitionPeriod">Repetition period (months)</label>
                <select
                  id="repetitionPeriod"
                  class="form-control"
                  v-model.number="repetitionPeriodInMonths"
                >
                  <option v-for="m in [1, 3, 6]" :key="m" :value="m">
                    {{ m }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="numberOfRepetitions">Number of repetitions</label>
                <select
                  id="numberOfRepetitions"
                  class="form-control"
                  v-model.number="numberOfRepetitions"
                >
                  <option v-for="n in [1, 2, 3]" :key="n" :value="n">
                    {{ n }}
                  </option>
                </select>
              </div>

              <div class="form-group">
                <label for="scheduleEmail">Notification email (optional)</label>
                <input
                  id="scheduleEmail"
                  type="email"
                  class="form-control"
                  v-model.trim="scheduleEmail"
                  placeholder="you@example.org"
                />
                <small class="form-text text-muted"
                  >We'll notify you when each scheduled ZIM is ready.</small
                >
                <div class="invalid-feedback">Please provide a valid email</div>
              </div>
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
              :disabled="processing || tooManyArticles()"
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
      <div
        v-else-if="status === 'FILE_READY' || status === 'REQUESTED'"
        class="row"
      >
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
import { byGrapheme } from 'split-by-grapheme'
import PulseLoader from 'vue-spinner/src/PulseLoader.vue'

import LoginRequired from './LoginRequired.vue'
import SecondaryNav from './SecondaryNav.vue'

export default {
  name: 'ZimFile',
  components: { SecondaryNav, LoginRequired, PulseLoader },

  data() {
    return {
      zimTitle: '',
      articleCount: null,
      maxArticleCount: null,
      description: '',
      errors: [],
      errorUrl: '',
      isDeleted: false,
      loaderColor: '#007bff',
      loaderSize: '1rem',
      longDescription: '',
      notFound: false,
      noArticleCount: false,
      pollId: null,
      processing: false,
      ready: false,
      serverError: false,
      status: null,
      success: true,
      activeSchedule: null,
      deletingSchedule: false,
      maxTitleLength: 30,
      maxDescriptionLength: 80,
      maxLongDescriptionLength: 4000,
      schedulingEnabled: false,
      repetitionPeriodInMonths: 1,
      numberOfRepetitions: 1,
      scheduleEmail: '',
      builder: null
    }
  },

  async created() {
    await this.getBuilder()
    await this.getStatus()
    await this.loadUserEmail()
    this.ready = true
  },

  methods: {
    async loadUserEmail() {
      const res = await fetch(
        `${import.meta.env.VITE_API_URL}/oauth/email`,
        { credentials: 'include' }
      )

      if (res.ok) {
        const data = await res.json()
        if (data?.email && !this.scheduleEmail) {
          this.scheduleEmail = data.email
        }
      }
    },

    async getBuilder() {
      if (!this.builderId) return

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${this.builderId}`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include'
        }
      )

      if (response.status === 404) {
        this.notFound = true
        return
      }

      if (!response.ok) {
        this.serverError = true
        return
      }

      this.notFound = false
      this.builder = await response.json()

      if (this.builder?.name) {
        this.zimTitle = this.truncateToLength(
          this.builder.name,
          this.maxTitleLength
        )
      }

      await this.getArticleCount()
      this.$emit('onBuilderLoaded', this.builder)
    },

    async getStatus() {
      if (!this.builderId) return

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${this.builderId}/zim/status`,
        { credentials: 'include' }
      )

      if (!response.ok) {
        this.success = false
        this.errors = ['An unknown server error has occurred.']
        return
      }

      const data = await response.json()

      this.status = data.status
      this.isDeleted = data.is_deleted
      this.activeSchedule = data.active_schedule

      if (this.status === 'FILE_READY') {
        this.stopProgressPolling()
      } else if (this.status === 'FAILED') {
        this.errorUrl = data.error_url
        this.stopProgressPolling()
      } else if (this.status !== 'NOT_REQUESTED') {
        this.startProgressPolling()
      }
    },

    async getArticleCount() {
      if (!this.builderId) return

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${this.builderId}/selection/latest/article_count`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include'
        }
      )

      if (!response.ok) {
        this.noArticleCount = true
        return
      }

      const data = await response.json()
      this.articleCount = data.article_count
    },

    async onSubmit() {
      if (this.hasLengthErrors) return

      const postUrl =
        `${import.meta.env.VITE_API_URL}/builders/${this.builderId}/zim`

      this.processing = true

      const payload = {
        title: this.zimTitle,
        description: this.description,
        long_description: this.longDescription
      }

      if (this.schedulingEnabled) {
        const scheduled = {
          repetition_period_in_months: this.repetitionPeriodInMonths,
          number_of_repetitions: this.numberOfRepetitions
        }

        if (this.scheduleEmail?.trim()) {
          scheduled.email = this.scheduleEmail.trim()
        }

        payload.scheduled_repetitions = scheduled
      }

      const response = await fetch(postUrl, {
        headers: { 'Content-Type': 'application/json' },
        method: 'POST',
        credentials: 'include',
        body: JSON.stringify(payload)
      })

      this.processing = false

      if (!response.ok) {
        this.success = false
        try {
          const data = await response.json()
          this.errors =
            data.error_messages || [data.error || 'Request failed']
        } catch {
          this.errors = ['Request failed']
        }
        return
      }

      await this.getStatus()
    },

    truncateToLength(text, maxLength) {
      return text.split(byGrapheme).slice(0, maxLength).join('')
    },

    graphemeCount(text) {
      return text.split(byGrapheme).length
    },

    validateInput(field, maxLength) {
      if (this.graphemeCount(this[field]) > maxLength) {
        this[field] = this.truncateToLength(this[field], maxLength)
      }
    },

    validationOnBlur(event) {
      if (event.target.value) {
        event.target.classList.remove('is-invalid')
      } else {
        event.target.classList.add('is-invalid')
      }
    },

    displayGraphemeLimitText(text, maxLength) {
      const count = this.graphemeCount(text)
      return `${count}/${maxLength} graphemes${
        count === maxLength ? ' (max reached)' : ''
      }`
    },

    formatDate(dateString) {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },

    startProgressPolling() {
      if (this.pollId) return
      this.pollId = setInterval(() => this.getStatus(), 30000)
    },

    stopProgressPolling() {
      if (this.pollId) {
        clearInterval(this.pollId)
        this.pollId = null
      }
    },

    async deleteSchedule() {
      if (!this.activeSchedule) return

      this.deletingSchedule = true

      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/builders/${this.builderId}/schedule`,
          {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include'
          }
        )

        if (response.ok) {
          this.activeSchedule = null
          await this.getStatus()
        } else {
          this.success = false
          this.errors = ['Failed to delete schedule']
        }
      } finally {
        this.deletingSchedule = false
      }
    }
  },

  computed: {
    builderId() {
      return this.$route.params.builder_id
    },

    isLoggedIn() {
      return this.$root.$data.isLoggedIn
    },

    showLoader() {
      return (
        this.processing ||
        this.status === 'REQUESTED' ||
        this.status === 'ENDED'
      )
    },

    hasLengthErrors() {
      return !this.zimTitle || !this.description
    },

    isLongDescriptionValid() {
      if (!this.longDescription || !this.description) return true

      const longCount = this.graphemeCount(this.longDescription)
      const descCount = this.graphemeCount(this.description)

      return (
        longCount >= descCount &&
        this.longDescription !== this.description
      )
    },

    isScheduleWarningRequired() {
      return this.activeSchedule && this.status !== 'REQUESTED'
    }
  }
}
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