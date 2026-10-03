<template>
  <div class="wp1r flex flex-1 flex-col bg-page">
    <div
      class="mx-auto flex w-full max-w-[1200px] flex-1 flex-col border-x border-border bg-surface"
    >
      <div v-if="isLoggedIn" class="px-[18px] pb-16 pt-6 max-md:px-3">
        <h2 class="m-0 text-[19px] font-semibold tracking-[-0.015em]">
          Manual update
        </h2>
        <div
          class="mt-3 max-w-[720px] rounded border border-warn-border bg-warn-tint px-3 py-2 text-[13px] leading-[1.5] text-warn-text-strong"
        >
          This tool can perform a manual update <b>once per hour at most</b>,
          and not until all pending updates are complete.
        </div>
        <div class="mt-4 max-w-[560px]">
          <Autocomplete
            label="Project"
            :incomingSearch="incomingSearch || $route.params.projectName"
            v-on:select-project="currentProject = $event"
          ></Autocomplete>
        </div>

        <div
          v-if="currentProject && !updateTime && !jobScheduled"
          class="mt-5 max-w-[560px] rounded border border-border p-[14px]"
        >
          <p class="m-0 text-[13.5px] text-ink">
            Proceed with manual update of <b>{{ currentProject }}</b
            >?
          </p>
          <button
            type="button"
            class="wp1r-btn-primary mt-3 h-8 px-4"
            v-on:click="onUpdateClick()"
          >
            Manual Update
          </button>
        </div>

        <div
          v-if="currentProject && (updateTime || jobScheduled)"
          class="mt-5 max-w-[560px] rounded border border-border p-[14px]"
        >
          <p class="m-0 text-[13px] leading-[1.55] text-ink-2">
            Manual update of
            <b class="text-ink">{{ $route.params.projectName }}</b> has been
            scheduled. It can take anywhere from 2 - 200 minutes, depending on
            project size. The next update can be performed
            <span v-if="updateTime"
              >at <b class="font-mono text-[12px] text-ink">{{ updateTime }}</b
              >.</span
            >
            <span v-else>when the current update completes.</span>
          </p>
          <p class="mb-1 mt-3 text-[13px] text-ink">
            <b>Progress:</b>
            {{ getProgressString() }}
          </p>

          <template v-if="!jobComplete && !jobNotStarted">
            <div
              class="h-[6px] overflow-hidden rounded-full bg-border-row"
              role="progressbar"
              :aria-valuenow="progressCurrent"
              aria-valuemin="0"
              :aria-valuemax="progressTotal"
            >
              <div
                class="h-full rounded-full bg-accent"
                :style="{ width: progressWidth + '%' }"
              ></div>
            </div>
            <div
              v-if="progressCurrent !== null && progressTotal !== null"
              class="mt-1.5 font-mono text-[11.5px] text-ink-3"
            >
              {{ progressCurrent.toLocaleString() }} /
              {{ progressTotal.toLocaleString() }} articles
            </div>
          </template>
        </div>
      </div>
      <LoginRequired v-else></LoginRequired>
    </div>
  </div>
</template>

<script>
import Autocomplete from './Autocomplete.vue';
import LoginRequired from './LoginRequired.vue';
import { loginStore } from '../store.js';

export default {
  name: 'update-page',
  components: {
    Autocomplete,
    LoginRequired,
  },
  props: ['incomingSearch'],
  data: function () {
    return {
      currentProject: null,
      updateTime: null,
      pollingId: 0,
      progressCurrent: null,
      progressTotal: null,
      jobStatusEnum: null,
    };
  },
  computed: {
    currentProjectId: function () {
      if (!this.currentProject) {
        return null;
      }
      return this.currentProject.replace(/ /g, '_');
    },
    jobComplete: function () {
      return this.jobStatusEnum === 'finished';
    },
    jobFinishingUp: function () {
      return (
        this.jobStatusEnum !== null &&
        this.jobStatusEnum !== 'finished' &&
        this.progressTotal > 0 &&
        this.progressCurrent >= this.progressTotal
      );
    },
    jobNotStarted: function () {
      return this.jobStatusEnum === null || this.jobStatusEnum === 'queued';
    },
    jobScheduled: function () {
      return (
        this.jobStatusEnum === 'queued' || this.jobStatusEnum === 'started'
      );
    },
    progressWidth: function () {
      if (this.progressCurrent !== null && this.progressTotal !== null) {
        return ((this.progressCurrent * 100) / this.progressTotal).toFixed(4);
      }
      return null;
    },
    isLoggedIn: function () {
      return loginStore.isLoggedIn;
    },
  },
  watch: {
    currentProject: async function (val) {
      this.stopProgressPolling();
      if (val !== this.$route.params.projectName) {
        this.$router.push({ path: `/update/${val}` });
      }
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${
          this.currentProjectId
        }/update/time`
      );
      const data = await response.json();
      this.updateTime = data.next_update_time;
      this.progressCurrent = null;
      this.progressTotal = null;
      this.jobStatusEnum = null;
    },
    updateTime: function (val) {
      if (val !== null) {
        this.startProgressPolling();
      } else {
        this.stopProgressPolling();
      }
    },
  },
  beforeRouteUpdate(to, from, next) {
    this.stopProgressPolling();
    next();
  },
  beforeRouteLeave: function (to, from, next) {
    this.stopProgressPolling();
    next();
  },
  methods: {
    onUpdateClick: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${
          this.currentProjectId
        }/update`,
        { method: 'POST', credentials: 'include' }
      );
      const data = await response.json();
      this.updateTime = data.next_update_time;
    },
    pollForProgress: async function () {
      if (!this.isLoggedIn) {
        return;
      }
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/projects/${
          this.currentProjectId
        }/update/progress`
      );
      const data = await response.json();
      this.progressCurrent = (data.job && data.job.progress) || null;
      this.progressTotal = (data.job && data.job.total) || null;
      this.jobStatusEnum = (data.queue && data.queue.status) || null;
      if (this.jobComplete) {
        this.stopProgressPolling();
      }
    },
    getProgressString: function () {
      if (this.jobNotStarted) {
        return "Your job has been scheduled, but hasn't started yet.";
      }
      if (this.jobComplete) {
        return (
          'Your job is complete! You must wait up to an hour to start ' +
          'a new manual update.'
        );
      }
      if (this.jobFinishingUp) {
        return 'Your job is almost finished, just wrapping up some tasks.';
      }
      return 'Your job is running, track its progress below.';
    },
    startProgressPolling: function () {
      this.pollForProgress();
      this.pollingId = setInterval(() => this.pollForProgress(), 2000);
    },
    stopProgressPolling: function () {
      clearInterval(this.pollingId);
    },
  },
};
</script>
