<template>
  <div class="wp1r flex flex-1 flex-col bg-page">
    <div
      class="mx-auto flex w-full max-w-[1200px] flex-1 flex-col border-x border-border bg-surface"
    >
      <div v-if="!isLoggedIn" class="mx-auto w-full max-w-[760px]">
        <SelectionsNullState mode="signed-out" />
      </div>

      <div v-else-if="notFound" class="mx-auto w-full max-w-[760px] p-[22px]">
        <h1 class="m-0 mb-2 text-xl font-semibold">404 Not Found</h1>
        <p class="m-0 text-[13.5px] text-ink-2">
          Sorry, the selection with that ID either doesn't exist or isn't owned
          by you.
        </p>
      </div>

      <div
        v-else-if="serverError || noArticleCount"
        class="mx-auto w-full max-w-[760px] p-[22px]"
      >
        <h1 class="m-0 mb-2 text-xl font-semibold">500 Server error</h1>
        <p class="m-0 text-[13.5px] text-ink-2">
          Something went wrong and we couldn't retrieve the selection with that
          ID. You might try again later.
        </p>
      </div>

      <div v-else-if="ready" class="mx-auto w-full max-w-[760px]">
        <div class="border-b border-border-subtle px-5 pb-4 pt-6">
          <router-link
            v-if="builder"
            :to="`/selections/user/${builderId}`"
            class="text-[12.5px]"
            >← {{ builder.name }}</router-link
          >
          <h1 class="m-0 mt-1 text-[19px] font-semibold tracking-[-0.015em]">
            Create ZIM file
          </h1>
          <p
            v-if="articleCount !== null"
            class="mb-0 mt-1 font-mono text-[11.5px] text-ink-3"
          >
            {{ articleCount.toLocaleString() }} articles in the latest selection
          </p>
        </div>

        <div class="flex flex-col gap-4 px-5 py-[18px]">
          <!-- Active schedule -->
          <div
            v-if="isScheduleWarningRequired"
            class="rounded border border-warn-border bg-warn-tint px-3.5 py-3"
            role="alert"
          >
            <div class="text-[13.5px] font-semibold text-warn-text-strong">
              Active schedule found
            </div>
            <p
              class="mb-0 mt-1 text-[13px] leading-[1.5] text-warn-text-strong"
            >
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
              You can delete that schedule and request a new ZIM immediately or
              create a new schedule.
            </p>
            <button
              class="wp1r-btn mt-2 h-7 border-warn-border-2 bg-surface px-2.5 !text-warn-text-strong"
              :disabled="deletingSchedule"
              @click="deleteSchedule"
            >
              <span v-if="deletingSchedule">Deleting…</span>
              <span v-else>Delete schedule</span>
            </button>
          </div>

          <div v-else-if="status === 'NOT_REQUESTED'">
            <p class="m-0 text-[13.5px] leading-[1.55] text-ink-2">
              Use this form to create a ZIM file from your selection, so that
              you can browse the articles it contains offline.
            </p>
            <div
              v-if="tooManyArticles()"
              class="article-limit-exceeded mt-3 rounded border border-danger-border bg-danger-tint px-3.5 py-3"
            >
              <div class="text-[13.5px] font-semibold text-danger">
                Too many articles
              </div>
              <p class="mb-0 mt-1 text-[13px] leading-[1.5] text-ink-2">
                Oh no! It seems that you have hit the limit for the maximum
                number of articles ({{ articleCount.toLocaleString() }} /
                {{ maxArticleCount.toLocaleString() }}). Could it be that such a
                big selection could be useful to others? How about
                <a href="https://github.com/openzim/zim-requests"
                  >opening a zim-request</a
                >
                so that we can look into it, and add it straight to the Kiwix
                library?
              </p>
            </div>
          </div>
          <p v-else class="m-0 text-[13.5px] leading-[1.55] text-ink-2">
            Once you request a ZIM file, it will be queued for creation. This
            page and the Selections page will automatically update with a URL to
            download your ZIM file once it is ready.
          </p>

          <p
            v-if="forceExpiredDisplay || (isDeleted && status == 'FILE_READY')"
            class="m-0 text-[13px] text-danger"
          >
            Your ZIM file has expired and needs to be re-created. ZIM file
            download links are only valid for 2 weeks. You can re-create your
            ZIM file with the button below.
          </p>
          <p
            v-else-if="status === 'REQUESTED'"
            class="m-0 flex items-center gap-2 text-[13px]"
          >
            <span
              aria-hidden="true"
              class="h-[7px] w-[7px] rounded-full bg-accent"
            ></span>
            Your ZIM file has been requested and is being processed. This page
            will update with the URL to download it once it is ready.
          </p>
          <p
            v-else-if="status === 'FILE_READY'"
            class="m-0 flex items-center gap-2 text-[13px]"
          >
            <span
              aria-hidden="true"
              class="h-[7px] w-[7px] rounded-full bg-ok"
            ></span>
            Your ZIM file is ready! Click the button below to download it.
          </p>
          <p
            v-else-if="status === 'FAILED'"
            class="m-0 text-[13px] text-danger"
          >
            There was an error creating your ZIM file. More information may be
            available <a :href="errorUrl">via the Zimfarm API</a>. If you feel
            this was a transient or external error, you can try requesting your
            ZIM file again below.
          </p>
          <p
            v-if="
              flavour &&
              (status === 'FILE_READY' ||
                status === 'REQUESTED' ||
                status === 'FAILED')
            "
            class="m-0 text-[13px] text-ink-3"
          >
            <span class="font-medium text-ink-2">Content:</span>
            {{ selectedFlavourDescription }}
          </p>

          <!-- ============ Request form ============ -->
          <form
            v-if="showForm"
            ref="form"
            class="flex flex-col gap-3.5"
            @submit.prevent="onSubmit"
          >
            <div id="zimtitle-group">
              <label
                for="zimtitle"
                class="mb-1 block text-xs font-medium text-ink-2"
                >Title</label
              >
              <input
                id="zimtitle"
                ref="zimtitle"
                v-model="zimTitle"
                class="wp1r-input h-8 w-full"
                placeholder="ZIM title"
                @input="validateInput('zimTitle', maxTitleLength)"
              />
              <small
                class="mt-1 block font-mono text-[11px]"
                :class="
                  graphemeCount(zimTitle) === maxTitleLength
                    ? 'text-warn-text'
                    : 'text-ink-4'
                "
              >
                {{ displayGraphemeLimitText(zimTitle, maxTitleLength) }}
              </small>
            </div>
            <div id="desc-group">
              <label
                for="desc"
                class="mb-1 block text-xs font-medium text-ink-2"
                >Description</label
              >
              <input
                id="desc"
                ref="desc"
                v-model="description"
                class="wp1r-input h-8 w-full"
                placeholder="ZIM file created from a WP1 Selection"
                @input="validateInput('description', maxDescriptionLength)"
              />
              <small
                class="mt-1 block font-mono text-[11px]"
                :class="
                  graphemeCount(description) === maxDescriptionLength
                    ? 'text-warn-text'
                    : 'text-ink-4'
                "
              >
                {{
                  displayGraphemeLimitText(description, maxDescriptionLength)
                }}
              </small>
            </div>
            <div id="long-desc-group">
              <label
                for="longdesc"
                class="mb-1 block text-xs font-medium text-ink-2"
                >Long description</label
              >
              <textarea
                id="longdesc"
                ref="longdesc"
                v-model="longDescription"
                rows="6"
                class="wp1r-input w-full py-2"
                :class="{ '!border-danger-border': !isLongDescriptionValid }"
                style="resize: vertical"
                placeholder="ZIM file created from a WP1 Selection"
                @input="
                  validateInput('longDescription', maxLongDescriptionLength)
                "
              ></textarea>
              <small
                class="mt-1 block font-mono text-[11px]"
                :class="
                  graphemeCount(longDescription) === maxLongDescriptionLength
                    ? 'text-warn-text'
                    : 'text-ink-4'
                "
              >
                {{
                  displayGraphemeLimitText(
                    longDescription,
                    maxLongDescriptionLength
                  )
                }}
              </small>
              <div
                v-if="!isLongDescriptionValid"
                class="mt-1 text-[12.5px] text-danger"
              >
                Long description must differ from description and not be shorter
              </div>
            </div>
            <div id="flavour-group">
              <label
                for="flavour"
                class="mb-1 block text-xs font-medium text-ink-2"
                >What to include</label
              >
              <select
                id="flavour"
                v-model="flavour"
                class="wp1r-select h-8 w-full"
              >
                <option
                  v-for="opt in flavourOptions"
                  :key="opt.value"
                  :value="opt.value"
                >
                  {{ opt.description }}
                </option>
              </select>
            </div>

            <!-- Scheduling -->
            <label
              class="flex cursor-pointer items-center gap-2 text-[13px]"
              for="enableScheduling"
            >
              <input
                id="enableScheduling"
                v-model="schedulingEnabled"
                type="checkbox"
              />
              Schedule repeated ZIM generations
            </label>

            <div
              v-if="schedulingEnabled"
              class="flex flex-col gap-3 rounded border border-border-strong bg-surface-muted px-3.5 py-3"
            >
              <div>
                <label
                  for="repetitionPeriod"
                  class="mb-1 block text-xs font-medium text-ink-2"
                  >Repetition period (months)</label
                >
                <select
                  id="repetitionPeriod"
                  v-model.number="repetitionPeriodInMonths"
                  class="wp1r-select h-8 w-full"
                >
                  <option v-for="m in [1, 3, 6]" :key="m" :value="m">
                    {{ m }}
                  </option>
                </select>
              </div>
              <div>
                <label
                  for="numberOfRepetitions"
                  class="mb-1 block text-xs font-medium text-ink-2"
                  >Number of repetitions</label
                >
                <select
                  id="numberOfRepetitions"
                  v-model.number="numberOfRepetitions"
                  class="wp1r-select h-8 w-full"
                >
                  <option v-for="n in [1, 2, 3]" :key="n" :value="n">
                    {{ n }}
                  </option>
                </select>
              </div>
              <div>
                <label
                  for="scheduleEmail"
                  class="mb-1 block text-xs font-medium text-ink-2"
                  >Notification email (optional)</label
                >
                <input
                  id="scheduleEmail"
                  v-model.trim="scheduleEmail"
                  type="email"
                  class="wp1r-input h-8 w-full"
                  placeholder="you@example.org"
                />
                <small class="mt-1 block text-[11.5px] text-ink-4"
                  >We'll notify you when each scheduled ZIM is ready.</small
                >
              </div>
            </div>

            <div
              v-if="!success"
              class="error-list rounded border border-danger-border bg-danger-tint px-3.5 py-3"
            >
              <p class="m-0 text-[13px] font-medium text-danger">
                The following errors occurred:
              </p>
              <ul class="mb-0 mt-1 list-disc pl-5 text-[13px] text-ink-2">
                <li v-for="msg in errors" :key="msg">{{ msg }}</li>
              </ul>
            </div>

            <div class="flex items-center gap-2.5">
              <button
                id="request"
                type="submit"
                class="wp1r-btn-primary h-8 px-3.5"
                :disabled="processing || tooManyArticles()"
              >
                {{ processing ? 'Requesting…' : 'Request ZIM file' }}
              </button>
            </div>
          </form>

          <!-- ============ Download ============ -->
          <div
            v-else-if="
              !forceExpiredDisplay &&
              (status === 'FILE_READY' || status === 'REQUESTED')
            "
            class="flex items-center gap-2.5"
          >
            <a :href="zimPathFor()">
              <button
                id="download"
                type="button"
                class="wp1r-btn-primary h-8 px-3.5"
                :disabled="status !== 'FILE_READY'"
              >
                Download ZIM
              </button>
            </a>
            <span v-if="status === 'REQUESTED'" class="text-[12.5px] text-ink-3"
              >Building…</span
            >
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { byGrapheme } from 'split-by-grapheme';

