<script setup>
import { computed } from "vue";
import RailGlyph from "./RailGlyph.vue";

const props = defineProps({
  scenes: {
    type: Array,
    default: () => []
  },
  groups: {
    type: Array,
    default: () => []
  },
  currentScene: {
    type: String,
    default: "home"
  },
  currentGroup: {
    type: Number,
    default: 0
  }
});

defineEmits(["navigate", "select-group"]);

const activeSceneMeta = computed(() => props.scenes.find((scene) => scene.id === props.currentScene) || props.scenes[0] || null);
const activeGroupMeta = computed(() => props.groups[props.currentGroup] || props.groups[0] || null);
</script>

<template>
  <nav class="rail-nav" aria-label="空间导航" data-promoted-layer="true">
    <div class="rail-nav__shell">
      <div class="rail-nav__group-list" aria-label="空间分组">
        <button
          v-for="(group, index) in groups"
          :key="group.id"
          type="button"
          class="rail-nav__group-button"
          :class="{ 'is-active': currentGroup === index }"
          :aria-label="group.title"
          @click.prevent="$emit('select-group', index)"
        >
          <span class="rail-nav__button-glow" aria-hidden="true"></span>
          <RailGlyph :type="group.id" />
        </button>
      </div>

      <span class="rail-nav__divider" aria-hidden="true"></span>

      <div class="rail-nav__scene-list">
        <button
          v-for="scene in scenes"
          :key="scene.id"
          type="button"
          class="rail-nav__button"
          :class="{ 'is-active': currentScene === scene.id }"
          :aria-label="scene.title"
          @click.prevent="$emit('navigate', scene.id)"
        >
          <span class="rail-nav__button-glow" aria-hidden="true"></span>
          <RailGlyph :type="scene.id" />
        </button>
      </div>
    </div>

    <div class="rail-nav__readout" v-if="activeSceneMeta">
      <strong>{{ activeSceneMeta.title }}</strong>
      <small>{{ activeGroupMeta?.title || activeSceneMeta.titleEn }}</small>
    </div>
  </nav>
</template>
