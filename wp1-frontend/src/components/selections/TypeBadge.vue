<template>
  <span class="wp1r-badge">{{ label }}</span>
</template>

<script>
import { modelLabel } from '../../lib/selections.js';

export default {
  name: 'TypeBadge',
  props: {
    model: { type: String, required: true },
  },
  computed: {
    label: function () {
      return modelLabel(this.model);
    },
  },
};
</script>