import SelectionsNullState from './SelectionsNullState.vue';
import { loginStore } from '../../store.js';

export default {
  name: 'ZimPage',
  components: { SelectionsNullState },
  data: function () {
    return {
      builder: null,
      zimTitle: '',
      articleCount: null,
      maxArticleCount: null,
      description: '',
      errors: [],
      errorUrl: '',
      isDeleted: false,
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
      forceExpiredDisplay: false,
      flavour: '',
      flavourOptions: [
        { value: '', label: 'All', description: 'Everything including videos' },
        {
          value: 'maxi',
          label: 'Maxi',
          description: 'All except article videos',
        },
        {
          value: 'nopic',
          label: 'Nopic',
          description: 'No article pictures or videos',
        },
        {
          value: 'mini',
          label: 'Mini',
          description: 'No article details or pictures or videos',
        },
      ],
    };
  },
  created: async function () {
    await this.getBuilder();
    await this.getStatus();
    if (this.$route.query.expired) {
      this.forceExpiredDisplay = true;
    }
    await this.loadUserEmail();
    this.ready = true;
  },
  beforeUnmount: function () {
    this.stopProgressPolling();
  },
  methods: {
    loadUserEmail: async function () {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/oauth/email`, {
        credentials: 'include',
      });
      if (res.ok) {
        const data = await res.json();
        if (data && data.email && !this.scheduleEmail) {
          this.scheduleEmail = data.email;
        }
      }
    },
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
        if (this.builder && this.builder.name) {
          this.zimTitle = this.truncateToLength(
            this.builder.name,
            this.maxTitleLength
          );
        }
        await this.getArticleCount();
      }
    },
    getStatus: async function () {
      const url = `${import.meta.env.VITE_API_URL}/builders/${
        this.builderId
      }/zim/status`;
      const response = await fetch(url);

      if (!response.ok) {
        this.success = false;
        this.errors = ['An unknown server error has occurred.'];
        return;
      }

      const data = await response.json();
      this.status = data.status;
      this.isDeleted = data.is_deleted;
      this.activeSchedule = data.active_schedule;
      if (data.flavour) {
        this.flavour = data.flavour;
      }
      if (this.status === 'FILE_READY') {
        this.stopProgressPolling();
      } else if (this.status === 'FAILED') {
        this.errorUrl = data.error_url;
      } else if (this.status !== 'NOT_REQUESTED') {
        this.startProgressPolling();
      }
    },
    getArticleCount: async function () {
      const url = `${import.meta.env.VITE_API_URL}/builders/${
        this.builderId
      }/selection/latest/article_count`;
      const response = await fetch(url, {
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      });

      if (!response.ok) {
        this.noArticleCount = true;
        return;
      }
      const data = await response.json();

      this.articleCount = data.selection.article_count;
      this.maxArticleCount = data.selection.max_article_count;
    },
    onSubmit: async function () {
      this.errors = [];
      if (!this.zimTitle) {
        this.errors.push('Please provide a title');
      }
      if (!this.description) {
        this.errors.push('Please provide a description');
      }
      if (!this.isLongDescriptionValid) {
        this.errors.push(
          'Long description must differ from description and not be shorter'
        );
      }
      if (
        this.schedulingEnabled &&
        this.scheduleEmail &&
        !this.isValidEmail(this.scheduleEmail)
      ) {
        this.errors.push('Please provide a valid email');
      }
      if (this.errors.length) {
        this.success = false;
        return;
      }
      this.success = true;

      const postUrl = `${import.meta.env.VITE_API_URL}/builders/${
        this.builderId
      }/zim`;

      this.processing = true;
      const payload = {
        title: this.zimTitle,
        description: this.description,
        long_description: this.longDescription,
      };
      if (this.flavour) {
        payload.flavour = this.flavour;
      }
      if (this.schedulingEnabled) {
        const scheduled = {
          repetition_period_in_months: this.repetitionPeriodInMonths,
          number_of_repetitions: this.numberOfRepetitions,
        };
        const email = (this.scheduleEmail || '').trim();
        if (email.length > 0) {
          scheduled.email = email;
        }
        payload.scheduled_repetitions = scheduled;
      }

      const response = await fetch(postUrl, {
        headers: { 'Content-Type': 'application/json' },
        method: 'post',
        credentials: 'include',
        body: JSON.stringify(payload),
      });
      this.processing = false;

      if (!response.ok) {
        this.success = false;
        try {
          const data = await response.json();
          this.errors = data.error_messages || [data.error || 'Request failed'];
        } catch (e) {
          const text = await response.text();
          this.errors = [text || 'Request failed'];
        }
        return;
      }

      this.forceExpiredDisplay = false;
      await this.getStatus();
    },
    validateInput: function (field, maxLength) {
      if (this.graphemeCount(this[field]) > maxLength) {
        this[field] = this.truncateToLength(this[field], maxLength);
      }
    },
    truncateToLength: function (text, maxLength) {
      const graphemes = text.split(byGrapheme);
      return graphemes.slice(0, maxLength).join('');
    },
    tooManyArticles: function () {
      return this.articleCount > this.maxArticleCount;
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
      this.pollId = null;
    },
    graphemeCount: function (text) {
      return text.split(byGrapheme).length;
    },
    displayGraphemeLimitText: function (text, maxLength) {
      const count = this.graphemeCount(text);
      return `${count}/${maxLength} graphemes${
        count === maxLength ? ' (max reached)' : ''
      }`;
    },
    isValidEmail: function (email) {
      if (!email) return false;
      return /.+@.+\..+/.test(email);
    },
    deleteSchedule: async function () {
      if (!this.activeSchedule) return;

      this.deletingSchedule = true;
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/builders/${this.builderId}/schedule`,
          {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
          }
        );

        if (response.ok) {
          this.activeSchedule = null;
          await this.getStatus();
        } else {
          const errorData = await response.json();
          this.errors = errorData.error_messages || [
            'Failed to delete schedule',
          ];
          this.success = false;
        }
      } catch (error) {
        this.errors = ['Failed to delete schedule: ' + error.message];
        this.success = false;
      } finally {
        this.deletingSchedule = false;
      }
    },
    formatDate: function (dateString) {
      if (!dateString) return 'Unknown';
      // Wikipedia-style (ISO) date; the backend already sends YYYY-MM-DD.
      return String(dateString).slice(0, 10);
    },
  },
  computed: {
    isLoggedIn: function () {
      return loginStore.isLoggedIn;
    },
    builderId: function () {
      return this.$route.params.builder_id;
    },
    showForm: function () {
      return (
        !this.activeSchedule &&
        (this.forceExpiredDisplay ||
          this.status === 'NOT_REQUESTED' ||
          this.status === 'FAILED' ||
          (this.status != 'REQUESTED' && this.isDeleted))
      );
    },
    isLongDescriptionValid: function () {
      if (!this.longDescription || !this.description) return true;
      const longCount = this.graphemeCount(this.longDescription);
      const descCount = this.graphemeCount(this.description);
      return (
        longCount >= descCount && this.longDescription !== this.description
      );
    },
    isScheduleWarningRequired: function () {
      return this.activeSchedule && this.status !== 'REQUESTED';
    },
    selectedFlavourDescription: function () {
      const opt = this.flavourOptions.find((o) => o.value === this.flavour);
      return opt ? opt.description : '';
    },
  },
  watch: {
    builderId: function () {
      this.getBuilder();
    },
  },
};
</script>
