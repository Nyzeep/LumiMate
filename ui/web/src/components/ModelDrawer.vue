<template>
  <aside class="model-drawer" :class="{ 'is-open': open }" :aria-hidden="!open">
    <button type="button" class="model-drawer__close" aria-label="关闭配置" @click.prevent="$emit('close')">
      <svg viewBox="0 0 24 24"><path d="M6 6l12 12M18 6 6 18" /></svg>
    </button>
    <p class="scene-kicker">{{ title }}</p>
    <h2>{{ name }}</h2>
    <p class="panel-note">{{ caption }}</p>
    <div class="model-drawer__path">
      <span>本地位置</span>
      <code>{{ path || "尚未选择" }}</code>
    </div>
    <button type="button" class="slender-button" @click.prevent="$emit('open-path')">打开本地文件夹</button>
    <div class="model-drawer__options">
      <button
        v-for="option in options"
        :key="option.id || option.path || option.title"
        type="button"
        :class="{ 'is-active': option.path === path }"
        @click.prevent="$emit('select', option.path)"
      >
        <span>{{ option.title }}</span>
        <small>{{ option.subtitle }}</small>
      </button>
    </div>
  </aside>
</template>

<script setup>
defineProps({
  open: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ""
  },
  name: {
    type: String,
    default: ""
  },
  caption: {
    type: String,
    default: ""
  },
  path: {
    type: String,
    default: ""
  },
  options: {
    type: Array,
    default: () => []
  }
});

defineEmits(["close", "select", "open-path"]);
</script>
