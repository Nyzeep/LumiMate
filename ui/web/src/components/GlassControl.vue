<script setup>
import { computed } from "vue";
import { useHoverIntent } from "../composables/useHoverIntent";

const CONTROL_ACCENTS = new Set(["core", "chat", "companion", "model", "system"]);

const props = defineProps({
  label: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ""
  },
  iconPath: {
    type: String,
    default: ""
  },
  iconViewBox: {
    type: String,
    default: "0 0 24 24"
  },
  kind: {
    type: String,
    default: "compact",
    validator: (value) => ["card", "icon", "compact"].includes(value)
  },
  buttonType: {
    type: String,
    default: "button",
    validator: (value) => ["button", "submit", "reset"].includes(value)
  },
  visuallyHideCopy: {
    type: Boolean,
    default: false
  },
  bareGlyph: {
    type: Boolean,
    default: false
  },
  truncateCopy: {
    type: Boolean,
    default: false
  },
  priority: {
    type: String,
    default: "secondary",
    validator: (value) => ["primary", "secondary", "quiet"].includes(value)
  },
  intent: {
    type: String,
    default: "neutral",
    validator: (value) => ["neutral", "danger"].includes(value)
  },
  accent: {
    type: String,
    default: "core"
  },
  disabled: {
    type: Boolean,
    default: false
  },
  block: {
    type: Boolean,
    default: false
  },
  selected: {
    type: Boolean,
    default: null
  },
  selectionRole: {
    type: String,
    default: "button",
    validator: (value) => ["button", "tab", "radio"].includes(value)
  },
  ariaLabel: {
    type: String,
    default: ""
  }
});

const emit = defineEmits(["click"]);
const { isEngaged, style, handlers } = useHoverIntent({
  disabled: computed(() => props.disabled)
});

const resolvedAccent = computed(() => (CONTROL_ACCENTS.has(props.accent) ? props.accent : "core"));

const accessibleLabel = computed(() => {
  const label = props.ariaLabel || props.label;
  return props.intent === "danger" ? "危险操作：" + label : label;
});

function activate(event) {
  if (!props.disabled) {
    emit("click", event);
  }
}
</script>

<template>
  <button
    :type="buttonType"
    class="glass-control"
    :class="[
      'glass-control--' + kind,
      'glass-control--' + priority,
      'glass-control--' + intent,
      'glass-control--accent-' + resolvedAccent,
      {
        'glass-control--block': block,
        'has-glyph': Boolean(iconPath),
        'has-bare-glyph': bareGlyph,
        'has-truncated-copy': truncateCopy,
        'has-visually-hidden-copy': visuallyHideCopy,
        'is-selected': selected === true
      }
    ]"
    :role="selectionRole === 'button' ? undefined : selectionRole"
    :aria-label="accessibleLabel"
    :aria-disabled="disabled ? 'true' : undefined"
    :aria-pressed="selectionRole === 'button' && selected !== null ? String(selected) : undefined"
    :aria-selected="selectionRole === 'tab' ? String(selected === true) : undefined"
    :aria-checked="selectionRole === 'radio' ? String(selected === true) : undefined"
    :disabled="disabled"
    :data-kind="kind"
    :data-priority="priority"
    :data-intent="intent"
    :data-hovered="isEngaged ? 'true' : 'false'"
    :style="style"
    data-promoted-layer="true"
    v-on="handlers"
    @click="activate"
  >
    <span class="glass-control__glow" aria-hidden="true"></span>
    <span class="glass-control__press" aria-hidden="true"></span>
    <slot>
      <span v-if="iconPath" class="glass-control__glyph" aria-hidden="true">
        <svg :viewBox="iconViewBox">
          <path :d="iconPath" />
        </svg>
      </span>
      <span class="glass-control__copy">
        <strong>{{ label }}</strong>
        <small v-if="subtitle">{{ subtitle }}</small>
      </span>
    </slot>
    <small v-if="intent === 'danger'" class="glass-control__intent-label">危险操作</small>
  </button>
</template>

