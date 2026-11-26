#!/usr/bin/env bash
# secret_guard.sh — не даёт утечь приватным ключам и токенам в репозиторий.
#
# Проверяет:
#   1) в отслеживаемых файлах нет приватных SSH-ключей;
#   2) нет токенов GitHub (github_pat_, ghp_, gho_, ghu_, ghs_);
#   3) файлы приватных ключей не отслеживаются;
#   4) в индексе (то, что уйдёт в коммит) нет ни того, ни другого.
#
# Запуск:  bash tools/secret_guard.sh
# Возвращает 0 — чисто, 1 — найдена утечка.

set -uo pipefail

REPO_DIR="${REPO_DIR:-$(pwd)}"
cd "$REPO_DIR" || exit 1

SELF="tools/secret_guard.sh"
fail=0

# Шаблоны собраны из кусков, чтобы guard не находил сам себя.
PRIV="BEGIN ""OPENSSH PRIVATE KEY"
PRIV2="BEGIN ""RSA PRIVATE KEY"
PRIV3="BEGIN ""EC PRIVATE KEY"
TOK1="github_""pat_"
TOK2="gh""p_"

echo "=== Проверка на утечку секретов ==="

scan() {  # scan <glob-файлы> -> печатает подходящие файлы
  local list="$1"
  # shellcheck disable=SC2086
  git grep -l -I -E "$PRIV|$PRIV2|$PRIV3" -- $list 2>/dev/null \
    | grep -v "^${SELF}$" || true
}

# 1) приватные ключи в отслеживаемых файлах
hits=$(scan ".")
if [ -n "$hits" ]; then
  echo "✗ Приватный ключ в отслеживаемых файлах:"
  echo "$hits" | sed 's/^/    /'
  fail=1
else
  echo "✓ Приватных ключей в отслеживаемых файлах нет"
fi

# 2) токены GitHub в отслеживаемых файлах
tok=$(git grep -l -I -E "${TOK1}[A-Za-z0-9_]{20,}|${TOK2}[A-Za-z0-9]{20,}" \
      -- . 2>/dev/null | grep -v "^${SELF}$" || true)
if [ -n "$tok" ]; then
  echo "✗ Токен GitHub в отслеживаемых файлах:"
  echo "$tok" | sed 's/^/    /'
  fail=1
else
  echo "✓ Токенов GitHub в отслеживаемых файлах нет"
fi

# 3) файлы с ключами не отслеживаются
keyfiles=$(git ls-files | grep -E "(^|/)(id_ed25519|id_rsa|id_ecdsa|ssh-keys/)" || true)
if [ -n "$keyfiles" ]; then
  echo "✗ Отслеживаются файлы с ключами:"
  echo "$keyfiles" | sed 's/^/    /'
  fail=1
else
  echo "✓ Файлы с ключами не отслеживаются"
fi

# 4) то же самое по индексу — то, что уйдёт в коммит
staged=$(git diff --cached --name-only 2>/dev/null || true)
if [ -n "$staged" ]; then
  for f in $staged; do
    [ -f "$f" ] || continue
    if grep -qE "$PRIV|$PRIV2|$PRIV3" "$f" 2>/dev/null; then
      echo "✗ В индексе приватный ключ: $f"; fail=1
    fi
    if grep -qE "${TOK1}[A-Za-z0-9_]{20,}|${TOK2}[A-Za-z0-9]{20,}" "$f" 2>/dev/null; then
      echo "✗ В индексе токен GitHub: $f"; fail=1
    fi
  done
  echo "✓ Индекс проверен"
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "ИТОГ: чисто."
else
  echo "ИТОГ: НАЙДЕНА УТЕЧКА — не коммить это."
fi
exit "$fail"
