#!/usr/bin/env bash
set -euo pipefail

# Build the dashboard
pixi run generate

# Deploy dashboard.html as index.html to gh-pages branch
git worktree add --orphan -B gh-pages /tmp/gh-pages-deploy 2>/dev/null || \
  git worktree add -B gh-pages /tmp/gh-pages-deploy origin/gh-pages 2>/dev/null || \
  git worktree add -B gh-pages /tmp/gh-pages-deploy

cp dashboard.html /tmp/gh-pages-deploy/index.html

(
  cd /tmp/gh-pages-deploy
  git add index.html
  git commit -m "deploy: $(date -u '+%Y-%m-%d %H:%M UTC')"
  git push origin gh-pages
)

git worktree remove /tmp/gh-pages-deploy
echo "Deployed to https://inwonakng.github.io/table-corpus-lineage/"