<style scoped>
.glass-control {
  --_glass-control-accent: 255, 182, 118;
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: var(--glass-control-justify-content, center);
  gap: 10px;
  min-inline-size: 0;
  min-height: 42px;
  padding: 10px 16px;
  border: var(--border-hairline) solid rgba(255, 255, 255, 0.16);
  border-radius: var(--glass-control-radius, var(--radius-md));
  overflow: hidden;
  color: var(--color-text);
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.1), rgba(24, 39, 66, 0.12) 42%, rgba(7, 17, 37, 0.16)),
    var(--color-glass);
  box-shadow: inset 0 1px rgba(255, 255, 255, 0.13), var(--shadow-soft);
  font: inherit;
  text-align: var(--glass-control-text-align, left);
  transition:
    border-color var(--duration-sm) var(--ease-standard),
    box-shadow var(--duration-sm) var(--ease-standard),
    transform var(--duration-xs) var(--ease-standard),
    background var(--duration-sm) var(--ease-standard);
}

.glass-control::before {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(115deg, rgba(255, 255, 255, 0.13), transparent 30%, transparent 74%, rgba(var(--_glass-control-accent), 0.07));
  content: "";
  pointer-events: none;
}

.glass-control__glow,
.glass-control__press {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  pointer-events: none;
}

.glass-control__glow {
  background: radial-gradient(circle at 50% 50%, rgba(var(--_glass-control-accent), 0.18), transparent 70%);
  opacity: var(--hover-intent, 0);
  transition: opacity var(--duration-sm) var(--ease-standard);
}

.glass-control__press {
  background: rgba(255, 255, 255, 0.08);
  opacity: var(--press-intent, 0);
  transition: opacity var(--duration-xs) var(--ease-standard);
}

.glass-control:hover:not(:disabled),
.glass-control:focus-visible:not(:disabled) {
  border-color: rgba(255, 230, 207, 0.34);
  box-shadow: inset 0 1px rgba(255, 255, 255, 0.2), 0 14px 34px rgba(0, 0, 0, 0.25), 0 0 26px rgba(var(--_glass-control-accent), 0.1);
  transform: translateY(-1px);
}

.glass-control:active:not(:disabled) {
  transform: translateY(1px) scale(0.985);
}

.glass-control:focus-visible {
  outline: 2px solid var(--color-amber-soft);
  outline-offset: 3px;
}

.glass-control:disabled {
  cursor: not-allowed;
  opacity: 0.46;
}

.glass-control--card {
  justify-content: flex-start;
  min-width: var(--glass-control-card-min-inline-size, min(100%, 220px));
  min-height: var(--glass-control-card-min-height, 104px);
  padding: var(--glass-control-card-padding, 14px 18px 14px 14px);
}

.glass-control--card.has-glyph {
  display: grid;
  grid-template-columns: var(--glass-control-card-glyph-track-size, var(--glass-control-card-glyph-size, 58px)) minmax(0, 1fr);
  justify-content: stretch;
  gap: var(--glass-control-card-gap, 12px);
}

.glass-control--block {
  width: 100%;
}

.glass-control--icon {
  display: grid;
  inline-size: var(--glass-control-icon-inline-size, auto);
  block-size: var(--glass-control-icon-block-size, auto);
  min-inline-size: var(--glass-control-icon-min-inline-size, var(--glass-control-icon-inline-size, 120px));
  min-block-size: var(--glass-control-icon-min-block-size, var(--glass-control-icon-block-size, 94px));
  padding: var(--glass-control-icon-padding, 10px 16px);
  border-radius: var(--glass-control-icon-radius, var(--glass-control-radius, var(--radius-md)));
  place-items: center;
  text-align: center;
}

.glass-control--icon .glass-control__copy small:not(.glass-control__intent-label) {
  margin-top: 4px;
}

.glass-control--primary {
  border-color: rgba(255, 218, 183, 0.34);
  background: linear-gradient(135deg, rgba(255, 208, 162, 0.22), rgba(255, 182, 118, 0.12) 56%, rgba(31, 45, 72, 0.19));
  box-shadow: inset 0 1px rgba(255, 255, 255, 0.22), 0 0 2px rgba(255, 255, 255, 0.6), 0 0 26px rgba(255, 161, 84, 0.18), 0 12px 34px rgba(0, 0, 0, 0.22);
}

.glass-control--primary::after {
  position: absolute;
  z-index: -1;
  inset: -24px;
  border-radius: inherit;
  background: radial-gradient(circle at 50% 56%, rgba(var(--_glass-control-accent), 0.25), transparent 62%);
  content: "";
  filter: blur(8px);
  opacity: 0.56;
  animation: glass-control-breathe 8s ease-in-out infinite;
  pointer-events: none;
}

.glass-control--compact {
  min-inline-size: var(--glass-control-compact-min-inline-size, 0);
  min-height: var(--glass-control-compact-min-block-size, 42px);
  padding: var(--glass-control-compact-padding, 10px 16px);
}

