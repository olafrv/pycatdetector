# CLAUDE.md

## Release Process

Releases are cut via `make github.release`, which chains: black format check →
git-clean check → docker build → full test suite → docker push (ghcr.io) →
git tag → GitHub release creation.

To cut a release:
1. Bump `VERSION` in `METADATA`.
2. Commit and push to `main`.
3. Run `make github.release`.

### Authentication

No env vars needed. `GITHUB_USER` is derived from the `origin` remote URL;
the GitHub token is read from the git credential store (`~/.git-credentials`)
at the moment it's needed (ghcr.io login, GitHub Releases API) — never
exported in plaintext, never echoed. The token needs `repo` +
`write:packages` scopes (classic PAT — fine-grained PATs don't reliably
support GHCR pushes).

If push/release auth fails with a 403, the stored credential is likely
stale/rotated:
```
printf 'protocol=https\nhost=github.com\n\n' | git credential reject
```
Then run `git push` once — it'll prompt for a fresh username/token and
cache it.

## Local Dev Setup

`install.base` is a **read-only prerequisite check**, not an installer — it
verifies python3/venv/pip/tkinter/gcc/ffmpeg/jq are present and fails with
an install command if not, rather than silently running `sudo apt install`.
`test`, `run`, `check-config`, `coverage*`, and `package.outdated` all
depend on `install.venv`/`install.dev`, so they build the venv automatically
on first use.

## Docker

`docker-compose.yaml` runs the `pycatdetector` service from
`ghcr.io/olafrv/pycatdetector:latest`. After a release or a local
`requirements.txt` change, pick it up with:
```
docker compose build && docker compose up -d
```

## Credential Hygiene

Never embed credentials in a git remote URL
(`https://user:pass@host/...`) — it's exposed in plaintext by `git remote -v`
and anything that echoes it back. Use the git credential store
(`credential.helper=store`) instead.
