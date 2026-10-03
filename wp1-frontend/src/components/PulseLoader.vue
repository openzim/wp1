<!-- Local copy of vue-spinner's PulseLoader (MIT,
     https://github.com/greyby/vue-spinner). vue-spinner ships Vue 2
     SFC source, which cannot compile under Vue 3; this component is
     prop- and markup-compatible. -->
<template>
  <div class="v-spinner" v-show="loading">
    <div class="v-pulse v-pulse1" :style="[spinnerStyle, spinnerDelay1]"></div>
    <div class="v-pulse v-pulse2" :style="[spinnerStyle, spinnerDelay2]"></div>
    <div class="v-pulse v-pulse3" :style="[spinnerStyle, spinnerDelay3]"></div>
  </div>
</template>

<script>
export default {
  name: 'PulseLoader',
  props: {
    loading: {
      type: Boolean,
      default: true,
    },
    color: {
      type: String,
      default: '#5dc596',
    },
    size: {
      type: String,
      default: '15px',
    },
    margin: {
      type: String,
      default: '2px',
    },
    radius: {
      type: String,
      default: '100%',
    },
  },
  data() {
    return {
      spinnerStyle: {
        backgroundColor: this.color,
        width: this.size,
        height: this.size,
        margin: this.margin,
        borderRadius: this.radius,
        display: 'inline-block',
        animationName: 'v-pulseStretchDelay',
        animationDuration: '0.75s',
        animationIterationCount: 'infinite',
        animationTimingFunction: 'cubic-bezier(.2,.68,.18,1.08)',
        animationFillMode: 'both',
      },
      spinnerDelay1: { animationDelay: '0.12s' },
      spinnerDelay2: { animationDelay: '0.24s' },
      spinnerDelay3: { animationDelay: '0.36s' },
    };
  },
};
</script>

<style>
@keyframes v-pulseStretchDelay {
  0%,
  80% {
    transform: scale(1);
    opacity: 1;
  }
  45% {
    transform: scale(0.1);
    opacity: 0.7;
  }
}
</style>
