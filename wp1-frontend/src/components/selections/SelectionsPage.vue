<template>
  <div class="wp1r flex flex-1 flex-col bg-page">
    <div
      class="mx-auto flex w-full max-w-[1200px] flex-1 flex-col border-x border-border bg-surface"
    >
      <div v-if="!isLoggedIn" class="mx-auto w-full max-w-[760px]">
        <SelectionsNullState mode="signed-out" />
      </div>

      <!-- A fetch failure must not render the onboarding empty state. -->
      <div
        v-else-if="loadError"
        id="list-load-error"
        class="mx-auto flex w-full max-w-[760px] flex-wrap items-center justify-center gap-2 px-6 py-10 text-[13px]"
      >
        <span class="text-danger">Couldn't load your selections.</span>
        <button
          id="retry-load-lists"
          type="button"
          class="wp1r-btn-secondary h-6 px-2 text-xs"
          @click="getLists"
        >
          Retry
        </button>
      </div>

      <div
        v-else-if="loaded && list.length === 0"
        class="mx-auto w-full max-w-[760px]"
      >
        <SelectionsNullState mode="empty" />
      </div>

      <template v-else>
        <!-- ============ Desktop: rail + detail ============ -->
        <div
          class="hidden flex-1 md:grid"
          :class="
            editing
              ? 'md:grid-cols-[220px_minmax(0,1fr)]'
              : 'md:grid-cols-[400px_minmax(0,1fr)]'
          "
        >
          <!-- Left rail -->
          <aside
            class="flex min-h-0 flex-col border-r border-border-strong"
            :class="{ 'bg-surface-muted': editing }"
          >
            <div
              v-if="!editing"
              class="flex flex-col gap-[9px] border-b border-border-subtle px-3 pb-3 pt-6"
            >
              <div class="flex items-center justify-between">
                <h1 class="m-0 text-[15px] font-semibold">Selections</h1>
                <router-link
                  id="new-selection-button"
                  to="/selections/new"
                  class="wp1r-btn-primary h-7 px-[9px] text-xs"
                  >New</router-link
                >
              </div>
              <label
                class="flex h-7 cursor-text items-center gap-1.5 rounded border border-border px-2 focus-within:border-accent focus-within:ring-1 focus-within:ring-accent-border-2"
              >
                <span aria-hidden="true" class="font-mono text-xs text-ink-4"
                  >/</span
                >
                <input
                  ref="search"
                  v-model="query"
                  type="text"
                  placeholder="Filter…"
                  class="w-full border-0 bg-transparent p-0 text-[13px] outline-none focus:!outline-none"
                  aria-label="Filter selections"
                />
              </label>
              <div class="flex flex-wrap gap-1">
                <button
                  v-for="chip in statusFilters"
                  :key="chip.key"
                  type="button"
                  class="min-h-6 cursor-pointer rounded-[3px] border-0 px-1.5 py-0.5 text-[11px]"
                  :class="
                    statusFilter === chip.key
                      ? 'bg-ink text-white'
                      : 'bg-border-row-light text-ink-3 hover:bg-border'
                  "
                  @click="toggleFilter(chip.key)"
                >
                  {{ chip.label }} {{ chip.count }}
                </button>
              </div>
            </div>

            <div
              ref="rail"
              class="min-h-0 flex-1 overflow-y-auto"
              :class="{ 'pb-2.5 pt-6': editing }"
              @keydown.up.prevent="moveFocus(-1)"
              @keydown.down.prevent="moveFocus(1)"
            >
              <!-- Loading skeleton -->
              <template v-if="!loaded">
                <div
                  v-for="i in 6"
                  :key="'skeleton-' + i"
                  class="border-b border-border-row px-3 py-[9px]"
                >
                  <div
                    class="mb-1.5 h-3.5 w-2/3 animate-pulse rounded bg-border-row"
                  ></div>
                  <div
                    class="h-3 w-1/3 animate-pulse rounded bg-border-row-light"
                  ></div>
                </div>
              </template>

              <template v-else>
                <button
                  v-for="item in filtered"
                  :key="item.id"
                  type="button"
                  class="wp1r-railrow"
                  :class="{
                    'wp1r-railrow-selected': isSelected(item),
                    'wp1r-railrow-collapsed': editing,
                    'wp1r-railrow-collapsed-selected':
                      editing && isSelected(item),
                  }"
                  :aria-current="isSelected(item) ? 'true' : undefined"
                  @click="select(item)"
                >
                  <span class="flex min-w-0 items-center gap-1.5">
                    <span
                      v-if="statusOf(item).attention && !editing"
                      aria-hidden="true"
                      class="h-1.5 w-1.5 shrink-0 rounded-full bg-warn"
                    ></span>
                    <span
                      class="truncate text-[14px]"
                      :class="[
                        isSelected(item) || !editing
                          ? 'text-ink'
                          : 'text-ink-4',
                        isSelected(item) ? 'font-semibold' : 'font-medium',
                      ]"
                      >{{ item.name }}</span
                    >
                  </span>
                  <span
                    v-if="!editing"
                    class="mt-0.5 block truncate text-[12px]"
                    :class="isSelected(item) ? 'text-ink-3' : 'text-ink-4'"
                    >{{ modelLabel(item.model) }} ·
                    {{ statusOf(item).label }}</span
                  >
                </button>

                <div
                  v-if="filtered.length === 0"
                  class="px-3 py-6 text-center text-[13px] text-ink-4"
                >
                  No selections match.
                  <button
                    type="button"
                    class="cursor-pointer border-0 bg-transparent p-0 text-[13px] text-accent"
                    @click="clearFilters"
                  >
                    Clear filters
                  </button>
                </div>
              </template>
            </div>
          </aside>

          <!-- Detail pane -->
          <SelectionDetail
            :key="selectedId || 'none'"
            v-if="selectedId || selectedNotFound"
            :item="selectedItem"
            :all-items="list"
            :editing="editing"
            :not-found="selectedNotFound"
            @refresh="getLists"
            @deleted="onDeleted"
            @dirty="dirtyEdit = $event"
          />
          <section
            v-else
            class="flex items-center justify-center p-8 text-[13px] text-ink-4"
          >
            Choose a selection from the list to view its details.
          </section>
        </div>

        <!-- ============ Mobile ============ -->
        <div class="flex-1 md:hidden">
          <!-- Detail view -->
          <div v-if="selectedId || selectedNotFound">
            <div class="border-b border-border-subtle px-3 pb-2 pt-4">
              <router-link to="/selections/user" class="text-[13px]"
                >← Selections</router-link
              >
            </div>
            <SelectionDetail
              :key="'m-' + (selectedId || 'none')"
              :item="selectedItem"
              :all-items="list"
              :editing="editing"
              :not-found="selectedNotFound"
              @refresh="getLists"
              @deleted="onDeleted"
              @dirty="dirtyEdit = $event"
            />
          </div>

          <!-- List -->
          <div v-else>
            <div
              class="flex items-center justify-between border-b border-border-subtle px-3 pb-[11px] pt-5"
            >
              <h1 class="m-0 text-[15px] font-semibold">Selections</h1>
              <router-link
                to="/selections/new"
                class="wp1r-btn-primary h-7 px-3"
                >New</router-link
              >
            </div>
            <div class="border-b border-border-subtle px-3 py-2.5">
              <label
                class="flex h-[30px] cursor-text items-center gap-1.5 rounded border border-border px-2 focus-within:border-accent focus-within:ring-1 focus-within:ring-accent-border-2"
              >
                <span aria-hidden="true" class="font-mono text-xs text-ink-4"
                  >/</span
                >
                <input
                  v-model="query"
                  type="text"
                  placeholder="Filter…"
                  class="w-full border-0 bg-transparent p-0 text-[13px] outline-none focus:!outline-none"
                  aria-label="Filter selections"
                />
              </label>
              <div class="mt-2 flex flex-wrap gap-1.5">
                <button
                  v-for="pill in statusFilters"
                  :key="pill.key"
                  type="button"
                  class="h-7 shrink-0 cursor-pointer rounded-full border px-3 text-xs"
                  :class="
                    statusFilter === pill.key
                      ? 'border-ink bg-ink text-white'
                      : 'border-border bg-surface text-ink-2'
                  "
                  @click="toggleFilter(pill.key)"
                >
                  {{ pill.label }}
                </button>
              </div>
            </div>

            <div v-if="!loaded" class="px-3 py-6 text-[13px] text-ink-4">
              Loading…
            </div>
            <template v-else>
              <div
                v-for="item in filtered"
                :key="'m-' + item.id"
                class="flex flex-col gap-1.5 border-b border-border-row px-3 py-[11px]"
              >
                <button
                  type="button"
                  class="cursor-pointer border-0 bg-transparent p-0 text-left"
                  @click="select(item)"
                >
                  <span class="block truncate text-sm font-medium text-ink">{{
                    item.name
                  }}</span>
                </button>
                <div class="flex items-center gap-1.5 text-[13px]">
                  <StatusDot :status="statusOf(item)" />
                  <span aria-hidden="true" class="text-ink-5">·</span>
                  <span class="text-[12px] text-ink-3">{{
                    modelLabel(item.model)
                  }}</span>
                </div>
                <div class="flex gap-1.5">
                  <router-link
                    :to="zimPagePath(item.id)"
                    class="wp1r-btn-secondary h-9 flex-1 font-medium !text-accent-hover"
                    >Build ZIM</router-link
                  >
                  <a
                    v-if="tsvReady(item)"
                    :href="item.s_url"
                    class="wp1r-btn-secondary h-9 flex-1"
                    >TSV</a
                  >
                  <span
                    v-else
                    class="flex h-9 flex-1 items-center justify-center text-[13px] text-ink-4"
                    title="The article list becomes downloadable once the selection has finished processing."
                    >TSV not ready</span
                  >
                  <button
                    type="button"
                    class="wp1r-btn-secondary h-9 w-11"
                    aria-label="Details"
                    @click="select(item)"
                  >
                    ⋯
                  </button>
                </div>
              </div>
              <div
                v-if="filtered.length === 0"
                class="px-3 py-6 text-center text-[13px] text-ink-4"
              >
                No selections match.
              </div>
            </template>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import SelectionDetail from './SelectionDetail.vue';
