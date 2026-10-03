<template>
  <span class="inline-flex min-w-0 items-center gap-1.5">
    <span
      aria-hidden="true"
      class="h-[7px] w-[7px] shrink-0 rounded-full"
      :class="status.dot"
    ></span>
    <span class="truncate">{{ status.label }}</span>
  </span>
</template>

<script>
export default {
  name: 'StatusDot',
  props: {
    status: { type: Object, required: true },
  },
};
</script>
