<script setup>
import { computed, ref } from "vue";
import ActionButton from "../components/ActionButton.vue";
import HoloCard from "../components/HoloCard.vue";
import MetricLine from "../components/MetricLine.vue";
import TechText from "../components/TechText.vue";
import { ICON_PATHS } from "../app/sceneRegistry";

const props = defineProps({
  scene: { type: Object, required: true },
  active: { type: Boolean, default: false },
  state: { type: Object, required: true },
  view: { type: Object, required: true },
  actions: { type: Object, required: true }
});

const composerFocused = ref(false);

const sceneClasses = computed(() => ({
  "is-active": props.active,
  "is-listening": props.state.chat.running,
  "is-thinking": props.state.chat.phase === "thinking",
  "is-replying": props.state.chat.phase === "replying",
  "is-focused": composerFocused.value
}));

const voiceBars = computed(() =>
  Array.from({ length: 7 }, (_, index) => 0.34 + (((props.view.voicePercent + index * 13) % 36) / 36) * 0.88)
);
</script>

<template>
  <section class="scene-panel scene-panel--chat" :class="sceneClasses" aria-label="对话空间">
    <div class="scene-ambient scene-ambient--chat" aria-hidden="true"></div>
    <div class="scene-grid">
      <div class="span-3 scene-side-stack">
        <TechText as="p" tone="muted">{{ scene.title }} / <span class="mono-inline">{{ scene.titleEn }}</span></TechText>

        <HoloCard class="info-card" tone="strong">
          <p class="scene-kicker">Lumi 状态</p>
          <p class="presence-copy"><strong>Lumi</strong><small>{{ view.presenceCopy }}</small></p>
          <MetricLine label="对话阶段" :value="view.chatStageLabel" :progress="state.emotion.presenceLevel" />
          <MetricLine label="听觉活性" :value="`${view.voicePercent}%`" :progress="state.chat.voiceLevel" />
          <MetricLine label="呼吸节律" :value="`${view.breathPercent}%`" :progress="state.emotion.breathLevel" />
          <p class="panel-note">{{ state.chat.status }}</p>
        </HoloCard>

        <div class="chat-actions">
          <ActionButton label="开始倾听" subtitle="Listen" :icon-path="ICON_PATHS.listen" semantic="chat" @click="actions.beginConversation" />
          <ActionButton label="回到安静" subtitle="Quiet" :icon-path="ICON_PATHS.quiet" semantic="companion" @click="actions.stopVoice" />
          <ActionButton label="清空星线" subtitle="Clear" :icon-path="ICON_PATHS.clear" semantic="system" @click="actions.clearChat" />
        </div>
      </div>

      <div class="span-6 chat-focus-shell">
        <HoloCard class="chat-stream" tone="strong">
          <div class="chat-stream__head">
            <div>
              <p class="scene-kicker">消息流</p>
              <p class="panel-note">输入、倾听与回应会在这里形成连续的对话轨迹。</p>
            </div>
            <TechText tone="muted" mono>{{ state.chat.messages.length }} MSG</TechText>
          </div>

          <div class="chat-stream__messages">
            <article class="chat-message chat-message--assistant chat-message--intro">
              <span class="chat-message__dot" aria-hidden="true"></span>
              <div class="chat-message__body">
                <strong>Lumi</strong>
                <p>今夜从哪里开始都可以。我在这里，慢一点也没关系。</p>
              </div>
            </article>

            <TransitionGroup name="message-fade" tag="div" class="chat-stream__message-list">
              <article
                v-for="(message, index) in state.chat.messages"
                :key="`${message.role}-${index}-${message.body}`"
                class="chat-message"
                :class="`chat-message--${message.role}`"
              >
                <span class="chat-message__dot" aria-hidden="true"></span>
                <div class="chat-message__body">
                  <strong>{{ message.author || (message.role === "assistant" ? "Lumi" : "You") }}</strong>
                  <p>{{ message.body }}</p>
                </div>
              </article>
            </TransitionGroup>
          </div>
        </HoloCard>

        <form
          class="chat-dock"
          :class="{ 'is-focused': composerFocused, 'is-running': state.chat.running }"
          data-promoted-layer="true"
          @submit.prevent="actions.sendCurrentText"
        >
          <span class="chat-dock__glow" aria-hidden="true"></span>
          <span class="chat-dock__orb" aria-hidden="true"></span>
          <input
            :value="state.ui.composerText"
            type="text"
            autocomplete="off"
            placeholder="轻声说点什么..."
            @focus="composerFocused = true"
            @blur="composerFocused = false"
            @input="actions.setComposerText($event.target.value)"
          />
          <div class="voice-wave" aria-hidden="true">
            <span v-for="(value, index) in voiceBars" :key="index" :style="{ transform: `scaleY(${value})` }"></span>
          </div>
          <button type="submit" class="dock-send" aria-label="发送消息">
            <svg viewBox="0 0 24 24"><path d="M12 5 19 18H5Z" /></svg>
          </button>
        </form>
      </div>

      <div class="span-3 scene-side-stack">
        <HoloCard class="chat-status-stack">
          <p class="scene-kicker">空间反馈</p>
          <MetricLine label="存在亮度" :value="`${view.presencePercent}%`" :progress="state.emotion.presenceLevel" />
          <MetricLine label="呼吸频率" :value="`${view.breathPercent}%`" :progress="state.emotion.breathLevel" />
          <MetricLine label="回应意愿" :value="view.stateLabel" :progress="view.progressRatio" />
          <MetricLine label="当前情绪" :value="view.moodLabel" :progress="state.emotion.breathLevel" />
        </HoloCard>

        <HoloCard class="info-card">
          <p class="scene-kicker">轻量提示</p>
          <p class="panel-note">输入时轨道会轻微展开，倾听与回应会抬升核心亮度，但不会打扰你的阅读节奏。</p>
        </HoloCard>
      </div>
    </div>
  </section>
</template>
