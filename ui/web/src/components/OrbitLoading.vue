<template>
  <div class="orbit-loader" :class="[`orbit-loader--${variant}`, { 'is-loaded': loaded }]">
    <svg class="orbit-loader__svg" viewBox="0 0 420 420" role="img" :aria-label="label">
      <g class="orbit-loader__rings">
        <circle cx="210" cy="210" r="158" />
        <circle cx="210" cy="210" r="126" />
        <circle cx="210" cy="210" r="92" />
        <circle cx="210" cy="210" r="52" />
      </g>
      <g class="orbit-loader__progress">
        <circle cx="210" cy="210" r="158" :style="progressStyle" />
      </g>
      <g class="orbit-loader__geometry">
        <path d="M210 78 326 278H94Z" />
        <path d="M70 210H350" />
        <path d="M210 54V366" />
        <path d="M112 280C166 248 254 248 308 280" />
      </g>
      <g class="orbit-loader__constellation">
        <path d="M112 280 156 128 290 118 326 278 210 340Z" />
        <circle cx="112" cy="280" r="2" />
        <circle cx="156" cy="128" r="2" />
        <circle cx="290" cy="118" r="2" />
        <circle cx="326" cy="278" r="2" />
        <circle cx="210" cy="340" r="2" />
      </g>
      <g class="orbit-loader__core">
        <circle cx="210" cy="210" r="46" class="orbit-loader__haze" />
        <path d="M210 182 235 226H185Z" class="orbit-loader__triangle" />
        <circle cx="210" cy="210" r="9" class="orbit-loader__star" />
      </g>
    </svg>
    <div class="orbit-loader__readout">
      <span>{{ percent }}%</span>
      <small>{{ caption }}</small>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  progress: {
    type: Number,
    default: 0
  },
  caption: {
    type: String,
    default: "Waiting"
  },
  label: {
    type: String,
    default: "Lumi orbital core"
  },
  loaded: {
    type: Boolean,
    default: false
  },
  variant: {
    type: String,
    default: "core"
  }
});

const radius = 158;
const circumference = 2 * Math.PI * radius;
const ratio = computed(() => Math.min(1, Math.max(0, props.progress)));
const percent = computed(() => Math.round(ratio.value * 100));
const progressStyle = computed(() => ({
  strokeDasharray: `${circumference}`,
  strokeDashoffset: `${circumference * (1 - ratio.value)}`
}));
</script>
