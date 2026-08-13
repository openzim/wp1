<template>
  <section v-if="notFound" class="p-[18px]">
    <h2 class="m-0 mb-2 text-[19px] font-semibold tracking-[-0.015em]">
      Not found
    </h2>
    <p class="m-0 text-[14px] text-ink-2">
      This selection either doesn't exist or isn't owned by you.
    </p>
  </section>

  <section v-else-if="!item" class="p-[18px] text-[13px] text-ink-4">
    Loading…
  </section>

  <section v-else class="flex min-w-0 flex-col" :data-selection-id="item.id">
    <!-- ============ Header ============ -->
    <header
      class="flex items-start justify-between gap-3 border-b border-border-subtle px-[18px] pb-4 pt-6"
    >
      <div class="min-w-0">
        <h2
          id="detail-title"
          class="m-0 truncate text-[19px] font-semibold tracking-[-0.015em]"
        >
          {{ item.name }}
        </h2>
        <div
          class="mt-1 flex flex-wrap items-center gap-x-1.5 gap-y-0.5 font-mono text-[12px] text-ink-3"
        >
          <TypeBadge :model="item.model" />
          <span aria-hidden="true" class="text-ink-5">·</span>
          <span class="truncate">{{ item.project }}</span>
          <template v-if="articleCount !== null">
            <span aria-hidden="true" class="text-ink-5">·</span>
            <span class="whitespace-nowrap"
              >{{ articleCount.toLocaleString() }} articles</span
            >
          </template>
        </div>
      </div>
      <div class="flex shrink-0 items-center gap-1.5">
        <span
          v-if="editing && saveState"
          id="save-indicator"
          class="mr-1 text-[12px]"
          :class="saveState === 'error' ? 'text-danger' : 'text-ink-4'"
        >
          {{ saveIndicatorText }}
        </span>
        <router-link
          id="create-zim-button"
          :to="zimPagePath"
          class="wp1r-btn-primary h-7 px-2.5"
          >Create ZIM</router-link
        >
        <router-link
          v-if="!editing"
          id="edit-button"
          :to="editTarget"
          class="wp1r-btn-secondary h-7 px-2.5"
          >Edit</router-link
        >
        <div
          v-if="!editing"
          ref="menuWrap"
          class="relative"
          @keydown.esc.stop="closeMenu(true)"
          @focusout="onMenuFocusOut"
        >
          <button
            id="overflow-button"
            ref="overflowButton"
            type="button"
            class="wp1r-btn-secondary h-7 w-7"
            aria-label="More actions"
            aria-haspopup="true"
            :aria-expanded="menuOpen ? 'true' : 'false'"
            @click="toggleMenu"
          >
            ⋯
          </button>
          <div
            v-if="menuOpen"
            ref="menu"
            class="absolute right-0 top-8 z-20 w-44 overflow-hidden rounded border border-border bg-surface py-1 shadow-card"
            role="menu"
            @keydown.down.prevent="moveMenuFocus(1)"
            @keydown.up.prevent="moveMenuFocus(-1)"
          >
            <a
              v-if="tsvUrl"
              :href="tsvUrl"
              role="menuitem"
              class="wp1r-menuitem"
              @click="closeMenu()"
              >Download TSV</a
            >
            <a
              v-if="zimReady"
              href="#"
              role="menuitem"
              class="wp1r-menuitem"
              @click.prevent="
                closeMenu();
                downloadZim();
              "
              >Download ZIM</a
            >
            <button
              id="delete-menuitem"
              type="button"
              role="menuitem"
              class="wp1r-menuitem w-full border-0 bg-transparent text-left !text-danger"
              @click="
                closeMenu();
                showDeleteDialog = true;
              "
            >
              Delete…
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- ============ Stat strip ============ -->
    <div class="grid grid-cols-2 border-b border-border-subtle sm:grid-cols-3">
      <div class="wp1r-stat border-r border-border-row">
        <div class="wp1r-microlabel">Selection</div>
        <StatusDot :status="selectionStatusInfo" class="text-sm" />
        <div class="truncate font-mono text-[12px] text-ink-3">
          {{ isoDateTime(item.s_updated_at || item.updated_at) }}
        </div>
      </div>
      <div class="wp1r-stat sm:border-r sm:border-border-row">
        <div class="wp1r-microlabel">ZIM</div>
        <StatusDot :status="zimStatusInfo" class="text-sm" />
        <div class="truncate font-mono text-[12px] text-ink-3">
          {{ item.z_updated_at ? isoDateTime(item.z_updated_at) : '—' }}
        </div>
      </div>
      <div
        class="wp1r-stat col-span-2 border-t border-border-row sm:col-span-1 sm:border-t-0"
      >
        <div class="wp1r-microlabel">Schedule</div>
        <div class="truncate text-sm">{{ scheduleText || 'None' }}</div>
      </div>
    </div>

    <!-- ============ Selection error banner ============ -->
    <div
      v-if="selectionErrors.length > 0"
      id="selection-errors"
      class="border-b border-border-subtle bg-danger-tint px-[18px] py-3"
    >
      <div class="text-[13px] font-medium text-danger">
        There was an error creating this selection
      </div>
      <div
        v-for="err in selectionErrors"
        :key="err.ext + ':' + err.status"
        class="mt-1.5 text-[13px] leading-[1.5] text-ink-2"
      >
        <div
          v-if="
            err.referenced_builder_errors &&
            err.referenced_builder_errors.length
          "
        >
          <p class="m-0">
            This Combinator could not be built because referenced selections
            need attention:
          </p>
          <ul class="m-0 mt-1 list-disc pl-5">
            <li
              v-for="refErr in err.referenced_builder_errors"
              :key="refErr.builder_id + ':' + (refErr.message || '')"
            >
              <router-link
                v-if="refErr.builder_id"
                :to="'/selections/user/' + refErr.builder_id"
                >{{ refErr.builder_name || refErr.builder_id }}</router-link
              >
              <span v-else>{{
                refErr.builder_name || 'Referenced selection'
              }}</span>
              <span
                >:
                {{ refErr.reason || refErr.message || 'needs attention' }}</span
              >
              <div v-if="refErr.action" class="text-ink-3">
                {{ refErr.action }}
              </div>
            </li>
          </ul>
        </div>
        <ul v-else class="m-0 list-disc pl-5">
          <li v-for="msg in err.error_messages" :key="msg">{{ msg }}</li>
        </ul>
      </div>
      <div class="mt-2 flex items-center gap-2.5">
        <button
          v-if="retryable"
          id="retry-button"
          type="button"
          class="wp1r-btn-secondary h-7 px-2.5"
          :disabled="retryProcessing"
          @click="retry"
        >
          {{ retryProcessing ? 'Retrying…' : 'Retry' }}
        </button>
        <span v-else class="text-[13px] text-ink-3">
          This error can't be retried — update the definition instead.
          <a
            href="https://wp1.readthedocs.io/en/latest/user/selections/"
            target="_blank"
            rel="noopener noreferrer"
            >Documentation</a
          >
        </span>
      </div>
    </div>

    <!-- ============ Staleness banner ============ -->
    <div
      v-else-if="showStaleBanner"
      id="stale-banner"
      class="flex flex-wrap items-center gap-2.5 border-b border-border-subtle bg-warn-tint px-[18px] py-2.5"
    >
      <span class="text-[13px] text-warn-text-strong">{{
        staleBannerText
      }}</span>
      <router-link
        :to="zimPagePath"
        class="wp1r-btn h-6 border-warn-border-2 bg-surface px-2 !text-warn-text-strong"
        >Rebuild ZIM</router-link
      >
    </div>

    <!-- ============ Edit mode: field rows ============ -->
    <div v-if="editing" id="field-rows" class="flex flex-1 flex-col">
      <template v-for="row in fieldRows">
        <!-- Editing state -->
        <div
          v-if="editingField === row.key"
          :key="row.key"
          class="grid gap-3 border-b border-border-row-light bg-accent-tint px-[18px] py-3 sm:grid-cols-[180px_minmax(0,1fr)]"
        >
          <div class="pt-[7px] text-[13px] font-medium text-ink-2">
            {{ row.label }}
          </div>
          <div class="flex min-w-0 flex-col gap-2">
            <textarea
              v-if="row.control === 'textarea'"
              :id="'edit-' + row.key"
              ref="editControl"
              v-model="draft"
              rows="8"
              class="wp1r-input w-full !border-accent-border-2 py-2 font-mono text-[13px] leading-[1.6]"
              style="resize: vertical"
              @keydown.esc="cancelField"
            ></textarea>
            <input
              v-else-if="row.control === 'text'"
              :id="'edit-' + row.key"
              ref="editControl"
              v-model="draft"
              type="text"
              class="wp1r-input h-8 w-full !border-accent-border-2"
              :class="{ 'font-mono text-[13px]': row.mono }"
              @keydown.esc="cancelField"
              @keydown.enter.prevent="saveField(row)"
            />
            <div
              v-else-if="row.control === 'projects'"
              class="flex flex-col gap-2"
            >
              <ProjectAutocomplete @select="addDraftProject" />
              <div v-if="draftList.length" class="flex flex-wrap gap-1.5">
                <span
                  v-for="(project, i) in draftList"
                  :key="row.key + '-' + i"
                  class="inline-flex items-center gap-1.5 rounded-[3px] border border-border-strong bg-surface px-2 py-1 text-[13px]"
                >
                  {{ project }}
                  <button
                    type="button"
                    class="flex h-6 w-6 shrink-0 cursor-pointer items-center justify-center border-0 bg-transparent p-0 leading-none text-ink-4 hover:text-danger"
                    :aria-label="'Remove ' + project"
                    @click="removeDraftProject(i)"
                  >
                    ×
                  </button>
                </span>
              </div>
              <div v-else class="text-[13px] text-ink-4">
                Nothing selected yet.
              </div>
            </div>

            <div v-if="fieldErrors" class="text-[13px] text-danger">
              {{ fieldErrors }}
            </div>
            <div class="flex items-center gap-2">
              <button
                :id="'save-' + row.key"
                type="button"
                class="wp1r-btn-primary h-7 px-2.5"
                :disabled="saveState === 'saving'"
                @click="saveField(row)"
              >
                Save
              </button>
              <button
                type="button"
                class="wp1r-btn-secondary h-7 px-2.5"
                :disabled="saveState === 'saving'"
                @click="cancelField"
              >
                Cancel
              </button>
              <span v-if="row.hint" class="text-xs text-ink-3">{{
                row.hint
              }}</span>
            </div>
          </div>
        </div>

        <!-- Schedule removal confirm strip -->
        <div
          v-else-if="row.key === 'schedule' && confirmingScheduleRemoval"
          :key="row.key"
          class="grid gap-3 border-b border-border-row-light bg-danger-tint px-[18px] py-3 sm:grid-cols-[180px_minmax(0,1fr)]"
        >
          <div class="pt-[3px] text-[13px] font-medium text-ink-2">
            {{ row.label }}
          </div>
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-[13px] text-ink-2"
              >Remove the recurring ZIM schedule for this selection?</span
            >
            <button
              id="confirm-remove-schedule"
              type="button"
              class="wp1r-btn-danger h-7 px-2.5"
              @click="removeSchedule"
            >
              Remove schedule
            </button>
            <button
              id="cancel-remove-schedule"
              type="button"
              class="wp1r-btn-secondary h-7 px-2.5"
              @click="confirmingScheduleRemoval = false"
            >
              Cancel
            </button>
          </div>
        </div>

        <!-- Read state. Non-interactive rows (static, schedule) render as a
             plain div so nothing announces as a button that can't activate;
             the schedule's destructive action is its own explicit button. -->
        <component
          :is="
            row.control === 'link'
              ? 'router-link'
              : row.control === 'static' || row.control === 'schedule'
              ? 'div'
              : 'button'
          "
          v-else
          :key="row.key"
          :id="'row-' + row.key"
          :to="row.control === 'link' ? combinatorEditPath : undefined"
          :type="
            row.control === 'text' ||
            row.control === 'textarea' ||
            row.control === 'projects'
              ? 'button'
              : undefined
          "
          class="wp1r-fieldrow"
          :class="{
            '!cursor-default hover:!bg-transparent':
              row.control === 'static' || row.control === 'schedule',
          }"
          @click="row.control === 'link' ? null : openField(row)"
        >
          <span class="text-[13px] text-ink-3">{{ row.label }}</span>
          <span
            class="min-w-0 truncate text-left text-[14px] text-ink"
            :class="{ 'font-mono text-[13px]': row.mono }"
            >{{ row.display() }}</span
          >
          <button
            v-if="row.control === 'schedule' && scheduleText"
            id="remove-schedule"
            type="button"
            class="wp1r-btn-secondary h-6 justify-self-end px-2 text-xs"
            @click="confirmingScheduleRemoval = true"
          >
            Remove
          </button>
          <span v-else class="text-right text-xs text-ink-4">{{
            row.control === 'link'
              ? 'Open'
              : row.action === undefined
              ? 'Edit'
              : row.action
          }}</span>
        </component>
      </template>

      <!-- Edit-mode footer -->
      <footer
        class="mt-auto flex items-center gap-4 border-t border-border-strong bg-surface-muted px-[18px] py-3"
      >
        <a v-if="tsvUrl" :href="tsvUrl" class="text-[13px]"
          >Article list (TSV)</a
        >
        <a
          v-if="zimReady"
          href="#"
          class="text-[13px]"
          @click.prevent="downloadZim"
          >Latest ZIM</a
        >
        <button
          id="delete-button"
          type="button"
          class="wp1r-btn-danger ml-auto h-7 px-2.5"
          @click="showDeleteDialog = true"
        >
          Delete
        </button>
      </footer>
    </div>

    <!-- ============ View mode: body ============ -->
    <div v-else class="grid flex-1 lg:grid-cols-[minmax(0,1fr)_300px]">
      <div
        class="min-w-0 border-b border-border-row px-[18px] py-4 lg:border-b-0 lg:border-r"
      >
        <div class="wp1r-microlabel mb-1.5">Definition</div>
        <pre
          v-if="builder"
          id="definition"
          class="m-0 max-h-72 overflow-auto whitespace-pre-wrap rounded border border-border-strong bg-surface-muted px-3 py-[11px] font-mono text-xs leading-[1.6] text-ink"
          >{{ definition }}</pre
        >
        <div v-else class="text-[13px] text-ink-4">Loading…</div>
        <p
          v-if="builder"
          class="mb-0 mt-2 text-[13px] leading-[1.5] text-ink-2"
        >
          {{ note }}
        </p>
      </div>
      <div class="bg-surface-muted px-[18px] py-4">
        <div class="wp1r-microlabel mb-1.5">Downloads</div>
        <div class="flex flex-col gap-1 text-[13px]">
          <a v-if="tsvUrl" :href="tsvUrl">Article list (TSV)</a>
          <span v-else class="text-ink-4">Article list not ready yet</span>
          <a
            v-if="zimReady"
            id="download-zim-link"
            href="#"
            @click.prevent="downloadZim"
            >Latest ZIM file</a
          >
          <span v-else class="text-ink-4">No ZIM file yet</span>
        </div>
        <template v-if="usedBy.length > 0">
          <div class="my-3.5 h-px bg-border-strong"></div>
          <div class="wp1r-microlabel mb-1.5">Used by</div>
          <div class="flex flex-col gap-1 text-[13px]">
            <router-link
              v-for="combinator in usedBy"
              :key="combinator.id"
              :to="'/selections/user/' + combinator.id"
              >{{ combinator.name }}</router-link
            >
          </div>
        </template>
      </div>
    </div>

    <DeleteSelectionDialog
      v-if="showDeleteDialog"
      :builder-id="item.id"
      :fallback-name="item.name"
      :has-zim="zimReady"
      :schedule-text="scheduleText"
      @cancel="showDeleteDialog = false"
      @deleted="onDeleted"
    />
  </section>
