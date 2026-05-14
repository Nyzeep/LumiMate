<script setup>
import { computed } from "vue";

const props = defineProps({
  type: {
    type: String,
    default: "home"
  }
});

const GLYPHS = {
  core: {
    circles: [
      { cx: 32, cy: 32, r: 22, class: "rail-glyph__orbit rail-glyph__orbit--slow" },
      { cx: 32, cy: 32, r: 12, class: "rail-glyph__orbit" }
    ],
    polygons: [{ points: "32 14 49 45 15 45", class: "rail-glyph__geometry rail-glyph__accent" }],
    lines: [
      { x1: 32, y1: 14, x2: 32, y2: 45, class: "rail-glyph__line" },
      { x1: 15, y1: 45, x2: 49, y2: 45, class: "rail-glyph__line" }
    ],
    dots: [
      { cx: 32, cy: 32, r: 2.2, class: "rail-glyph__node rail-glyph__node--core" },
      { cx: 49, cy: 45, r: 1.5, class: "rail-glyph__node" }
    ]
  },
  runtime: {
    polygons: [
      { points: "32 12 49 22 49 42 32 52 15 42 15 22", class: "rail-glyph__geometry" },
      { points: "32 21 41 27 41 37 32 43 23 37 23 27", class: "rail-glyph__geometry rail-glyph__accent" }
    ],
    lines: [
      { x1: 32, y1: 21, x2: 32, y2: 12, class: "rail-glyph__line" },
      { x1: 41, y1: 37, x2: 49, y2: 42, class: "rail-glyph__line" },
      { x1: 23, y1: 37, x2: 15, y2: 42, class: "rail-glyph__line" }
    ],
    dots: [
      { cx: 32, cy: 12, r: 1.6, class: "rail-glyph__node" },
      { cx: 49, cy: 42, r: 1.6, class: "rail-glyph__node" },
      { cx: 15, cy: 42, r: 1.6, class: "rail-glyph__node" },
      { cx: 32, cy: 32, r: 2, class: "rail-glyph__node rail-glyph__node--core" }
    ]
  },
  inner: {
    circles: [
      { cx: 32, cy: 32, r: 21, class: "rail-glyph__orbit rail-glyph__orbit--slow" },
      { cx: 32, cy: 32, r: 8, class: "rail-glyph__orbit" }
    ],
    paths: [
      { d: "M32 10v9M32 45v9M10 32h9M45 32h9", class: "rail-glyph__line" },
      { d: "M24 24l16 16M40 24 24 40", class: "rail-glyph__line rail-glyph__accent" }
    ],
    dots: [{ cx: 32, cy: 32, r: 2.2, class: "rail-glyph__node rail-glyph__node--core" }]
  },
  home: {
    circles: [{ cx: 32, cy: 34, r: 20, class: "rail-glyph__orbit rail-glyph__orbit--slow" }],
    polygons: [{ points: "32 15 49 45 15 45", class: "rail-glyph__geometry rail-glyph__accent" }],
    paths: [{ d: "M22 45c4-8 16-8 20 0", class: "rail-glyph__line" }],
    dots: [{ cx: 32, cy: 29, r: 2.2, class: "rail-glyph__node rail-glyph__node--core" }]
  },
  chat: {
    circles: [
      { cx: 32, cy: 32, r: 9, class: "rail-glyph__orbit rail-glyph__accent" },
      { cx: 32, cy: 32, r: 18, class: "rail-glyph__orbit rail-glyph__orbit--slow" }
    ],
    paths: [
      { d: "M18 32c4-8 24-8 28 0", class: "rail-glyph__line" },
      { d: "M20 41c7 7 17 7 24 0", class: "rail-glyph__line" },
      { d: "M25 31c2-2 4-2 6 0s4 2 6 0 4-2 6 0", class: "rail-glyph__wave" }
    ],
    dots: [
      { cx: 32, cy: 32, r: 1.8, class: "rail-glyph__node rail-glyph__node--core" },
      { cx: 46, cy: 32, r: 1.2, class: "rail-glyph__node" }
    ]
  },
  companion: {
    ellipses: [
      { cx: 32, cy: 32, rx: 23, ry: 10, class: "rail-glyph__orbit rail-glyph__tilt-a rail-glyph__orbit--slow" },
      { cx: 32, cy: 32, rx: 10, ry: 23, class: "rail-glyph__orbit rail-glyph__tilt-b" }
    ],
    paths: [{ d: "M22 34c3-9 17-9 20 0-3 8-17 8-20 0Z", class: "rail-glyph__geometry rail-glyph__accent" }],
    dots: [
      { cx: 32, cy: 31, r: 2, class: "rail-glyph__node rail-glyph__node--core" },
      { cx: 47, cy: 24, r: 1.2, class: "rail-glyph__node" }
    ]
  },
  workbench: {
    polygons: [
      { points: "32 13 48 23 48 41 32 51 16 41 16 23", class: "rail-glyph__geometry" },
      { points: "32 22 41 38 23 38", class: "rail-glyph__geometry rail-glyph__accent" }
    ],
    lines: [
      { x1: 32, y1: 22, x2: 32, y2: 13, class: "rail-glyph__line" },
      { x1: 23, y1: 38, x2: 16, y2: 41, class: "rail-glyph__line" },
      { x1: 41, y1: 38, x2: 48, y2: 41, class: "rail-glyph__line" }
    ],
    dots: [
      { cx: 32, cy: 22, r: 1.5, class: "rail-glyph__node" },
      { cx: 23, cy: 38, r: 1.5, class: "rail-glyph__node" },
      { cx: 41, cy: 38, r: 1.5, class: "rail-glyph__node" },
      { cx: 32, cy: 34, r: 2, class: "rail-glyph__node rail-glyph__node--core" }
    ]
  },
  loading: {
    circles: [
      { cx: 32, cy: 32, r: 20, class: "rail-glyph__orbit rail-glyph__orbit--slow rail-glyph__dash" },
      { cx: 32, cy: 32, r: 10, class: "rail-glyph__orbit rail-glyph__accent" }
    ],
    paths: [
      { d: "M32 14a18 18 0 0 1 18 18", class: "rail-glyph__scan" },
      { d: "M21 32h22M32 21v22", class: "rail-glyph__line" }
    ],
    dots: [{ cx: 32, cy: 32, r: 2.1, class: "rail-glyph__node rail-glyph__node--core" }]
  },
  storage: {
    polygons: [
      { points: "32 13 49 22 49 42 32 51 15 42 15 22", class: "rail-glyph__geometry rail-glyph__accent" },
      { points: "32 23 41 28 41 38 32 43 23 38 23 28", class: "rail-glyph__geometry" }
    ],
    paths: [
      { d: "M15 22l17 10 17-10M32 32v19", class: "rail-glyph__line" },
      { d: "M23 28l9 5 9-5", class: "rail-glyph__line" }
    ],
    dots: [{ cx: 32, cy: 32, r: 1.8, class: "rail-glyph__node rail-glyph__node--core" }]
  },
  settings: {
    circles: [
      { cx: 32, cy: 32, r: 20, class: "rail-glyph__orbit rail-glyph__orbit--slow" },
      { cx: 32, cy: 32, r: 11, class: "rail-glyph__orbit rail-glyph__accent" }
    ],
    paths: [
      { d: "M32 10v6M32 48v6M10 32h6M48 32h6M16.5 16.5l4.2 4.2M43.3 43.3l4.2 4.2M47.5 16.5l-4.2 4.2M20.7 43.3l-4.2 4.2", class: "rail-glyph__line" }
    ],
    dots: [{ cx: 32, cy: 32, r: 2, class: "rail-glyph__node rail-glyph__node--core" }]
  },
  personality: {
    circles: [{ cx: 32, cy: 32, r: 20, class: "rail-glyph__orbit rail-glyph__orbit--slow" }],
    polygons: [
      { points: "32 12 39 27 55 32 39 37 32 52 25 37 9 32 25 27", class: "rail-glyph__geometry rail-glyph__accent" },
      { points: "32 23 39 32 32 41 25 32", class: "rail-glyph__geometry" }
    ],
    dots: [
      { cx: 32, cy: 32, r: 2.1, class: "rail-glyph__node rail-glyph__node--core" },
      { cx: 55, cy: 32, r: 1.1, class: "rail-glyph__node" }
    ]
  },
  about: {
    circles: [
      { cx: 32, cy: 32, r: 20, class: "rail-glyph__orbit rail-glyph__orbit--slow" },
      { cx: 32, cy: 32, r: 7, class: "rail-glyph__orbit rail-glyph__accent" }
    ],
    paths: [
      { d: "M32 27v14M32 22v.1", class: "rail-glyph__wave rail-glyph__accent" },
      { d: "M17 25c7-7 23-7 30 0M17 39c7 7 23 7 30 0", class: "rail-glyph__line" }
    ],
    dots: [
      { cx: 32, cy: 32, r: 2, class: "rail-glyph__node rail-glyph__node--core" },
      { cx: 47, cy: 25, r: 1.1, class: "rail-glyph__node" },
      { cx: 17, cy: 39, r: 1.1, class: "rail-glyph__node" }
    ]
  }
};

const glyph = computed(() => GLYPHS[props.type] || GLYPHS.home);
</script>

<template>
  <svg class="rail-glyph" :data-glyph="type" viewBox="0 0 64 64" aria-hidden="true">
    <g class="rail-glyph__rotor">
      <ellipse v-for="(ellipse, index) in glyph.ellipses || []" :key="`e-${index}`" v-bind="ellipse" />
      <circle v-for="(circle, index) in glyph.circles || []" :key="`c-${index}`" v-bind="circle" />
    </g>
    <g class="rail-glyph__body">
      <polygon v-for="(polygon, index) in glyph.polygons || []" :key="`g-${index}`" v-bind="polygon" />
      <line v-for="(line, index) in glyph.lines || []" :key="`l-${index}`" v-bind="line" />
      <path v-for="(path, index) in glyph.paths || []" :key="`p-${index}`" v-bind="path" />
      <circle v-for="(dot, index) in glyph.dots || []" :key="`d-${index}`" v-bind="dot" />
    </g>
  </svg>
</template>