import SelectionsNullState from './SelectionsNullState.vue';
import { loginStore } from '../../store.js';
import StatusDot from './StatusDot.vue';
import {
  deriveStatus,
  hasZim,
  modelLabel,
  selectionIsPending,
  selectionHasError,
  tsvReady,
  zimPagePath,
} from '../../lib/selections.js';

export default {
  name: 'SelectionsPage',
  components: { SelectionDetail, SelectionsNullState, StatusDot },
  data: function () {
    return {
      list: [],
      loaded: false,
      query: '',
      statusFilter: 'all',
      pollId: null,
      loadError: false,
      // True while the detail pane has an open field with unsaved changes.
      dirtyEdit: false,
      // Tracks the md breakpoint (Tailwind's 768px) so the desktop pane's
      // auto-select follows resizes/rotations instead of a load-time bet.
      mdQuery: window.matchMedia('(min-width: 768px)'),
    };
  },
  computed: {
    isLoggedIn: function () {
      return loginStore.isLoggedIn;
    },
    selectedId: function () {
      return this.$route.params.builder_id || null;
    },
    editing: function () {
      return this.$route.path.endsWith('/edit');
    },
    selectedItem: function () {
      if (!this.selectedId) {
        return null;
      }
      return (
        this.list.find((item) => String(item.id) === this.selectedId) || null
      );
    },
    selectedNotFound: function () {
      return this.loaded && !!this.selectedId && !this.selectedItem;
    },
    filtered: function () {
      const query = this.query.trim().toLowerCase();
      return this.list.filter((item) => {
        if (query) {
          const haystack = (
            item.name +
            ' ' +
            modelLabel(item.model)
          ).toLowerCase();
          if (haystack.indexOf(query) === -1) {
            return false;
          }
        }
        switch (this.statusFilter) {
          case 'attention':
            return deriveStatus(item).attention;
          case 'ready':
            return deriveStatus(item).key === 'ready';
          case 'nozim':
            return !hasZim(item);
          case 'scheduled':
            return !!item.active_schedule;
          default:
            return true;
        }
      });
    },
    // One filter vocabulary for both layouts: desktop renders it as count
    // chips, mobile as pills.
    statusFilters: function () {
      return [
        { key: 'all', label: 'All', count: this.list.length },
        {
          key: 'attention',
          label: 'Needs attention',
          count: this.list.filter((item) => deriveStatus(item).attention)
            .length,
        },
        {
          key: 'ready',
          label: 'Up to date',
          count: this.list.filter((item) => deriveStatus(item).key === 'ready')
            .length,
        },
        {
          key: 'nozim',
          label: 'No ZIM',
          count: this.list.filter((item) => !hasZim(item)).length,
        },
        {
          key: 'scheduled',
          label: 'Scheduled',
          count: this.list.filter((item) => !!item.active_schedule).length,
        },
      ];
    },
  },
  created: function () {
    if (this.isLoggedIn) {
      this.getLists();
    }
  },
  mounted: function () {
    document.addEventListener('keydown', this.onKeydown);
    this.mdQuery.addEventListener('change', this.autoSelectFirst);
  },
  beforeUnmount: function () {
    document.removeEventListener('keydown', this.onKeydown);
    this.mdQuery.removeEventListener('change', this.autoSelectFirst);
    this.stopProgressPolling();
  },
  watch: {
    isLoggedIn: function (val) {
      if (val && !this.loaded) {
        this.getLists();
      }
    },
  },
  methods: {
    modelLabel,
    tsvReady,
    zimPagePath,
    statusOf: function (item) {
      return deriveStatus(item);
    },
    isSelected: function (item) {
      return String(item.id) === this.selectedId;
    },
    select: function (item) {
      if (this.isSelected(item) && !this.editing) {
        return;
      }
      if (
        this.dirtyEdit &&
        !window.confirm('Discard unsaved changes to this field?')
      ) {
        return;
      }
      this.dirtyEdit = false;
      this.$router.push(`/selections/user/${item.id}`);
    },
    // Auto-select the first row on desktop so the pane is never empty. Also
    // runs when the viewport crosses the md breakpoint (resize/rotation).
    autoSelectFirst: function () {
      if (
        !this.selectedId &&
        this.list.length > 0 &&
        this.mdQuery.matches &&
        this.$route.path === '/selections/user'
      ) {
        this.$router.replace(`/selections/user/${this.list[0].id}`);
      }
    },
    toggleFilter: function (key) {
      this.statusFilter = this.statusFilter === key ? 'all' : key;
    },
    clearFilters: function () {
      this.query = '';
      this.statusFilter = 'all';
    },
    onKeydown: function (event) {
      if (event.key !== '/' || event.defaultPrevented) {
        return;
      }
      const tag = (event.target.tagName || '').toLowerCase();
      if (['input', 'textarea', 'select'].includes(tag)) {
        return;
      }
      if (this.$refs.search) {
        event.preventDefault();
        this.$refs.search.focus();
      }
    },
    moveFocus: function (delta) {
      const rail = this.$refs.rail;
      if (!rail) {
        return;
      }
      const rows = Array.prototype.slice.call(
        rail.querySelectorAll('button.wp1r-railrow')
      );
      const index = rows.indexOf(document.activeElement);
      let nextIndex = null;
      if (index === -1 && rows.length) {
        nextIndex = 0;
      } else if (rows[index + delta]) {
        nextIndex = index + delta;
      }
      if (nextIndex === null) {
        return;
      }
      rows[nextIndex].focus();
      // Selection follows focus, like the rest of the arrow-key pattern;
      // replace instead of push so arrowing doesn't pile up history.
      const item = this.filtered[nextIndex];
      if (item && !this.isSelected(item) && !this.editing) {
        this.$router.replace(`/selections/user/${item.id}`);
      }
    },
    getLists: async function () {
      this.loadError = false;
      let response = null;
      try {
        response = await fetch(
          `${import.meta.env.VITE_API_URL}/selection/lists`,
          {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
          }
        );
      } catch (e) {
        this.loadError = true;
        this.loaded = true;
        return;
      }
      if (!response.ok) {
        this.loadError = true;
        this.loaded = true;
        return;
      }
      const data = await response.json();
      this.list = data.builders;
      this.loaded = true;

      this.autoSelectFirst();

      // Poll while anything is in flight: materializing selections every
      // 20s, pending/outdated ZIMs every 5 minutes (parity with the old
      // MyLists page).
      let hasPendingSelections = false;
      let hasPendingZim = false;
      this.list.forEach((item) => {
        if (selectionIsPending(item) && !selectionHasError(item)) {
          hasPendingSelections = true;
        }
        if (item.s_status === 'OK' && item.z_status === 'REQUESTED') {
          hasPendingZim = true;
        }
        if (item.z_updated_at && item.z_updated_at < item.s_updated_at) {
          hasPendingZim = true;
        }
      });
      const pollTimeoutMs = hasPendingSelections
        ? 20000
        : hasPendingZim
        ? 300000
        : 0;
      this.stopProgressPolling();
      if (pollTimeoutMs) {
        this.pollId = setInterval(() => this.getLists(), pollTimeoutMs);
      }
    },
    stopProgressPolling: function () {
      if (this.pollId) {
        clearInterval(this.pollId);
        this.pollId = null;
      }
    },
    onDeleted: function () {
      this.$router.replace('/selections/user');
      this.getLists();
    },
  },
};
</script>
