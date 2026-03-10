#!/usr/bin/env bash
# update.sh — 从 GitHub 更新 skills（覆盖旧版本，旧版本备份到 .backup/<skill>/）
# 用法:
#   ./update.sh              # 更新 .skills.json 中所有 skills
#   ./update.sh docx pdf     # 只更新指定的 skills
# 注意: skip 列表中的 skill 不参与更新

set -euo pipefail

SKILLS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_BASE=$(mktemp -d)
trap 'rm -rf "$TMP_BASE"' EXIT

command -v python3 >/dev/null 2>&1 || { echo "错误: 需要 python3"; exit 1; }
command -v git     >/dev/null 2>&1 || { echo "错误: 需要 git";     exit 1; }

log()  { printf '\033[34m▶\033[0m %s\n' "$*"; }
ok()   { printf '\033[32m✓ 已更新\033[0m\n'; }
warn() { printf '    \033[33m⊘\033[0m %s\n' "$*"; }
fail() { printf '\033[31m✗ %s\033[0m\n' "$*" >&2; }

FILTER="${*:-}"

# 克隆仓库到临时目录（同一仓库只克隆一次）
get_clone() {
  local repo="$1"
  local dest="$TMP_BASE/${repo//\//__}"
  if [[ ! -d "$dest" ]]; then
    git clone --depth=1 --quiet "https://github.com/$repo.git" "$dest"
  fi
  printf '%s' "$dest"
}

# 从 .skills.json 读取条目列表（排除 skip，支持按名称过滤）
read_skills() {
  python3 -c "
import json, os, sys
data = json.load(open(os.path.join('$SKILLS_DIR', '.skills.json')))
skips = set(data.get('skip', []))
f = set(sys.argv[1].split()) if sys.argv[1].strip() else None
for name, cfg in data['skills'].items():
    if name in skips:
        continue
    if f and name not in f:
        continue
    print(name + '\t' + cfg['repo'] + '\t' + cfg.get('subdir', ''))
" "$FILTER"
}

[[ -n "$FILTER" ]] && log "更新 skills: $FILTER" || log "更新所有 skills"
echo

while IFS=$'\t' read -r name repo subdir; do
  printf '  %s\n' "$name"
  dest="$SKILLS_DIR/$name"

  printf '    克隆 https://github.com/%s ... ' "$repo"
  repo_dir=$(get_clone "$repo") || { fail "克隆失败: $repo"; continue; }

  # 备份旧版本到 .backup/<name>/（Claude Code 不会扫描隐藏目录）
  BACKUP_DIR="$SKILLS_DIR/.backup"
  mkdir -p "$BACKUP_DIR"
  if [[ -d "$dest" ]]; then
    rm -rf "$BACKUP_DIR/$name"
    cp -r "$dest" "$BACKUP_DIR/$name"
    rm -rf "$dest"
  fi

  if [[ -n "$subdir" ]]; then
    src="$repo_dir/$subdir"
    if [[ ! -d "$src" ]]; then
      fail "子目录不存在: $subdir，恢复备份"
      [[ -d "$BACKUP_DIR/$name" ]] && cp -r "$BACKUP_DIR/$name" "$dest"
      continue
    fi
    if cp -r "$src" "$dest"; then ok; else
      fail "复制失败，恢复备份"
      [[ -d "$BACKUP_DIR/$name" ]] && cp -r "$BACKUP_DIR/$name" "$dest"
    fi
  else
    if cp -r "$repo_dir" "$dest" && rm -rf "$dest/.git"; then ok; else
      fail "复制失败，恢复备份"
      [[ -d "$BACKUP_DIR/$name" ]] && cp -r "$BACKUP_DIR/$name" "$dest"
    fi
  fi

done < <(read_skills)

echo
log "完成！如需回滚某个 skill: rm -rf <skill> && cp -r .backup/<skill> <skill>"
echo

# 如果在 git 仓库中，显示变更提示
if git -C "$SKILLS_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  changed=$(git -C "$SKILLS_DIR" status --short | grep -v '^\?\? \.backup/' | grep -v '^\?\? 说明' || true)
  if [[ -n "$changed" ]]; then
    printf '\033[33m─────────────────────────────────────────\033[0m\n'
    printf '\033[33m  有变更尚未提交到 GitHub：\033[0m\n'
    printf '%s\n' "$changed" | sed 's/^/    /'
    printf '\033[33m─────────────────────────────────────────\033[0m\n'
    printf '  git -C "%s" add -A && git -C "%s" commit -m "update skills" && git -C "%s" push\n' \
      "$SKILLS_DIR" "$SKILLS_DIR" "$SKILLS_DIR"
  else
    printf '  已是最新，无需提交。\n'
  fi
fi
