# Homelab Project Deploy Checklist

Walk through every item before declaring a deploy of this project
complete. If an item does not apply, mark `N/A` with one line of
justification (so the next reader knows it was considered, not
forgotten).

## Build and image

- [ ] Built on dev-vm (`docker build -t <project>:v<semver> .`).
- [ ] Image transferred to target host via
  `docker save <project>:v<semver> | ssh <host> docker load`.
- [ ] Tag follows the convention `<project>-<service>:v<semver>` from
  `~/src/home-infra/docs/CONVENTIONS.md` *Docker Image Management*.

## Secrets

- [ ] Doppler project + config exist in workspace `Xibstar`.
- [ ] On dev-vm: Doppler CLI authenticated (`doppler login`).
- [ ] On NAS: service token configured (Doppler CLI not installed on
  NAS; use `dopplerhq/cli` Docker image with `DOPPLER_TOKEN`).
- [ ] No secret values committed to this repo, to `infra.contract.yml`,
  or to any docs.

## Runtime

- [ ] `docker-compose.yml` placed at the standard path:
  - dev-vm: `~/runtime/<project>/docker-compose.yml`
  - NAS: `/share/Container/compose/<project>/docker-compose.yml`
- [ ] Container starts cleanly (`docker compose up -d`).
- [ ] Healthcheck passes (if defined). Logs show no errors on startup.
- [ ] On NAS, verified the docker-compose path workaround:
  `/usr/local/lib/docker/cli-plugins/docker-compose up -d`.

## Network and TLS (only if the project exposes UI / API / status)

- [ ] DNS configured: UDM static `A` record
  `<service>.lamanoriega.com → <host-ip>` (TTL 300).
- [ ] `edge-caddy` Caddyfile patched on NAS:
  - new `@<service>` matcher,
  - `handle` block with `reverse_proxy http://127.0.0.1:<port>`
    (or `https://<host>:<port>` for hosts with their own TLS),
  - Caddyfile backup saved as
    `Caddyfile.bak.before-<service>-<YYYYMMDD>-<HHMM>`.
- [ ] `edge-caddy` restarted on NAS using the **full path** of the
  compose plugin (the `docker compose` subcommand is not available
  on QNAP; see `~/src/home-infra/docs/CONVENTIONS.md` *Docker Image
  Management*):
  ```sh
  /usr/local/lib/docker/cli-plugins/docker-compose \
      -f /share/Container/compose/edge-caddy/docker-compose.yml \
      restart edge-caddy
  ```
  Use `restart`, not `caddy reload`. Reload alone may not pick up a
  newly added vhost depending on how Caddy was started; restart is
  the safer pattern documented in past TLS Hub sessions.
- [ ] HTTPS verified from LAN
  (`curl -fsS https://<service>.lamanoriega.com/...`).
- [ ] Cert chain confirmed
  (`*.lamanoriega.com` wildcard, currently valid).

## Source of truth (`~/src/home-infra/`)

- [ ] `docs/INVENTORY.md` updated when hosts, ports, or IPs change.
- [ ] `docs/SERVICES.md` updated with the new or relocated service.
- [ ] `docs/PROJECTS.md` updated (project entry, version, status).
- [ ] `catalog/services.yml` updated **only if portal-visible**
  (will be rendered by `infra-portal`).
- [ ] If portal-visible: ran
  `~/src/infra-portal/scripts/sync-catalog-to-nas.sh` to sync the
  runtime catalog copy and write `CATALOG_COMMIT`.
- [ ] All `home-infra` changes committed and pushed.

## Documentation in this project

- [ ] `docs/operations/DEPLOY_PLAYBOOK.md` reflects the deploy reality
  (paths, images, hosts, compose location, rollback recipe). Links to
  `~/src/home-infra/docs/CONVENTIONS.md` instead of duplicating it.
- [ ] `docs/llm/HANDOFF.md` *Last Updated* and *Session Focus* match
  this session.
- [ ] `docs/llm/HISTORY.md` has an entry for this deploy.
- [ ] `CHANGELOG.md` reflects the new version.
- [ ] `VERSION` and all version-synced doc-version markers in sync
  (`scripts/check-version-sync.sh`).
- [ ] Project repo committed and pushed.

## Optional: Project contract (experimental)

- [ ] `infra.contract.yml` declared at the project root, with `TODO`
  placeholders replaced by real values.
- [ ] Validated against `~/src/home-infra-protocol/schemas/` (when a
  validator exists; today this is a manual sanity check against
  `docs/PROJECT_CONTRACTS.md`).
- [ ] No secret values in the contract; only Doppler references.
- [ ] Note in `docs/llm/DECISIONS.md` recording that this project
  declares a contract and which protocol version it targets.

## Final smoke check

- [ ] From a LAN client: the service responds at its public URL with
  the expected status, payload, or login screen.
- [ ] From a WireGuard client: same as above.
- [ ] No regression in adjacent services on the same host
  (spot-check at least one other vhost on `edge-caddy`).
