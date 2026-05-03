<!-- doc-version: 0.2.2 -->
# Home Infra Protocol

A Git-based infrastructure memory protocol for humans, dashboards, and LLM
agents.

**Version:** see [VERSION](VERSION) | [CHANGELOG](CHANGELOG.md)

## Overview

Home Infra Protocol defines how a small infrastructure can describe itself in
plain documentation plus machine-readable catalogs. The goal is to make current
state legible to humans, portals, MCP servers, recovery workflows, and LLM
agents without turning any one consumer into the source of truth.

The protocol started from the `home-infra` and `infra-portal` split:
`home-infra` owns durable truth, while `infra-portal` renders that truth and
adds observed telemetry. This repository extracts that pattern into reusable
specification material, schemas, examples, and future validation tooling.

## Ecosystem map

The protocol exists alongside four other repositories that together form a
working homelab. Visibility differs deliberately: source-of-truth and consumer
repositories are private because they contain real hosts, IPs, runbook
references, and secret store names. The protocol stays public so others can
adopt or learn from the same contracts.

| Repository | Role | Visibility | Status |
|------------|------|------------|--------|
| [`cdelalama/LLM-DocKit`](https://github.com/cdelalama/LLM-DocKit) | General-purpose documentation scaffold reused across projects in this ecosystem and beyond | Public | Operational |
| `cdelalama/home-infra-protocol` (this repo) | Public specification of the contracts | Public | Draft v0.1 |
| `cdelalama/home-infra` | Private source-of-truth implementation (inventory, services, hosts, runbooks) | Private | Operational |
| `cdelalama/infra-portal` | Private consumer / renderer reading the source-of-truth catalog | Private | Operational |
| `cdelalama/infra-agent` | Planned per-host telemetry provider | — | Not yet created |

`LLM-DocKit` is intentionally kept separate from this protocol so it can stay
general-purpose. New ecosystem projects scaffold from `LLM-DocKit` first
(per `docs/GOVERNANCE.md` *Project Bootstrap Rule*) and may opt into the
protocol's contracts as they mature.

## Quick Start

```bash
git clone https://github.com/cdelalama/home-infra-protocol.git
cd home-infra-protocol
```

Start with [SPEC.md](SPEC.md), then compare the example catalog under
[examples/home-infra](examples/home-infra) with the JSON Schemas under
[schemas](schemas).

## Documentation

| Document | Purpose |
|----------|---------|
| [SPEC.md](SPEC.md) | Draft protocol specification |
| [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) | Vision and current scope |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Protocol components and roadmap |
| [docs/COMPLETION_RULE.md](docs/COMPLETION_RULE.md) | Definition of done for infrastructure changes |
| [docs/PROJECT_CONTRACTS.md](docs/PROJECT_CONTRACTS.md) | Project-level contract direction |
| [docs/GOVERNANCE.md](docs/GOVERNANCE.md) | Field policy, ownership, bootstrap, compliance claims |
| [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) | Exposure and trust model |
| [docs/RECOVERY_MODEL.md](docs/RECOVERY_MODEL.md) | Rebuilding the knowledge system |
| [docs/LLM_WORKFLOW.md](docs/LLM_WORKFLOW.md) | How LLM agents should use the protocol |
| [docs/STRUCTURE.md](docs/STRUCTURE.md) | Repository layout |
| [docs/llm/HANDOFF.md](docs/llm/HANDOFF.md) | Current work state |

## Contributing

Keep changes small and explicit. Schema changes should be additive unless a
major version deliberately breaks compatibility.

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.

---

*Documentation scaffold powered by [LLM-DocKit](https://github.com/cdelalama/LLM-DocKit).*
