# 06: Cross-space motion and visual acceptance

**What to build:** 用户获得完整、安静且一致的控制体验；所有已迁移空间在不同窗口尺寸和减少动效模式下都保持清晰，且原有背景与整体色调没有回归。

**Blocked by:** 02 (Core-space action controls), 03 (Navigation and choice semantics), 04 (Workbench command rail), 05 (Supporting native control migration).

**Status:** needs-info

- [x] 对已迁移空间审查每个局部区域的 primary 数量、危险意图、文字标签、焦点与禁用行为。
- [x] 确认普通控件默认不持续动画，减少动效模式移除新增无限动画，当前运行或 primary 的柔光保持克制。
- [x] 在 1440×900、1280×720、980px 和 860px 进行浏览器视觉验收，并在 Tauri WebView2 spot-check 半透明、泛光和布局。
- [x] 确认背景资产、环境层和深蓝琥珀色域未被控件改造替换或覆盖。
- [ ] 完整前端构建、前端测试和现有 Runtime 烟雾检查通过。

## Comments

Formal spec: doc/proposals/2026-09-04-glass-control-refinement.md
- 2026-09-04 browser acceptance: all nine migrated spaces had no document-level horizontal overflow at 1440×900, 1280×720, 980×720, and 860×720. Background stage, RuntimeAmbientLayer, and active background remained present; close retained visible and accessible `危险操作` wording; closed drawer stayed inert with a disabled, hidden scrim; focus outline was 2px solid; a disabled download stayed natively disabled; reduced-motion removed primary animation; and task → trail/evidence → command rail order retained visible confirm/reject controls. Galaxy catalog content retained an inner scroll, no overlap, no horizontal overflow, and a reachable action row.
- 2026-09-04 native acceptance: `npx tauri dev --no-watch` compiled and launched the final WebView2 shell. Its local debug target loaded `http://127.0.0.1:5173/` with app shell, background stage, ambient layer, native window controls, and an accessible `危险操作：关闭窗口` control; native 1440×900 and minimum-window checks reported matching document and viewport widths.
- 2026-09-04 verification blocker: `npm test` passed 10 files / 34 tests, `npm run build` passed, and `git diff --check` passed. The existing Runtime smoke was rerun with `D:\LumiMate\.venv` (where pydantic and the SDK import successfully) and reached agent launch, but stopped before task execution because the DeepSeek Harness checkout lacks its dev-only `python/sdk-runtime/.../runtime/node/node_modules/@deepseek-ai/dsh/lib/bin.js` closure. Building that external Harness runtime closure would mutate the Harness checkout and is outside this UI branch; human direction is needed before the final Runtime checkbox can be marked complete.
- 2026-09-04 final seam follow-up: Download catalog cards were migrated to card variables plus caller-owned rich-slot content, removing their last shared-control root/direct-child reach-through. The complete 10-file / 34-test suite, production build, diff whitespace check, all-size browser acceptance, and Galaxy scroll/reachability check were rerun afterward and passed.