</template>

<script>
import DeleteSelectionDialog from './DeleteSelectionDialog.vue';
import ProjectAutocomplete from './ProjectAutocomplete.vue';
import StatusDot from './StatusDot.vue';
import TypeBadge from './TypeBadge.vue';
import { isoDateTime } from '../../lib/util.js';
import {
  deriveSelectionStatus,
  deriveStatus,
  deriveZimStatus,
  definitionText,
  tsvReady,
  definitionNote,
  describeSchedule,
  modelFragment,
  zimDownloadUrl,
  zimPagePath,
} from '../../lib/selections.js';

export default {
  name: 'SelectionDetail',
  components: {
    DeleteSelectionDialog,
    ProjectAutocomplete,
    StatusDot,
    TypeBadge,
  },
  props: {
    // Row from /v1/selection/lists for this builder. Null while the list
    // is loading.
    item: { type: Object, default: null },
    // All list rows; used to resolve combinator member names.
    allItems: { type: Array, default: () => [] },
    editing: { type: Boolean, default: false },
    notFound: { type: Boolean, default: false },
  },
  data: function () {
    return {
      builder: null,
      zimStatus: null,
      articleCount: null,
      usedBy: [],
      menuOpen: false,
      editingField: null,
      draft: '',
      draftList: [],
      // Snapshots taken when a field opens, to detect unsaved changes.
      originalDraft: '',
      originalDraftList: [],
      fieldErrors: '',
      // null until the first save attempt: claiming "all changes saved"
      // before anything was touched is a lie.
      saveState: null,
      confirmingScheduleRemoval: false,
      showDeleteDialog: false,
      retryProcessing: false,
      justEditedDefinition: false,
    };
  },
  computed: {
    status: function () {
      return deriveStatus(this.item);
    },
    selectionStatusInfo: function () {
      return deriveSelectionStatus(this.item);
    },
    // Distinct name: `zimStatus` is the /zim/status payload in data.
    zimStatusInfo: function () {
      return deriveZimStatus(this.item);
    },
    fragment: function () {
      return modelFragment(this.builder ? this.builder.model : this.item.model);
    },
    zimPagePath: function () {
      return zimPagePath(this.item.id);
    },
    editTarget: function () {
      if (this.fragment === 'combinator') {
        return `/selections/combinator/${this.item.id}`;
      }
      return `/selections/user/${this.item.id}/edit`;
    },
    combinatorEditPath: function () {
      return `/selections/combinator/${this.item.id}`;
    },
    tsvUrl: function () {
      return tsvReady(this.item) ? this.item.s_url : null;
    },
    zimReady: function () {
      return this.item.z_status === 'FILE_READY' && !this.item.z_is_deleted;
    },
    scheduleText: function () {
      return describeSchedule(
        this.zimStatus ? this.zimStatus.active_schedule : null
      );
    },
    definition: function () {
      return definitionText(
        this.builder.model || this.item.model,
        this.builder.params,
        this.nameForId
      );
    },
    note: function () {
      return definitionNote(
        this.builder.model || this.item.model,
        this.builder.params
      );
    },
    selectionErrors: function () {
      return (this.builder && this.builder.selection_errors) || [];
    },
    retryable: function () {
      return !this.selectionErrors.some((err) => err.status === 'FAILED');
    },
    showStaleBanner: function () {
      return (
        ['stale', 'expired'].includes(this.status.key) ||
        this.justEditedDefinition
      );
    },
    staleBannerText: function () {
      if (this.status.key === 'expired') {
        return 'The ZIM file has expired — downloads are only kept for 2 weeks.';
      }
      if (this.justEditedDefinition) {
        return 'This change makes the current ZIM stale.';
      }
      return 'The selection changed after the last ZIM was built.';
    },
    saveIndicatorText: function () {
      if (this.saveState === 'saving') {
        return 'Saving…';
      }
      if (this.saveState === 'error') {
        return "Couldn't save";
      }
      return 'All changes saved';
    },
    fieldDirty: function () {
      if (!this.editingField) {
        return false;
      }
      return (
        this.draft !== this.originalDraft ||
        JSON.stringify(this.draftList) !==
          JSON.stringify(this.originalDraftList)
      );
    },
    fieldRows: function () {
      if (!this.builder) {
        return [];
      }
      const params = this.builder.params || {};
      const rows = [
        {
          key: 'name',
          label: 'Name',
          control: 'text',
          hint: 'Shown in your list',
          display: () => this.builder.name,
        },
      ];

      switch (this.fragment) {
        case 'simple':
          rows.push({
            key: 'list',
            label: 'Articles',
            control: 'textarea',
            mono: true,
            hint: 'One title per line — # comments and blank lines are ignored',
            display: () => {
              const n = (params.list || []).filter(
                (l) => l.trim() && !l.trim().startsWith('#')
              ).length;
              return `${n} title${n === 1 ? '' : 's'}`;
            },
          });
          break;
        case 'sparql':
          rows.push({
            key: 'query',
            label: 'Query',
            control: 'textarea',
            mono: true,
            hint: 'Must return ?article',
            display: () => (params.query || '').split('\n')[0],
          });
          break;
        case 'petscan':
          rows.push({
            key: 'url',
            label: 'Petscan URL',
            control: 'text',
            mono: true,
            hint: 'A psid or full URL',
            display: () => params.url || '',
          });
          break;
        case 'book':
          rows.push({
            key: 'url',
            label: 'Book page',
            control: 'text',
            mono: true,
            hint: 'A Book: namespace page URL',
            display: () => params.url || '',
          });
          break;
        case 'wikiproject':
          rows.push(
            {
              key: 'wp_include',
              label: 'WikiProjects to include',
              control: 'projects',
              hint: 'At least one is required',
              display: () => (params.include || []).join(', '),
            },
            {
              key: 'wp_exclude',
              label: 'WikiProjects to exclude',
              control: 'projects',
              hint: 'Optional',
              display: () => (params.exclude || []).join(', ') || 'None',
            }
          );
          break;
        case 'combinator':
          rows.push({
            key: 'combinator',
            label: 'Combination',
            control: 'link',
            display: () =>
              definitionText(this.builder.model, params, this.nameForId),
          });
          break;
      }

      // The project is fixed at creation time; show it but offer no editing.
      rows.push({
        key: 'project',
        label: 'Project',
        control: 'static',
        action: '',
        display: () => this.builder.project,
      });

      rows.push({
        key: 'schedule',
        label: 'Schedule',
        control: 'schedule',
        action: this.scheduleText ? 'Remove' : '',
        display: () =>
          this.scheduleText || 'None — set one up when creating a ZIM',
      });

      return rows;
    },
  },
  watch: {
    fieldDirty: function (val) {
      // Lets the parent guard rail clicks against silently discarding an
      // in-progress field edit.
      this.$emit('dirty', val);
    },
    'item.id': function () {
      this.resetAndFetch();
    },
    // Re-fetch derived data when polling updates the row underneath us.
    'item.s_updated_at': function () {
      this.fetchArticleCount();
      this.fetchBuilder();
    },
    'item.z_status': function () {
      this.fetchZimStatus();
    },
  },
  created: function () {
    this.resetAndFetch();
  },
  mounted: function () {
    document.addEventListener('pointerdown', this.onDocumentPointerDown);
  },
  beforeUnmount: function () {
    document.removeEventListener('pointerdown', this.onDocumentPointerDown);
  },
  methods: {
    isoDateTime,
    // ---- Overflow menu ----
    toggleMenu: function () {
      this.menuOpen = !this.menuOpen;
      if (this.menuOpen) {
        this.$nextTick(() => this.moveMenuFocus(1));
      }
    },
    closeMenu: function (focusButton) {
      this.menuOpen = false;
      if (focusButton && this.$refs.overflowButton) {
        this.$refs.overflowButton.focus();
      }
    },
    onDocumentPointerDown: function (event) {
      if (
        this.menuOpen &&
        this.$refs.menuWrap &&
        !this.$refs.menuWrap.contains(event.target)
      ) {
        this.menuOpen = false;
      }
    },
    onMenuFocusOut: function (event) {
      // Tabbing (or programmatic focus) out of the button + menu closes it.
      if (
        this.menuOpen &&
        this.$refs.menuWrap &&
        !this.$refs.menuWrap.contains(event.relatedTarget)
      ) {
        this.menuOpen = false;
      }
    },
    moveMenuFocus: function (delta) {
      const menu = this.$refs.menu;
      if (!menu) {
        return;
      }
      const items = Array.prototype.slice.call(
        menu.querySelectorAll('[role="menuitem"]')
      );
      if (!items.length) {
        return;
      }
      const index = items.indexOf(document.activeElement);
      const next =
        index === -1
          ? items[delta > 0 ? 0 : items.length - 1]
          : items[(index + delta + items.length) % items.length];
      next.focus();
    },
    resetAndFetch: function () {
      this.builder = null;
      this.zimStatus = null;
      this.articleCount = null;
      this.usedBy = [];
      this.menuOpen = false;
      this.editingField = null;
      this.fieldErrors = '';
      this.confirmingScheduleRemoval = false;
      this.saveState = null;
      this.justEditedDefinition = false;
      if (this.item) {
        this.fetchBuilder();
        this.fetchZimStatus();
        this.fetchArticleCount();
        this.fetchUsedBy();
      }
    },
    fetchBuilder: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${this.item.id}`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }
      );
      if (response.ok) {
        this.builder = await response.json();
      }
    },
    fetchZimStatus: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${this.item.id}/zim/status`
      );
      if (response.ok) {
        this.zimStatus = await response.json();
      }
    },
    fetchArticleCount: async function () {
      this.articleCount = null;
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${
          this.item.id
        }/selection/latest/article_count`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }
      );
      if (response.ok) {
        const data = await response.json();
        this.articleCount = data.selection.article_count;
      }
    },
    fetchUsedBy: async function () {
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${
          this.item.id
        }/delete-impact`,
        {
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }
      );
      if (response.ok) {
        const data = await response.json();
        this.usedBy = data.affected_combinators || [];
      }
    },
    nameForId: function (builderId) {
      const found = this.allItems.find(
        (other) => String(other.id) === String(builderId)
      );
      return found ? found.name : String(builderId).substring(0, 8);
    },
    downloadZim: async function () {
      const url = zimDownloadUrl(this.item.id);
      const response = await fetch(url);
      if (response.status === 410) {
        this.$router.push({
          path: this.zimPagePath,
          query: { expired: true },
        });
      } else {
        window.location.href = url;
      }
    },
    // ---- Edit mode ----
    openField: function (row) {
      if (row.control === 'static' || row.control === 'schedule') {
        return;
      }
      this.editingField = row.key;
      this.fieldErrors = '';
      const params = this.builder.params || {};
      switch (row.key) {
        case 'name':
          this.draft = this.builder.name;
          break;
        case 'list':
          this.draft = (params.list || []).join('\n');
          break;
        case 'query':
          this.draft = params.query || '';
          break;
        case 'url':
          this.draft = params.url || '';
          break;
        case 'wp_include':
          this.draftList = [...(params.include || [])];
          break;
        case 'wp_exclude':
          this.draftList = [...(params.exclude || [])];
          break;
      }
      this.originalDraft = this.draft;
      this.originalDraftList = [...this.draftList];
      this.$nextTick(() => {
        const control = this.$refs.editControl;
        const el = Array.isArray(control) ? control[0] : control;
        if (el && el.focus) {
          el.focus();
        }
      });
    },
    cancelField: function () {
      this.editingField = null;
      this.fieldErrors = '';
    },
    addDraftProject: function (project) {
      if (!this.draftList.includes(project)) {
        this.draftList.push(project);
      }
    },
    removeDraftProject: function (index) {
      this.draftList.splice(index, 1);
    },
    saveField: async function (row) {
      const params = { ...(this.builder.params || {}) };
      let name = this.builder.name;
      let project = this.builder.project;
      let definitionChanged = false;

      switch (row.key) {
        case 'name':
          name = this.draft.trim();
          if (!name) {
            this.fieldErrors = 'Please provide a name.';
            return;
          }
          break;
        case 'list':
          if (!this.draft.trim()) {
            this.fieldErrors = 'Please provide at least one article title.';
            return;
          }
          params.list = this.draft.split('\n');
          definitionChanged = true;
          break;
        case 'query':
          if (!this.draft.trim()) {
            this.fieldErrors = 'Please provide a query.';
            return;
          }
          params.query = this.draft;
          definitionChanged = true;
          break;
        case 'url':
          if (!this.draft.trim()) {
            this.fieldErrors = 'Please provide a URL.';
            return;
          }
          params.url = this.draft.trim();
          definitionChanged = true;
          break;
        case 'wp_include':
          if (this.draftList.length === 0) {
            this.fieldErrors = 'Please provide at least one WikiProject.';
            return;
          }
          params.include = [...this.draftList];
          definitionChanged = true;
          break;
        case 'wp_exclude':
          params.exclude = [...this.draftList];
          definitionChanged = true;
          break;
      }

      await this.postBuilder({ name, project, params }, definitionChanged);
    },
    retry: async function () {
      this.retryProcessing = true;
      await this.postBuilder(
        {
          name: this.builder.name,
          project: this.builder.project,
          params: this.builder.params,
        },
        false
      );
      this.retryProcessing = false;
    },
    postBuilder: async function ({ name, project, params }, definitionChanged) {
      this.saveState = 'saving';
      this.fieldErrors = '';
      let response = null;
      try {
        response = await fetch(
          `${import.meta.env.VITE_API_URL}/builders/${this.item.id}`,
          {
            headers: { 'Content-Type': 'application/json' },
            method: 'post',
            credentials: 'include',
            body: JSON.stringify({
              name,
              project,
              model: this.builder.model || this.item.model,
              params,
            }),
          }
        );
      } catch (e) {
        this.saveState = 'error';
        this.fieldErrors = 'Network error — your change was not saved.';
        return;
      }

      if (!response.ok) {
        this.saveState = 'error';
        this.fieldErrors = 'An unknown server error has occurred.';
        return;
      }

      const data = await response.json();
      if (!data.success) {
        this.saveState = 'error';
        const errors = (data.items && data.items.errors) || [];
        const invalid = (data.items && data.items.invalid) || [];
        this.fieldErrors =
          errors.join(', ') +
          (invalid.length ? ` — invalid: ${invalid.join(', ')}` : '');
        return;
      }

      this.saveState = 'saved';
      this.editingField = null;
      if (definitionChanged && this.item.z_updated_at) {
        this.justEditedDefinition = true;
      }
      await this.fetchBuilder();
      this.$emit('refresh');
    },
    removeSchedule: async function () {
      this.confirmingScheduleRemoval = false;
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/builders/${this.item.id}/schedule`,
        {
          method: 'DELETE',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
        }
      );
      if (response.ok) {
        await this.fetchZimStatus();
        this.$emit('refresh');
      }
    },
    onDeleted: function () {
      this.showDeleteDialog = false;
      this.$emit('deleted');
    },
  },
};
</script>
