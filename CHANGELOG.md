# Changelog

## [Unreleased]

### Changed
- Migrated frontend from Next.js to React + Vite SPA
- Removed Next.js API proxy routes (`/api/chat`, `/api/security`) — frontend now calls FastAPI backend directly
- Added red accent Cloudscape theme (portfolio standard)
- Dark mode now defaults to on, persisted via `scaffold-ai-darkMode` localStorage key
- Updated env vars from `NEXT_PUBLIC_*` to `VITE_*`
- Added 95% coverage thresholds to `vitest.config.ts`
- Added `CLAUDE.md`, `RUNBOOK.md`, `config.json` for PSP compatibility
