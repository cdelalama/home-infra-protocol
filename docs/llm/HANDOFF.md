<!-- doc-version: 0.1.1 -->
# LLM Work Handoff

This file is the current operational snapshot. Durable decisions live in
`docs/llm/DECISIONS.md`.

## Current Status

- Last Updated: 2026-05-01 - Codex
- Session Focus: Patch 0.1.1 — document protocol governance and ecosystem
  project bootstrap rules.
- Status: 0.1.1 is documentation-only. The protocol now records field policy,
  ownership boundaries, compliance-claim rules, and the rule that new ecosystem
  projects start from LLM-DocKit unless the user explicitly approves a waiver.

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
- New ecosystem projects such as a future `infra-agent` should start from
  `cdelalama/LLM-DocKit` unless Carlos explicitly approves a waiver.

## Next Concrete Steps

1. Review the v0.1 draft and governance rules with the user.
2. Decide whether the repo should remain spec-only for v0.1.
3. Add CI validation once a validator exists.
4. Add protocol version declarations for private implementations later.
5. If `infra-agent` starts, document its stats contract as a candidate
   telemetry-provider extension before wiring it into `infra-portal`.

## Files To Read First

- `README.md`
- `SPEC.md`
- `docs/PROJECT_CONTEXT.md`
- `docs/ARCHITECTURE.md`
- `docs/COMPLETION_RULE.md`
- `docs/GOVERNANCE.md`
- `docs/PROJECT_CONTRACTS.md`
