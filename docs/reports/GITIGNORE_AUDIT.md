# Gitignore Audit

Date: 2026-05-27

## Repository Structure Reviewed

The repository contains:

- Root project documentation, PRD/specification files, audit reports, and planning reports.
- `backend/`: FastAPI backend source, migrations, tests, local SQLite database files, virtual environments, cache folders, and generated carousel output.
- `frontend/`: Next.js source, package manifests, build/cache output, TypeScript build info, and `node_modules`.
- Local generated artifacts including `.pytest_cache/`, `dev.db`, and temporary test files.

## Rules Added

### Secrets and Local Environments

Ignored:

- `.env`
- `*/.env`
- `**/.env`
- `.env.local`
- `*/.env.local`
- `**/.env.local`
- `.env.production`
- `*/.env.production`
- `**/.env.production`
- `.env.development`
- `*/.env.development`
- `**/.env.development`

Reason: prevents local secrets, Supabase keys, API keys, and deployment-specific configuration from entering Git.

Explicitly allowed:

- `.env.example`
- `*/.env.example`
- `**/.env.example`

Reason: environment templates are documentation and must remain trackable.

### Python Artifacts

Ignored:

- `__pycache__/`
- `**/__pycache__/`
- `*.pyc`
- `*.pyo`
- `*.pyd`
- `*.py[cod]`
- `*$py.class`
- `.pytest_cache/`
- `**/.pytest_cache/`
- `.mypy_cache/`
- `**/.mypy_cache/`
- `.ruff_cache/`
- `**/.ruff_cache/`
- `.coverage`
- `**/.coverage`
- `htmlcov/`
- `**/htmlcov/`

Reason: excludes Python bytecode, test caches, type/lint caches, and coverage output.

### Python Virtual Environments

Ignored:

- `venv/`
- `.venv/`
- `*/venv/`
- `*/.venv/`
- `**/venv/`
- `**/.venv/`
- `backend/venv_py311/`

Reason: virtual environments are machine-local dependency installs and should be recreated from requirements files.

### Python Build Output

Ignored:

- `build/`
- `dist/`
- `**/build/`
- `**/dist/`
- `*.egg-info/`
- `**/*.egg-info/`

Reason: excludes generated package/build artifacts while keeping source code trackable.

### Databases and Local Runtime State

Ignored:

- `*.db`
- `dev.db`
- `backend/dev.db`

Reason: local SQLite databases are runtime artifacts and may contain local test data.

### Node and Next.js Artifacts

Ignored:

- `node_modules/`
- `**/node_modules/`
- `.next/`
- `**/.next/`
- `out/`
- `**/out/`
- `dist/`
- `**/dist/`
- `build/`
- `**/build/`
- `*.tsbuildinfo`

Reason: excludes installed dependencies, Next.js build output, static export output, compiled bundles, and TypeScript incremental build metadata.

### Logs, Generated Output, and Temporary Files

Ignored:

- `*.log`
- `npm-debug.log*`
- `yarn-debug.log*`
- `yarn-error.log*`
- `pnpm-debug.log*`
- `backend/carousel_output/`
- `tmp/`
- `temp/`
- `**/tmp/`
- `**/temp/`

Reason: excludes logs, generated carousel image output, and temporary local work directories.

### IDE and OS Files

Ignored:

- `.vscode/`
- `**/.vscode/`
- `.idea/`
- `**/.idea/`
- `.DS_Store`
- `**/.DS_Store`
- `Thumbs.db`
- `**/Thumbs.db`

Reason: excludes editor configuration and OS metadata that are not part of the application.

## Confirmed Not Ignored

These files and directories are intentionally not ignored:

- `.env.example`
- `backend/.env.example`
- `frontend/.env.example`
- `PRD_Content_Engine.txt`
- `ARCHITECTURE_STACK.md`
- `PROMPT_TEMPLATES.md`
- Audit and sprint reports, including `*_REPORT.md` and `FINAL_*_AUDIT.md`
- `backend/migrations/`
- Backend source code under `backend/app/`, `backend/services/`, `backend/models/`, and related source directories
- Frontend source code under `frontend/components/`, `frontend/lib/`, `frontend/pages/`, `frontend/styles/`, and configuration files

## Verification Results

Executed from the repository root.

```powershell
git check-ignore -v backend/.env
```

Result: `backend/.env` is ignored by `.gitignore:6:**/.env`.

```powershell
git check-ignore -v frontend/.env
```

Result: `frontend/.env` is ignored by `.gitignore:6:**/.env`.

```powershell
git check-ignore -v backend/.env.example
```

Result: `backend/.env.example` matches the explicit allow rule `.gitignore:20:!**/.env.example`, so it remains trackable.

```powershell
git check-ignore -v frontend/.env.example
```

Result: `frontend/.env.example` matches the explicit allow rule `.gitignore:20:!**/.env.example`, so it remains trackable.

Additional sampled generated artifacts were also verified:

- `dev.db` is ignored.
- `backend/dev.db` is ignored.
- `frontend/node_modules/` is ignored.
- `frontend/.next/` is ignored.
- `backend/venv_py311/` is ignored.
- `.pytest_cache/` is ignored.
