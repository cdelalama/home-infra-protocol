<!-- doc-version: 0.13.5 -->
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
specification material, schemas, examples, and executable validation tooling.

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

Validate a real project interface from the canonical protocol checkout:

```bash
scripts/validate-project-interface.py \
  --contract /path/to/project/infra.contract.yml \
  --status <job-id>=/path/to/project/status.json \
  --obligations-projection /path/to/operational-obligations.json \
  --previous-obligations-projection /path/to/previous-operational-obligations.json
```

Use `--template` only for the TODO-bearing homelab profile starter. Strict mode
rejects TODO values, joins each supplied snapshot to a declared job, enforces
periodic `stale_after > cadence`, validates accepted obligation projections,
rejects stable identity reuse with changed windows when a prior projection is
supplied, and keeps freshness and obligation state consumer-derived.

## Documentation

| Document | Purpose |
|----------|---------|
| [SPEC.md](SPEC.md) | Draft protocol specification |
| [docs/PROJECT_CONTEXT.md](docs/PROJECT_CONTEXT.md) | Vision and current scope |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Protocol components and roadmap |
| [docs/COMPLETION_RULE.md](docs/COMPLETION_RULE.md) | Definition of done for infrastructure changes |
| [docs/PROJECT_CONTRACTS.md](docs/PROJECT_CONTRACTS.md) | Project-level contract direction |
| [docs/CAPABILITY_TRANSPARENCY.md](docs/CAPABILITY_TRANSPARENCY.md) | Visible project capability declaration, runtime evidence, and evolution path |
| [integrations/dockit/INTEGRATION.md](integrations/dockit/INTEGRATION.md) | Reusable homelab profile and validation workflow |
| [docs/STATUS_SNAPSHOT_CONTRACT_PROPOSAL.md](docs/STATUS_SNAPSHOT_CONTRACT_PROPOSAL.md) | Standard Telemetry Source status output |
| [docs/SYNC_JOB_CONTRACT_PROPOSAL.md](docs/SYNC_JOB_CONTRACT_PROPOSAL.md) | Project-owned sync and telemetry job declarations |
| [docs/PARALLEL_ENVIRONMENTS_PROPOSAL.md](docs/PARALLEL_ENVIRONMENTS_PROPOSAL.md) | Development runtime lifecycle and side-effect ownership |
| [docs/RECOVERY_ACCEPTANCE_PROPOSAL.md](docs/RECOVERY_ACCEPTANCE_PROPOSAL.md) | All-surface recovery completion model grounded in two incidents |
| [docs/INCIDENT_LIFECYCLE_PROPOSAL.md](docs/INCIDENT_LIFECYCLE_PROPOSAL.md) | Separation of detection, delivery, acknowledgement, recovery, and closure |
| [docs/OPERATIONAL_OBLIGATIONS_PROPOSAL.md](docs/OPERATIONAL_OBLIGATIONS_PROPOSAL.md) | Project-owned human actions, absolute occurrences, and evidence-only completion |
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
