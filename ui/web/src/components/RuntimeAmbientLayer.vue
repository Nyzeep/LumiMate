<script setup>
const props = defineProps({
  ambientMode: {
    type: String,
    default: "quiet"
  },
  chatPhase: {
    type: String,
    default: "idle"
  },
  idle: {
    type: Boolean,
    default: false
  }
});

const stars = [
  { id: 1, x: "10%", y: "18%", size: "2px", delay: "0s", duration: "18s" },
  { id: 2, x: "18%", y: "36%", size: "3px", delay: "2s", duration: "24s" },
  { id: 3, x: "26%", y: "62%", size: "2px", delay: "5s", duration: "20s" },
  { id: 4, x: "42%", y: "22%", size: "2px", delay: "1s", duration: "16s" },
  { id: 5, x: "54%", y: "68%", size: "3px", delay: "4s", duration: "30s" },
  { id: 6, x: "68%", y: "16%", size: "2px", delay: "3s", duration: "21s" },
  { id: 7, x: "74%", y: "38%", size: "4px", delay: "6s", duration: "28s" },
  { id: 8, x: "82%", y: "58%", size: "2px", delay: "1.5s", duration: "26s" },
  { id: 9, x: "90%", y: "28%", size: "3px", delay: "3.5s", duration: "18s" },
  { id: 10, x: "88%", y: "74%", size: "2px", delay: "7s", duration: "24s" }
];
</script>

<template>
  <div
    class="runtime-ambient"
    :class="[`runtime-ambient--${ambientMode}`, `runtime-ambient--${chatPhase}`, { 'is-idle': idle }]"
    aria-hidden="true"
    data-promoted-layer="true"
  >
    <div class="runtime-ambient__mist runtime-ambient__mist--left" data-animated="true"></div>
    <div class="runtime-ambient__mist runtime-ambient__mist--right" data-animated="true"></div>
    <div class="runtime-ambient__mist runtime-ambient__mist--center" data-animated="true"></div>

    <div class="runtime-ambient__stars">
      <span
        v-for="star in stars"
        :key="star.id"
        class="runtime-ambient__star"
        data-animated="true"
        :style="{
          left: star.x,
          top: star.y,
          width: star.size,
          height: star.size,
          animationDelay: star.delay,
          animationDuration: star.duration
        }"
      ></span>
    </div>

    <svg class="runtime-ambient__orbits" viewBox="0 0 1440 900" data-animated="true">
      <g>
        <circle cx="720" cy="460" r="138" />
        <circle cx="720" cy="460" r="214" />
        <circle cx="720" cy="460" r="322" />
        <path d="M392 520C500 408 628 352 720 352c92 0 220 56 328 168" />
      </g>
      <g class="runtime-ambient__constellation">
        <path d="M572 292 720 226 868 292 910 470 720 622 530 470Z" />
        <circle cx="572" cy="292" r="2" />
        <circle cx="720" cy="226" r="2" />
        <circle cx="868" cy="292" r="2" />
        <circle cx="910" cy="470" r="2" />
        <circle cx="720" cy="622" r="2" />
        <circle cx="530" cy="470" r="2" />
      </g>
    </svg>
  </div>
</template>
