# Publishing Hawkeyes

Users install with a shell command. They do **not** need Python or pip.

```bash
curl -fsSL https://YOUR-INSTALL-HOST/install.sh | sh
```

Your GitHub repo is for development only. Host `install.sh` and binaries somewhere users can reach without cloning the repo.

---

## How it works

1. You build a **standalone `hawk` binary** (Python bundled inside via PyInstaller).
2. You upload `install.sh` + binaries to a download host.
3. Users run `curl ... | sh` — the script downloads the binary to `~/.local/bin/hawk`.

---

## Release workflow

### 1. Push code to `main`

```bash
git add .
git commit -m "Release Hawkeyes v1.0.0"
git push origin main
```

### 2. Create a version tag (builds binaries automatically)

```bash
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions (`.github/workflows/release.yml`) builds:

- `hawk-linux-x86_64`
- `hawk-linux-aarch64`
- `install.sh`

…and attaches them to the GitHub Release.

### 3. Build locally (optional)

```bash
chmod +x scripts/build_binary.sh
./scripts/build_binary.sh
# Output: dist/hawk-linux-x86_64 (or aarch64)
```

---

## Host install files (hide GitHub from users)

Pick one option and point users only at that URL.

### Option A — Custom domain (recommended)

Upload to any static host (Cloudflare Pages, Netlify, S3, VPS):

```
https://get.yourdomain.com/install.sh
https://get.yourdomain.com/releases/v1.0.0/hawk-linux-x86_64
https://get.yourdomain.com/releases/v1.0.0/hawk-linux-aarch64
```

Set the download base URL when users install:

```bash
curl -fsSL https://get.yourdomain.com/install.sh | \
  HAWKEYES_BASE_URL=https://get.yourdomain.com/releases/v1.0.0 sh
```

Or edit `install.sh` and set `HAWKEYES_BASE_URL` as the default before uploading.

**What you share publicly:**

```bash
curl -fsSL https://get.yourdomain.com/install.sh | sh
```

### Option B — CDN mirror of release assets

After creating a GitHub Release, mirror files to your CDN. Users never see GitHub.

### Option C — Temporary: GitHub Releases (internal testing only)

```bash
curl -fsSL https://github.com/green-cyber-city/hawkeyes/releases/download/v1.0.0/install.sh | sh
```

Use this while testing. Switch to Option A before promoting publicly.

---

## Update `install.sh` for each release

Before uploading, bump the version in `install.sh`:

```sh
VERSION="${HAWKEYES_VERSION:-1.0.0}"
```

Also bump `hawkeyes/__init__.py` and `pyproject.toml` if you still publish metadata there.

---

## Test the installer

```bash
# Local test without downloading
HAWKEYES_BASE_URL="file://$(pwd)/dist" \
HAWKEYES_INSTALL_DIR="/tmp/hawkeyes-test/bin" \
sh install.sh

/tmp/hawkeyes-test/bin/hawk --version
/tmp/hawkeyes-test/bin/hawk target 127.0.0.1 --ports "80"
```

For a real remote test, upload assets first, then run the public curl command.

---

## Optional: PyPI (not required)

If you also want `pip install hawkeyes`, see the PyPI section in an older revision or run:

```bash
python -m build
python -m twine upload dist/*
```

The shell installer is the primary path — no pip for users.
