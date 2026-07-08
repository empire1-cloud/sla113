# Hybrid Intelligence Core Repository

This repository contains the main app and a standalone SLA113 export workflow.

## Run from repo root

All build and export commands are meant to be executed from the repository root, for example:

```bash
cd /path/to/your/repo
bash build_repos.sh sla113-standalone-export-and-build
```

You can run this in any terminal, including:
- VS Code integrated terminal
- your local terminal after pulling the repo
- remote terminal on a server if the repo is there

## Available commands

- `bash build_repos.sh main-backend`
  - install Python dependencies for the main backend
- `bash build_repos.sh main-frontend`
  - install and build the main frontend
- `bash build_repos.sh sla113-backend`
  - install Python dependencies for the SLA113 standalone backend
- `bash build_repos.sh sla113-frontend`
  - install and build the SLA113 standalone frontend (if configured)
- `bash build_repos.sh sla113-standalone-export [dir]`
  - export the standalone SLA113 project into `dir` (default: `sla113_export`)
- `bash build_repos.sh sla113-standalone-export-and-build [dir]`
  - export the standalone SLA113 repo, validate it, and build the exported repo
- `bash build_repos.sh all`
  - install/build main backend, main frontend, and SLA113 backend + frontend

## Recommended command

For a one-shot standalone export and build:

```bash
bash build_repos.sh sla113-standalone-export-and-build
```

This will:
1. export `sla113_standalone/` into `sla113_export/`
2. validate the export structure
3. install backend dependencies in the exported repo
4. install frontend dependencies and build the exported frontend

## Notes

- If you pull the repo locally, use the same command from the repo root.
- If you run inside VS Code, use the integrated terminal in the workspace root.
- The command works the same whether the repo is local or opened in VS Code.

