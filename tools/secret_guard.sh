#!/usr/bin/env bash
# secret_guard.sh — не даёт утечь приватным ключам и токенам в репозиторий.
#
# Проверяет:
#   1) в индексе/рабочем дереве нет приватных SSH-ключей (BEGIN OPENSSH PRIVATE KEY);
#   2) нет токенов GitHub (github_pat_, ghp_, gho_, ghu_, ghs_);
#   3) файлы приватных ключей не добавлены в индекс.
#
# Запуск:  bash tools/secret_guard.sh
# Возвращает 0 — чисто, 1 — найдена утечка.

set -uo pipefail

REPO_DIR="${REPO_DIR:-$(pwd)}"
cd "$REPO_DIR" || exit 1

fail=0

echo "=== Проверка на утечку секретов ==="

# 1) приватные ключи среди отслеживаемых и готовых к добавлению файлов
hits=$(git grep -l -I -E "BEGIN OPENSSH PRIVATE KEY|BEGIN RSA PRIVATE KEY|BEGIN OPENSSH" \
        -- . 2>/dev/null || true)
if [ -n "$hits" ]; then
  echo "✗ Приватный ключ в отслеживаемых файлах:"
  echo "$hits" | sed 's/^/    /'
  fail=1
else
  echo "✓ Приватных ключей в отслеживаемых файлах нет"
fi

# 2) то же по индексу (то, что уйдёт в коммит)
staged=$(git diff --cached --name-only 2>/dev/null || true)
for f in $staged; do
  [ -f "$f" ] || continue
  if grep -qE "BEGIN (OPENSSH|RSA|EC) PRIVATE KEY" "$f" 2>/dev/null; then
    echo "✗ В индексе приватный ключ: $f"; fail=1
  fi
  if grep -qE "github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}" "$f" 2>/dev/null; then
    echo "✗ В индексе токен GitHub: $f"; fail=1
  fi
done
[ "$fail" -eq 0 ] && echo "✓ В индексе секретов нет"

# 3) токены в отслеживаемых файлах
tok=$(git grep -l -I -E "github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,}" \
      -- . 2>/dev/null || true)
if [ -n "$tok" ]; then
  echo "✗ Токен GitHub в отслеживаемых файлах:"
  echo "$tok" | sed 's/^/    /'
  fail=1
else
  echo "✓ Токенов GitHub в отслеживаемых файлах нет"
fi

# 4) файлы-ключи не отслеживаются
keyfiles=$(git ls-files | grep -E "(^|/)(id_ed25519|id_rsa|id_ecdsa|ssh-keys/)" || true)
if [ -n "$keyfiles" ]; then
  echo "✗ Отслеживаются файлы с ключами:"
  echo "$keyfiles" | sed 's/^/    /'
  fail=1
else
  echo "✓ Файлы с ключами не отслеживаются"
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "ИТОГ: чисто."
else
  echo "ИТОГ: НАЙДЕНА УТЕЧКА — не коммить это."
fi
exit "$fail"
