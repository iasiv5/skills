#!/usr/bin/env bash
# release.sh — 发版关键链（管道吞码免疫版；retro R1）。
# 用法: scripts/release.sh vX.Y.Z
# 链条：版本三处一致性 → 干净树 → build+test → 远端快进预检 → push main → tag → push tag。
# 退出码即真相：任一步失败立即中止（失败路径上没有展示用管道）。
set -euo pipefail

TAG_NAME="${1:?usage: release.sh vX.Y.Z}"
cd "$(dirname "$0")/.."   # dsh-plugin/

PKG_VERSION=$(node -p "require('./package.json').version")
LOCK_VERSION=$(node -p "require('./package-lock.json').version")
[ "$PKG_VERSION" = "$LOCK_VERSION" ] || { echo "✗ package.json($PKG_VERSION) != package-lock.json($LOCK_VERSION)"; exit 1; }
[ "${TAG_NAME#v}" = "$PKG_VERSION" ] || { echo "✗ tag($TAG_NAME) != package.json($PKG_VERSION)"; exit 1; }

[ -z "$(git status --porcelain)" ] || { echo "✗ 工作树不干净，先提交"; exit 1; }

npm run build > /dev/null
npm test > /dev/null
echo "✓ build + gates + tests 全绿"

git fetch origin main --quiet
git merge-base --is-ancestor origin/main HEAD || {
  echo "✗ 本地 main 与远端分岔——先整合再发版（参考 plan 勘误 G）"
  exit 1
}

git push origin main
git tag "$TAG_NAME"
git push origin "$TAG_NAME"

echo "✓ $TAG_NAME 已推送。轮询 npm 转正（know-how 018：绿 ≠ 已上架）："
echo "  npm view @iasiv5/dsh-skills version --registry https://registry.npmjs.org"
