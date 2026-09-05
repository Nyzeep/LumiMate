<script setup>
import HoloCard from "../components/HoloCard.vue";
import OrbitalIconButton from "../components/OrbitalIconButton.vue";
import TechText from "../components/TechText.vue";
import { ICON_PATHS } from "../app/sceneRegistry";

defineProps({
  scene: { type: Object, required: true },
  active: { type: Boolean, default: false },
  state: { type: Object, required: true },
  view: { type: Object, required: true },
  actions: { type: Object, required: true }
});
</script>

<template>
  <section class="scene-panel scene-panel--settings" :class="{ 'is-active': active }" aria-label="设置">
    <div class="scene-ambient scene-ambient--settings" aria-hidden="true"></div>
    <div class="scene-grid">
      <div class="span-4 scene-copy">
        <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>
        <h2 class="scene-heading scene-heading--medium">系统控制</h2>
        <p class="scene-summary">把界面、动效、启动习惯与系统入口整理成成组控制，而不是稀疏的图标墙。</p>
      </div>

      <div class="span-8 settings-group-grid">
        <HoloCard class="settings-group-card">
          <p class="scene-kicker">界面语言</p>
          <OrbitalIconButton label="切换语言" :icon-path="ICON_PATHS.language" semantic="system" @click="actions.toggleLanguage" />
          <p class="panel-note">当前语言：{{ state.app.language === "zh-CN" ? "简体中文" : "English" }}</p>
        </HoloCard>

        <HoloCard class="settings-group-card">
          <p class="scene-kicker">动效强度</p>
          <OrbitalIconButton label="切换动效" :icon-path="ICON_PATHS.motion" semantic="system" @click="actions.toggleReduceMotion" />
          <p class="panel-note">当前模式：{{ state.app.reduceMotion ? "已收敛" : "标准呼吸" }}</p>
        </HoloCard>

        <HoloCard class="settings-group-card">
          <p class="scene-kicker">启动行为</p>
          <p class="panel-note">当前策略：{{ state.app.checkUpdateOnStartup ? "启动时检查更新" : "保持静默启动" }}</p>
        </HoloCard>

        <HoloCard class="settings-group-card">
          <p class="scene-kicker">系统入口</p>
          <OrbitalIconButton label="前往关于" :icon-path="ICON_PATHS.about" semantic="system" @click="actions.navigate('about')" />
          <p class="panel-note">查看版本、运行环境和 LumiMate 当前所处的本地空间信息。</p>
        </HoloCard>
      </div>
    </div>
  </section>
</template>
