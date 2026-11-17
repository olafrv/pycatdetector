# CLAUDE.md

## Release Process

A release is just a git tag. `make github.release` chains: black format
check → git-clean check → docker build → full test suite → create and push the
annotated tag `<VERSION>`. No GitHub Release is created and no Docker image is
pushed to any registry (ghcr.io was dropped to stay within free-account package
limits); each host builds locally. Release notes live in `CHANGELOG.md`.

To cut a release:
1. Bump `VERSION` in `METADATA` and add its section to `CHANGELOG.md`.
2. Commit and push to `main`.
3. Run `make github.release`.

### Authentication

No env vars or API tokens are used by the Makefile; the only GitHub access
is `git push` (of `main` and the tag), authenticated by the git credential
helper. The token needs the `repo` scope.

If a push fails with a 403, the stored credential is likely
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

`docker-compose.yaml` runs the `pycatdetector` service from the local image
`pycatdetector:latest`. Use the Makefile targets rather than raw
`docker compose` commands:

- `make docker.start` / `make docker.restart` — builds the image from the
  current checkout (`docker.build` tags `:<VERSION>` and `:latest`), then
  recreates the container. Nothing is pulled or pushed.
- The container runs as uid/gid 1000 (`user:` in compose and `USER` in the
  Dockerfile) with all capabilities dropped; the mounted `config.yaml`,
  `logs/`, `videos/` and `models/` must be owned by uid 1000.

## Credential Hygiene

Never embed credentials in a git remote URL
(`https://user:pass@host/...`) — it's exposed in plaintext by `git remote -v`
and anything that echoes it back. Use the git credential store
(`credential.helper=store`) instead.
