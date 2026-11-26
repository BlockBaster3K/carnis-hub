#!/usr/bin/env bash
# verify_ssh_roles.sh — проверка SSH-доступа каждой роли к carnis-hub.
#
# Для каждой роли проверяет:
#   1) ssh -T git@github.com      (аутентификация)
#   2) clone --depth 1            (получение репозитория)
#   3) fetch origin <branch>      (обновление)
#   4) push --dry-run             (право записи)
#
# Временные клоны удаляются в конце. Приватные ключи не печатаются и не копируются
# в репозиторий — используются только по назначению (-i <key> -o IdentitiesOnly=yes).
#
# Запуск:  bash /home/user/tools/verify_ssh_roles.sh

set -uo pipefail

REPO_SLUG="BlockBaster3K/carnis-hub"
SSH_REMOTE="git@github.com:${REPO_SLUG}.git"
BRANCH="arena/d474d740-carnis-hub"
KEY_DIR="${KEY_DIR:-/home/user/ssh-keys}"
ROLES=(architect reviewer coder artist sound)
TMP_ROOT="$(mktemp -d /tmp/sshverify.XXXXXX)"

pass=0; fail=0

cleanup() { rm -rf "$TMP_ROOT"; }
trap cleanup EXIT

echo "=== Проверка SSH-ролей для $REPO_SLUG ==="
echo "Ветка: $BRANCH"
echo

for role in "${ROLES[@]}"; do
  key="${KEY_DIR}/${role}"
  echo "--- Роль: $role"

  if [ ! -f "$key" ]; then
    echo "    ✗ нет приватного ключа: $key"; fail=$((fail+1)); echo; continue
  fi
  mode=$(stat -c '%a' "$key")
  if [ "$mode" != "600" ]; then
    echo "    ! права на ключе $mode (нужно 600) — исправляю"
    chmod 600 "$key"
  fi

  # 1) аутентификация
  auth=$(ssh -i "$key" -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new \
              -o ConnectTimeout=15 -T git@github.com 2>&1)
  if echo "$auth" | grep -q "successfully authenticated"; then
    echo "    ✓ SSH-аутентификация"
  else
    echo "    ✗ SSH-аутентификация не прошла:"
    echo "$auth" | sed 's/^/        /'
    echo "      → deploy key для роли '$role' не зарегистрирован в GitHub"
    fail=$((fail+1)); echo; continue
  fi

  work="$TMP_ROOT/$role"
  # 2) clone
  if git clone --depth 1 --branch "$BRANCH" "$SSH_REMOTE" "$work" >/dev/null 2>&1; then
    echo "    ✓ clone"
  else
    echo "    ✗ clone не удался"; fail=$((fail+1)); echo; continue
  fi

  # 3) fetch
  if git -C "$work" fetch origin "$BRANCH" >/dev/null 2>&1 \
     || git -C "$work" fetch --unshallow origin >/dev/null 2>&1; then
    echo "    ✓ fetch"
  else
    echo "    ✗ fetch не удался"; fail=$((fail+1)); echo; continue
  fi

  # 4) push (dry-run — проверка права записи без создания коммитов)
  git -C "$work" config user.name  "verify-$role"
  git -C "$work" config user.email "verify-$role@arena.local"
  if GIT_SSH_COMMAND="ssh -i $key -o IdentitiesOnly=yes" \
       git -C "$work" push --dry-run origin "HEAD:refs/heads/$BRANCH" >/dev/null 2>&1; then
    echo "    ✓ push (dry-run) — право записи есть"
    pass=$((pass+1))
  else
    echo "    ✗ push отклонён — deploy key зарегистрирован без права записи (read_only=true)"
    fail=$((fail+1))
  fi
  echo
done

echo "=== Итог: успешно $pass, с ошибкой $fail ==="
[ "$fail" -eq 0 ] || exit 1
