<!-- doc-version: 0.1.0 -->
# LLM Work Handoff

This file is the current operational snapshot. Durable decisions live in
`docs/llm/DECISIONS.md`.

## Current Status

- Last Updated: 2026-05-01 - Codex
- Session Focus: Create `home-infra-protocol` from LLM-DocKit and seed the v0.1
  specification.
- Status: Initial protocol scaffold in progress. Repository is documentation
  and schema only; no validator or runtime exists yet.

## Project Summary

Home Infra Protocol defines a reusable way to describe small infrastructure in
Git so humans, portals, MCP servers, recovery workflows, and LLM agents share a
single current memory.

The first private implementation is expected to be `home-infra`; the first
consumer pattern is expected to be `infra-portal`.

## Important Constraints

- Do not copy private infrastructure facts from `home-infra` into this public
  protocol repo.
- Keep examples sanitized.
- Do not build runtime services before the spec and schemas stabilize.
- Prefer additive schema evolution.

## Next Concrete Steps

1. Review the v0.1 draft with the user.
2. Decide whether the repo should remain spec-only for v0.1.
3. Add CI validation once a validator exists.
4. Add protocol version declarations for private implementations later.

## Files To Read First

- `README.md`
- `SPEC.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/COMPLETION_RULE.md`
- `docs/PROJECT_CONTRACTS.md`
