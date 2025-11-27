# GitHub Actions Workflows

This directory contains automated CI/CD workflows for Auto Cheatsheet.

## Workflows

### 1. Build and Release (`build-and-release.yml`)

Automatically builds and releases the application when triggered.

#### Trigger Methods

**A. Tag-based Release (Recommended)**
```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0
```

**B. Manual Release**
1. Go to Actions tab in GitHub
2. Select "Build and Release" workflow
3. Click "Run workflow"
4. Enter version number (e.g., `1.0.0`)
5. Optionally mark as pre-release
6. Click "Run workflow"

#### What It Does

1. ✅ Sets up Python 3.11 and dependencies
2. ✅ Installs MinGW compiler
3. ✅ Builds with Nuitka (optimized)
4. ✅ Creates release package with:
   - `AutoCheatsheet.exe`
   - `log/` directory
   - `src/` directory
   - `README.txt`
5. ✅ Generates SHA256 checksum
6. ✅ Creates GitHub release with artifacts
7. ✅ Uploads build artifacts (30-day retention)

### 2. Test Build (`test-build.yml`)

Runs on pull requests and pushes to main/develop branches.

#### What It Does

1. ✅ Validates code with Ruff linter
2. ✅ Tests build process
3. ✅ Verifies package structure
4. ✅ Uploads test artifacts (7-day retention)

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `v1.0.0` - Major release
- `v1.1.0` - Minor release (new features)
- `v1.0.1` - Patch release (bug fixes)
- `v1.0.0-beta.1` - Pre-release

## Release Process

### Standard Release

```bash
# 1. Update version in code if needed
# 2. Commit changes
git add .
git commit -m "Release v1.0.0"

# 3. Create and push tag
git tag v1.0.0
git push origin main
git push origin v1.0.0

# 4. Workflow automatically creates release
```

### Pre-release

```bash
# Use manual workflow dispatch
# Mark "pre-release" checkbox
# Or use pre-release tag format
git tag v1.0.0-beta.1
git push origin v1.0.0-beta.1
```

## Troubleshooting

### Build Fails

1. Check Python dependencies in `requirements.txt`
2. Verify Nuitka build script works locally
3. Check workflow logs in Actions tab

### Release Not Created

1. Ensure tag follows `v*.*.*` format
2. Check `GITHUB_TOKEN` permissions
3. Verify workflow file syntax

### Artifacts Not Uploaded

1. Check file paths in workflow
2. Verify build output location
3. Check artifact retention settings

## Local Testing

Test the build process locally before pushing:

```bash
# Install dependencies
pip install -r requirements.txt
pip install nuitka ordered-set zstandard pillow

# Run build
python script/build_nuitka.py

# Verify output
ls build/app.exe
```

## Workflow Permissions

Required GitHub token permissions:
- ✅ `contents: write` - Create releases
- ✅ `actions: read` - Read workflow status

These are automatically provided by `GITHUB_TOKEN`.