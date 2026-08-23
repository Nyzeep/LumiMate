# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`doc/CONTEXT.md`**: LumiMate 领域词汇（Companion / Task Agent / Bridge / Task / Session / Plan / Todo / Grant / Projection / Memory / Workspace 等）
- **`doc/adr/`**: read ADRs that touch the area you're about to work in（如 `0001-harness-agent-topology.md`）

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/domain-modeling` skill creates them lazily when terms or decisions actually get resolved.

## File structure

This repo is **single-context**, but intentionally keeps its domain docs under `doc/` rather than the root-level `docs/` layout:

```text
doc/
├── CONTEXT.md
├── adr/
│   └── 0001-harness-agent-topology.md
├── proposals/
├── research/
└── tasks/
```

Do not create a root-level `CONTEXT.md` or a separate `docs/adr/` tree.

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `doc/CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal: either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/domain-modeling`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders), but worth reopening because…_
