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
        v-else-if="serverError"
        class="mx-auto w-full max-w-[760px] p-[22px]"
      >
        <h1 class="m-0 mb-2 text-xl font-semibold">500 Server error</h1>
        <p class="m-0 text-[13.5px] text-ink-2">
          Something went wrong and we couldn't retrieve that selection. You
          might try again later.
        </p>
      </div>

      <div v-else class="flex flex-1 flex-col">
        <!-- ============ Header ============ -->
        <div
          class="flex flex-wrap items-center gap-2.5 border-b border-border-subtle px-[18px] pb-3.5 pt-6"
        >
          <h1 class="m-0 mr-1 text-[17px] font-semibold tracking-[-0.015em]">
            {{
              isEditing
                ? 'Edit combinator selection'
                : 'New combinator selection'
            }}
          </h1>
          <input
            id="combinator-name"
            v-model="name"
            type="text"
            class="wp1r-input h-[30px] w-[220px]"
            placeholder="Selection name"
            aria-label="Selection name"
          />
          <select
            id="combinator-project"
            v-model="project"
            class="wp1r-select h-[30px]"
            aria-label="Project"
          >
            <option v-for="site in projectOptions" :key="site">
              {{ site }}
            </option>
          </select>
          <button
            id="saveListButton"
            type="button"
            class="wp1r-btn-primary ml-auto h-[30px] px-3.5"
            :disabled="!canSave || processing"
            @click="onSave"
          >
            {{ processing ? 'Saving…' : 'Save' }}
          </button>
        </div>

        <div class="grid min-h-[460px] flex-1 md:grid-cols-[1fr_1.15fr]">
          <!-- ============ Library ============ -->
          <div class="order-2 flex min-h-0 flex-col md:order-1">
            <div
              class="flex flex-col gap-2 border-b border-border-subtle px-3.5 py-[11px]"
            >
              <div class="flex items-baseline justify-between">
                <span class="wp1r-microlabel">Your selections</span>
                <span class="font-mono text-[11px] text-ink-4"
                  >{{ library.length }} total</span
                >
              </div>
              <label
                class="flex h-7 cursor-text items-center gap-1.5 rounded border border-border px-2 focus-within:border-accent focus-within:ring-1 focus-within:ring-accent-border-2"
              >
                <span aria-hidden="true" class="font-mono text-xs text-ink-4"
                  >/</span
                >
                <input
                  v-model="libQuery"
                  type="text"
                  placeholder="Filter…"
                  class="w-full border-0 bg-transparent p-0 text-[13px] outline-none focus:!outline-none"
                  aria-label="Filter your selections"
                />
              </label>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="pill in typePills"
                  :key="pill.key"
                  type="button"
                  class="h-7 cursor-pointer rounded-full border border-solid px-2.5 text-[11.5px]"
                  :class="
                    libType === pill.key
                      ? 'border-ink bg-ink text-white'
                      : 'border-border bg-surface text-ink-2 hover:bg-surface-muted'
                  "
                  @click="libType = pill.key"
                >
                  {{ pill.label }}
                </button>
              </div>
            </div>

            <div class="min-h-0 flex-1 overflow-y-auto">
              <div
                v-if="!buildersFetchFinished"
                class="px-3.5 py-4 text-[12.5px] text-ink-4"
              >
                Loading selections…
              </div>
              <div
                v-else-if="buildersLoadError"
                class="px-3.5 py-4 text-[12.5px] text-danger"
              >
                {{ buildersLoadError }}
              </div>
              <template v-else>
                <div
                  v-for="item in filteredLibrary"
                  :key="item.id"
                  class="flex items-center gap-2 border-b border-border-row-light px-3.5 py-[7px] hover:bg-surface-muted"
                >
                  <span class="min-w-0 flex-1 truncate text-[13px]">{{
                    item.name
                  }}</span>
                  <span
                    class="shrink-0 font-mono text-[10.5px] uppercase text-ink-4"
                    >{{ modelLabel(item.model) }}</span
                  >
                  <button
                    type="button"
                    class="wp1r-btn h-7 shrink-0 border-ok-border px-1.5 text-[11.5px] font-medium text-ok hover:bg-ok-tint"
                    @click="addTo('include', item.id)"
                  >
                    include
                  </button>
                  <button
                    type="button"
                    class="wp1r-btn h-7 shrink-0 border-danger-border px-1.5 text-[11.5px] font-medium text-danger hover:bg-danger-tint"
                    @click="addTo('exclude', item.id)"
                  >
                    exclude
                  </button>
                </div>
                <div
                  v-if="filteredLibrary.length === 0"
                  class="px-3.5 py-4 text-[12.5px] text-ink-4"
                >
                  <span v-if="library.length === 0"
                    >No eligible selections for {{ project }}. Combinators
                    combine selections you've already created.</span
                  >
                  <span v-else>No selections match.</span>
                </div>
              </template>
            </div>
          </div>

          <!-- ============ Recipe ============ -->
          <div
            class="order-1 flex flex-col gap-3.5 border-b border-border-row bg-surface-muted p-3.5 md:order-2 md:border-b-0 md:border-l"
          >
            <div
              v-for="group in ['include', 'exclude']"
              :key="group"
              :id="group + '-items'"
              class="flex flex-col gap-2"
            >
              <div class="flex items-center gap-2">
                <span
                  aria-hidden="true"
                  class="h-[7px] w-[7px] rounded-full"
                  :class="group === 'include' ? 'bg-ok' : 'bg-danger'"
                ></span>
                <span class="text-[13.5px] font-semibold">{{
                  group === 'include' ? 'Include' : 'Exclude'
                }}</span>
                <button
                  :id="group + '-operation'"
                  type="button"
                  class="ml-auto h-6 cursor-pointer rounded border border-solid px-2 font-mono text-[11.5px]"
                  :class="
                    operations[group] === 'intersection'
                      ? 'border-ink bg-ink text-white'
                      : 'border-border bg-surface text-ink-2 hover:bg-surface-muted'
                  "
                  :aria-label="
                    'Combine ' +
                    group +
                    'd selections using ' +
                    (operations[group] === 'intersection'
                      ? 'AND (only shared articles)'
                      : 'OR (any article)')
                  "
                  @click="toggleOperation(group)"
                >
                  {{
                    operations[group] === 'intersection'
                      ? 'AND · only shared'
                      : 'OR · any article'
                  }}
                </button>
              </div>

              <div
                v-if="groups[group].length === 0"
                class="rounded border border-dashed border-border bg-surface px-4 py-4 text-center text-[12.5px] text-ink-4"
              >
                {{
                  group === 'include'
                    ? 'Add selections from your library'
                    : 'Nothing excluded'
                }}
              </div>

              <div
                v-for="builderId in groups[group]"
                :key="group + '-' + builderId"
                class="flex items-center gap-2 rounded border border-l-2 border-solid border-border-strong bg-surface py-2 pl-2.5 pr-2"
                :class="group === 'include' ? 'border-l-ok' : 'border-l-danger'"
              >
                <span class="min-w-0 flex-1 truncate text-[13px] font-medium">{{
                  nameForId(builderId)
                }}</span>
                <button
                  type="button"
                  class="wp1r-btn-secondary h-7 px-1.5 text-[11.5px]"
                  @click="moveBetween(group, builderId)"
                >
                  Move to {{ group === 'include' ? 'exclude' : 'include' }}
                </button>
                <button
                  type="button"
                  class="h-6 w-6 cursor-pointer border-0 bg-transparent p-0 text-sm leading-none text-ink-4 hover:text-danger"
                  :aria-label="'Remove ' + nameForId(builderId)"
                  @click="removeFrom(group, builderId)"
                >
                  ×
                </button>
              </div>
            </div>

            <!-- Footer -->
            <div
              class="mt-auto -mx-3.5 -mb-3.5 border-t border-border-strong bg-surface px-4 py-3"
            >
              <div class="wp1r-microlabel mb-1">Result</div>
              <p class="m-0 text-[13px] leading-[1.5]">{{ sentence }}</p>
              <div
                id="expression-preview"
                class="mt-1 font-mono text-xs leading-[1.6] text-ink-2"
              >
                {{ expression }}
              </div>
              <div
                v-if="footerProblem"
                class="mt-1.5 text-[12.5px] text-warn-text"
              >
                {{ footerProblem }}
              </div>
              <div v-if="errors" class="mt-1.5 text-[12.5px] text-danger">
                {{ errors }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import SelectionsNullState from './SelectionsNullState.vue';
import { loginStore } from '../../store.js';
import {
  COMBINATOR_MODEL,
  combinatorExpression,
  combinatorSentence,
  modelLabel,
} from '../../lib/selections.js';

export default {
  name: 'CombinatorPage',
  components: { SelectionsNullState },
  data: function () {
    return {
      allBuilders: [],
      buildersFetchFinished: false,
      buildersLoadError: '',
      sites: [],
      name: '',
      project: 'en.wikipedia.org',
      groups: {
        include: [],
        exclude: [],
      },
      operations: {
        include: 'union',
        exclude: 'union',
      },
      libQuery: '',
      libType: 'all',
      processing: false,
      errors: '',
      notFound: false,
      serverError: false,
    };
  },
  computed: {
    isLoggedIn: function () {
      return loginStore.isLoggedIn;
    },
    builderId: function () {
      return this.$route.params.builder_id
        ? String(this.$route.params.builder_id)
        : null;
    },
    isEditing: function () {
      return !!this.builderId;
    },
    projectOptions: function () {
      return this.sites.length ? this.sites : ['en.wikipedia.org'];
    },
    // Selections eligible for this combinator: same project, not a
    // combinator, not this builder itself.
    library: function () {
      return this.allBuilders.filter(
        (item) =>
          item.model !== COMBINATOR_MODEL &&
          item.project === this.project &&
          item.id !== this.builderId
      );
    },
    typePills: function () {
      const present = new Set(
        this.library.map((item) => modelLabel(item.model))
      );
      return [{ key: 'all', label: 'All types' }].concat(
        Array.from(present)
          .sort()
          .map((label) => ({ key: label, label }))
      );
    },
    filteredLibrary: function () {
      const query = this.libQuery.trim().toLowerCase();
      const selected = new Set([
        ...this.groups.include,
        ...this.groups.exclude,
      ]);
      return this.library.filter((item) => {
        if (selected.has(item.id)) {
          return false;
        }
        if (this.libType !== 'all' && modelLabel(item.model) !== this.libType) {
          return false;
        }
        if (query && item.name.toLowerCase().indexOf(query) === -1) {
          return false;
        }
        return true;
      });
    },
    params: function () {
      return {
        include: {
          builders: [...this.groups.include],
          operation: this.operations.include,
        },
        exclude: {
          builders: [...this.groups.exclude],
          operation: this.operations.exclude,
        },
      };
    },
    sentence: function () {
      return combinatorSentence(this.params);
    },
    expression: function () {
      return combinatorExpression(this.params, this.nameForId);
    },
    footerProblem: function () {
      if (!this.name.trim() && this.groups.include.length === 0) {
        return 'Name the selection and add at least one selection to include before saving.';
      }
      if (!this.name.trim()) {
        return 'Name the selection before saving.';
      }
      if (this.groups.include.length === 0) {
        return 'Add at least one selection to include before saving.';
      }
      return '';
    },
    canSave: function () {
      return !this.footerProblem;
    },
  },
  watch: {
    isLoggedIn: function (val) {
      if (val) {
        this.initialize();
      }
    },
  },
  created: function () {
    if (this.isLoggedIn) {
      this.initialize();
    }
  },
  methods: {
    modelLabel,
    initialize: function () {
      this.fetchSites();
      this.fetchBuilders();
      if (this.isEditing) {
        this.fetchBuilder();
      }
    },
    fetchSites: async function () {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/sites/`);
      if (response.ok) {
        const data = await response.json();
        this.sites = data.sites;
      }
    },
    fetchBuilders: async function () {
      this.buildersLoadError = '';
      this.buildersFetchFinished = false;
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/selection/lists`,
          {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
          }
        );
        if (!response.ok) {
          this.buildersLoadError =
            'Unable to load your selections. Please try again later.';
          return;
        }
        const data = await response.json();
        this.allBuilders = data.builders
          .map((builder) => ({ ...builder, id: String(builder.id) }))
          .sort((a, b) => a.name.localeCompare(b.name));
      } catch (e) {
        this.buildersLoadError =
          'Unable to load your selections. Please try again later.';
      } finally {
        this.buildersFetchFinished = true;
      }
    },
    fetchBuilder: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${this.builderId}`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }
      );
      if (response.status === 404 || response.status === 401) {
        this.notFound = true;
        return;
      }
      if (!response.ok) {
        this.serverError = true;
        return;
      }
      const builder = await response.json();
      this.name = builder.name;
      this.project = builder.project;
      const include = builder.params.include || {};
      const exclude = builder.params.exclude || {};
      this.groups.include = (include.builders || []).map(String);
      this.groups.exclude = (exclude.builders || []).map(String);
      this.operations.include = include.operation || 'union';
      this.operations.exclude = exclude.operation || 'union';
    },
    nameForId: function (builderId) {
      const found = this.allBuilders.find(
        (item) => item.id === String(builderId)
      );
      return found ? found.name : String(builderId).substring(0, 8);
    },
    addTo: function (group, builderId) {
      const other = group === 'include' ? 'exclude' : 'include';
      this.groups[other] = this.groups[other].filter((id) => id !== builderId);
      if (!this.groups[group].includes(builderId)) {
        this.groups[group].push(builderId);
      }
    },
    removeFrom: function (group, builderId) {
      this.groups[group] = this.groups[group].filter((id) => id !== builderId);
    },
    moveBetween: function (fromGroup, builderId) {
      const toGroup = fromGroup === 'include' ? 'exclude' : 'include';
      this.removeFrom(fromGroup, builderId);
      this.addTo(toGroup, builderId);
    },
    toggleOperation: function (group) {
      this.operations[group] =
        this.operations[group] === 'intersection' ? 'union' : 'intersection';
    },
    onSave: async function () {
      if (!this.canSave) {
        return;
      }

      // Members must belong to the selected project (they normally do,
      // because the library is filtered, but the project can change after
      // members were added).
      const mismatched = [...this.groups.include, ...this.groups.exclude]
        .map((id) => this.allBuilders.find((item) => item.id === id))
        .filter((item) => item && item.project !== this.project);
      if (mismatched.length) {
        this.errors =
          `All combined selections must use ${this.project}. ` +
          `Remove or replace: ` +
          mismatched.map((item) => item.name).join(', ');
        return;
      }

      this.errors = '';
      this.processing = true;
      const postUrl = this.isEditing
        ? `${import.meta.env.VITE_API_URL}/builders/${this.builderId}`
        : `${import.meta.env.VITE_API_URL}/builders/`;
      let response = null;
      try {
        response = await fetch(postUrl, {
          headers: { 'Content-Type': 'application/json' },
          method: 'post',
          credentials: 'include',
          body: JSON.stringify({
            name: this.name,
            project: this.project,
            model: COMBINATOR_MODEL,
            params: this.params,
          }),
        });
      } catch (e) {
        this.processing = false;
        this.errors = 'A network error has occurred.';
        return;
      }
      this.processing = false;

      if (!response.ok) {
        this.errors = 'An unknown server error has occurred.';
        return;
      }

      const data = await response.json();
      if (data.success) {
        this.$router.push(`/selections/user/${data.id || this.builderId}`);
        return;
      }
      this.errors = data.items.errors.join(', ');
    },
  },
};
</script>
