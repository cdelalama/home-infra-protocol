<!-- doc-version: 0.1.2 -->
# Changelog

All notable changes to Home Infra Protocol are tracked here.

## [0.1.2] - 2026-05-01

### Added

- README "Ecosystem map" section listing the four ecosystem
  repositories alongside this one, with role and visibility per
  repo. The map makes the public/private split explicit so
  external readers can see why source-of-truth and consumer repos
  are intentionally not on GitHub publicly.

### Changed

- README clarifies that `LLM-DocKit` is kept separate from this
  protocol on purpose, so it can stay general-purpose. New
  ecosystem projects scaffold from `LLM-DocKit` first per
  `docs/GOVERNANCE.md` *Project Bootstrap Rule* and may opt into
  the protocol's contracts as they mature.

### Fixed

## [0.1.1] - 2026-05-01

### Added

- Added `docs/GOVERNANCE.md` with field policy, ownership boundaries,
  project bootstrap rules, and compliance-claim freshness rules.
- Documented that new ecosystem projects should start from LLM-DocKit unless
  the user explicitly approves a waiver.

### Changed

- Linked the governance rules from the README, spec, usage guide, start-here
  guide, and structure map.

### Fixed

## [0.1.0] - 2026-05-01

### Added

- Created the project from LLM-DocKit.
- Added the first draft protocol specification.
- Added JSON Schema drafts for services, hosts, and project contracts.
- Added sanitized examples for a source-of-truth repo and project contract.
- Documented completion, security, recovery, LLM workflow, and project contract
  direction.
