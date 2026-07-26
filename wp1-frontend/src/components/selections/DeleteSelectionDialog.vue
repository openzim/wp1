<template>
  <div
    id="delete-impact-dialog"
    class="wp1r fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/45 px-4 py-12"
  >
    <div
      class="w-full max-w-[560px] rounded-md border border-border bg-surface shadow-card"
      role="dialog"
      aria-modal="true"
      aria-label="Confirm delete"
    >
      <div class="border-b border-border-subtle px-[18px] py-3.5">
        <h2 class="m-0 text-[15px] font-semibold">Delete selection</h2>
      </div>

      <div v-if="loading" class="px-[18px] py-6 text-[13px] text-ink-3">
        Checking what this affects…
      </div>
      <div v-else-if="loadError" class="px-[18px] py-6 text-[13px] text-danger">
        {{ loadError }}
      </div>
      <div v-else class="flex flex-col gap-3.5 px-[18px] py-4">
        <p class="m-0 text-[13.5px] leading-[1.5] text-ink-2">
          Deleting
          <strong class="font-semibold text-ink">{{ builderName }}</strong>
          permanently removes this selection and all of its downloadable article
          lists.
        </p>

        <div
          v-if="affectedCombinators.length > 0"
          id="affected-combinators"
          class="flex flex-col gap-2.5"
        >
          <div
            class="rounded border border-warn-border bg-warn-tint px-3 py-2.5 text-[13px] leading-[1.5] text-warn-text-strong"
          >
            This selection is used by the Combinator selections below. For each
            one, choose whether to remove this selection from it or delete the
            Combinator completely.
          </div>

          <div
            v-for="item in affectedCombinators"
            :key="'affected-combinator-' + item.id"
            class="delete-combinator-choice rounded border border-border-strong px-3 py-2.5"
          >
            <div class="mb-1.5 text-[13px] font-medium">
              <span
                v-if="!item.will_be_auto_deleted"
                :id="'decision-required-' + item.id"
                class="text-danger"
                aria-hidden="true"
                >*</span
              >
              {{ item.name }}
              <span class="font-mono text-[11.5px] text-ink-3">{{
                item.project
              }}</span>
            </div>
            <label
              class="mb-1 flex cursor-pointer items-center gap-2 text-[13px] text-ink-2"
              :for="'remove-builder-' + item.id"
            >
              <input
                :id="'remove-builder-' + item.id"
                type="radio"
                :name="'delete-action-' + item.id"
                :disabled="item.will_be_auto_deleted"
                :checked="actionFor(item) === 'remove'"
                @change="setAction(item.id, 'remove')"
              />
              Remove {{ builderName }} from this Combinator
            </label>
            <label
              class="flex cursor-pointer items-center gap-2 text-[13px] text-danger"
              :for="'delete-combinator-' + item.id"
            >
              <input
                :id="'delete-combinator-' + item.id"
                type="radio"
                :name="'delete-action-' + item.id"
                :checked="actionFor(item) === 'delete'"
                @change="setAction(item.id, 'delete')"
              />
              Delete this Combinator completely
            </label>
          </div>
        </div>

        <div v-if="requiresConfirmation">
          <label
            for="delete-confirm-name"
            class="mb-1 block text-[13px] text-ink-2"
          >
            Type
            <strong class="font-semibold text-ink">{{ builderName }}</strong>
            to confirm deletion.
          </label>
          <input
            id="delete-confirm-name"
            v-model="confirmName"
            type="text"
            class="wp1r-input h-8 w-full"
            autocomplete="off"
          />
        </div>

        <div v-if="errors" class="text-[13px] text-danger">{{ errors }}</div>
      </div>

      <div
        class="flex justify-end gap-2 border-t border-border-subtle px-[18px] py-3"
      >
        <button
          id="cancelDeleteButton"
          type="button"
          class="wp1r-btn-secondary h-8 px-3"
          :disabled="processing"
          @click="$emit('cancel')"
        >
          Cancel
        </button>
        <button
          id="confirmDeleteButton"
          type="button"
          class="wp1r-btn-danger h-8 px-3"
          :disabled="!canConfirm"
          @click="confirmDelete"
        >
          Delete selection
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DeleteSelectionDialog',
  props: {
    builderId: { type: String, required: true },
    fallbackName: { type: String, default: '' },
  },
  data: function () {
    return {
      loading: true,
      loadError: '',
      impact: null,
      actions: {},
      confirmName: '',
      errors: '',
      processing: false,
    };
  },
  computed: {
    affectedCombinators: function () {
      if (!this.impact || !this.impact.affected_combinators) {
        return [];
      }
      return this.impact.affected_combinators;
    },
    builderName: function () {
      if (this.impact && this.impact.builder) {
        return this.impact.builder.name;
      }
      return this.fallbackName;
    },
    requiresConfirmation: function () {
      return this.affectedCombinators.length > 0;
    },
    allActionsSelected: function () {
      return this.affectedCombinators.every(
        (item) => item.will_be_auto_deleted || this.actions[item.id]
      );
    },
    canConfirm: function () {
      if (this.processing || this.loading || this.loadError) {
        return false;
      }
      if (!this.requiresConfirmation) {
        return true;
      }
      return this.confirmName === this.builderName && this.allActionsSelected;
    },
  },
  created: function () {
    this.fetchImpact();
  },
  methods: {
    fetchImpact: async function () {
      this.loading = true;
      this.loadError = '';
      let response = null;
      try {
        response = await fetch(
          `${import.meta.env.VITE_API_URL}/builders/${
            this.builderId
          }/delete-impact`,
          {
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
          }
        );
      } catch (e) {
        this.loadError = 'Could not check delete impact. Please try again.';
        this.loading = false;
        return;
      }
      if (!response.ok) {
        this.loadError =
          response.status === 404 || response.status === 403
            ? "Could not delete this selection. Check that it still exists and you're logged in as its owner."
            : 'Could not check delete impact. Please try again.';
        this.loading = false;
        return;
      }
      try {
        this.impact = await response.json();
      } catch (e) {
        this.loadError = 'Could not check delete impact. Please try again.';
      }
      this.loading = false;
    },
    actionFor: function (item) {
      if (item.will_be_auto_deleted) {
        return 'delete';
      }
      return this.actions[item.id] || '';
    },
    setAction: function (id, action) {
      this.actions = { ...this.actions, [id]: action };
    },
    confirmDelete: async function () {
      if (!this.canConfirm) {
        return;
      }
      this.errors = '';
      this.processing = true;

      const body = {
        delete_combinator_ids: this.affectedCombinators
          .filter(
            (item) =>
              !item.will_be_auto_deleted && this.actions[item.id] === 'delete'
          )
          .map((item) => item.id),
      };
      if (this.requiresConfirmation) {
        body.confirm_builder_name = this.confirmName;
      }

      let response = null;
      try {
        response = await fetch(
          `${import.meta.env.VITE_API_URL}/builders/${this.builderId}/delete`,
          {
            headers: { 'Content-Type': 'application/json' },
            method: 'post',
            credentials: 'include',
            body: JSON.stringify(body),
          }
        );
      } catch (e) {
        this.errors = 'Could not delete this selection. Please try again.';
        this.processing = false;
        return;
      }
      this.processing = false;

      if (response.status === 200) {
        this.$emit('deleted');
        return;
      }
      if ([401, 403, 404].includes(response.status)) {
        this.errors =
          "Could not delete this selection. Check that it still exists and you're logged in as its owner.";
        return;
      }
      try {
        const data = await response.json();
        this.errors = (data.error_messages || []).join(', ');
      } catch (e) {
        this.errors = 'Could not delete this selection. Please try again.';
      }
    },
  },
};
</script>
