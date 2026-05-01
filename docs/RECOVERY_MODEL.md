<!-- doc-version: 0.1.3 -->
# Recovery Model

The protocol distinguishes recovering the **knowledge system** from rebuilding
all live services.

## Knowledge Recovery

If the source-of-truth and consumer repos are lost, the target workflow is:

```text
clone source-of-truth repo
read project index and project contracts
clone relevant project repos
validate or regenerate catalogs
start consumers against those catalogs
```

This restores what the operator and LLM agents know about the infrastructure.

## Service Recovery

Rebuilding live services is project-specific. Project contracts should link to
rebuild, restore, verify, and rollback runbooks, but this protocol does not
execute them.
