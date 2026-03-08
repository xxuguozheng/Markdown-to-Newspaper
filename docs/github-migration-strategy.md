# GitHub Migration Strategy

This document describes how the workspace is split into project-level public or semi-public repositories.

## Migration principles
- Never publish the whole workspace as one repository.
- Migrate one project at a time.
- Build a public-copy directory first, then review, then push.
- Prefer preserving runnable examples and docs over preserving local runtime traces.

## Good candidates for migration
- self-contained product prototypes
- UI/demo sites with reusable templates
- scripts and schema that explain a workflow
- research artifacts that do not expose private accounts, chats, or machine details

## Poor candidates / do not migrate directly
- mixed personal workspace roots
- projects containing private notes, account tokens, auth state, or message history
- repos whose current value depends on local absolute paths or machine-specific mounts
- generated archives that mainly reflect one user's runtime session traces

## Sanitization rules

### Common rules
- remove absolute local paths
- remove tokens, auth files, and invalid/old account material
- remove runtime request/receipt/output traces unless they are intentionally rewritten as demos
- rename live session identifiers to neutral placeholders like `public-demo`
- exclude caches, build trash, and machine-local temp files

### OpenClaw-Newspaper
- keep templates, scripts, public HTML examples, and source-of-truth data
- remove `data/requests/`, `data/receipts/`, `data/publish/requests/`, `data/publish/receipts/` runtime JSONs
- remove session-demo and execution-receipt digest artifacts
- rewrite `source.sessionId` values to `public-demo` in kept examples
- rewrite local project root paths to relative paths

## Recommended flow for future projects
1. select a single project
2. copy to `tmp/public-repos/<project>`
3. sanitize and re-run minimal validation
4. search again for sensitive strings
5. create target repo under `Vimalinx-zero`
6. push only the sanitized copy