.glass-control--quiet {
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.025);
  color: var(--color-muted);
}

.glass-control--compact.glass-control--quiet {
  min-height: var(--glass-control-compact-min-block-size, 38px);
}

.glass-control--danger {
  justify-content: space-between;
  border-color: rgba(229, 169, 127, 0.38);
  background: linear-gradient(135deg, rgba(229, 169, 127, 0.17), rgba(81, 35, 47, 0.17));
  color: #ffe4d8;
}

.glass-control--danger:hover:not(:disabled),
.glass-control--danger:focus-visible:not(:disabled) {
  border-color: rgba(255, 192, 166, 0.58);
  box-shadow: inset 0 1px rgba(255, 255, 255, 0.16), 0 12px 30px rgba(0, 0, 0, 0.24), 0 0 22px rgba(229, 128, 112, 0.16);
}

.glass-control--accent-chat {
  --_glass-control-accent: 255, 196, 132;
}

.glass-control--accent-companion {
  --_glass-control-accent: 248, 208, 176;
}

.glass-control--accent-model {
  --_glass-control-accent: 255, 166, 104;
}

.glass-control--accent-system {
  --_glass-control-accent: 168, 207, 188;
}

.glass-control.is-selected {
  border-color: rgba(255, 218, 183, 0.36);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(var(--_glass-control-accent), 0.13));
}

.glass-control__glyph {
  position: relative;
  z-index: 1;
  display: grid;
  width: var(--glass-control-glyph-size, 42px);
  aspect-ratio: 1;
  place-items: center;
  border: var(--border-hairline) solid rgba(var(--_glass-control-accent), 0.28);
  border-radius: 50%;
  background: rgba(var(--_glass-control-accent), 0.07);
}

.glass-control--card .glass-control__glyph {
  width: var(--glass-control-card-glyph-size, 58px);
}

.glass-control.has-bare-glyph .glass-control__glyph {
  border: 0;
  background: transparent;
}

.glass-control__glyph svg {
  width: var(--glass-control-glyph-svg-size, 58%);
  height: var(--glass-control-glyph-svg-size, 58%);
  fill: none;
  stroke: rgba(var(--_glass-control-accent), 0.98);
  stroke-width: 1.2;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 0 4px rgba(var(--_glass-control-accent), 0.32));
}

.glass-control__copy {
  position: relative;
  z-index: 1;
  min-width: 0;
}

.glass-control.has-visually-hidden-copy .glass-control__copy {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
}

.glass-control__copy strong,
.glass-control__copy small {
  display: block;
}

.glass-control.has-truncated-copy .glass-control__copy strong,
.glass-control.has-truncated-copy .glass-control__copy small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.glass-control__copy strong {
  font-family: var(--glass-control-label-font-family, inherit);
  font-size: var(--glass-control-label-font-size, var(--text-body));
  font-weight: 400;
  letter-spacing: var(--glass-control-label-letter-spacing, normal);
  text-transform: var(--glass-control-label-text-transform, none);
}

.glass-control--card .glass-control__copy strong {
  font-size: var(--glass-control-label-font-size, var(--text-card));
  font-weight: 300;
}

.glass-control__copy small {
  margin-top: 2px;
  color: var(--color-dim);
  font-family: var(--glass-control-subtitle-font-family, var(--font-mono));
  font-size: var(--glass-control-subtitle-font-size, 10px);
  letter-spacing: var(--glass-control-subtitle-letter-spacing, 0.7px);
  text-transform: var(--glass-control-subtitle-text-transform, none);
}

.glass-control--icon .glass-control__copy strong {
  color: var(--color-dim);
  font-family: var(--glass-control-label-font-family, var(--font-mono));
  font-size: var(--glass-control-label-font-size, 11px);
  font-weight: 300;
  letter-spacing: var(--glass-control-label-letter-spacing, var(--tracking-mono));
}

.glass-control__intent-label {
  margin-bottom: 3px;
  color: #ffd0c2 !important;
  letter-spacing: var(--tracking-mono);
  text-transform: uppercase;
}

@keyframes glass-control-breathe {
  0%,
  100% {
    opacity: 0.32;
    transform: scale(0.98);
  }

  50% {
    opacity: 0.68;
    transform: scale(1.03);
  }
}

:global(.reduced-motion) .glass-control--primary::after {
  animation: none;
}

@media (prefers-reduced-motion: reduce) {
  .glass-control--primary::after {
    animation: none;
  }
}
</style>
