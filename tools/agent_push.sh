#!/usr/bin/env bash
# agent_push.sh — безопасная отправка изменений в репозиторий carnis-hub.
#
# Использование:
#   export GITHUB_TOKEN=ghp_xxx          # fine-grained PAT, repo-scoped
#   bash agent_push.sh <ветка> "<сообщение коммита>" [путь ...]
#
# Что гарантирует скрипт:
#   * токен НЕ попадает в argv (нет процесса в ps), в .git/config и в reflog —
#     учётные данные отдаёт credential-helper из переменной окружения;
#   * при «non-fast-forward» выполняется pull --rebase --autostash и повтор push
#     (до 3 попыток) — это снимает главную боль при параллельной работе нескольких агентов;
#   * печатается список файлов коммита и предупреждение, если затронуты
#     каталоги, зарезервированные за Интегратором;
#   * в коммит попадает только то, что указано аргументами (по умолчанию — ничего).
#
# Требования к токену: fine-grained PAT, репозиторий BlockBaster3K/carnis-hub,
# разрешения Contents: Read and write (+ Actions: Read, если нужны логи CI).

set -euo pipefail

REPO_SLUG="BlockBaster3K/carnis-hub"
REPO_DIR="${REPO_DIR:-/home/user/hub5}"

# Каталоги, за которые отвечает Интегратор. Агент может их трогать, но
# предупреждение печатается обязательно.
INTEGRATOR_OWNED="^(STATUS\.md|VERIFICATIONS/|06-build/|07-project/|\.github/|README\.md)"

usage() {
  cat >&2 <<'EOF'
Использование:
  export GITHUB_TOKEN=ghp_xxx
  bash agent_push.sh <ветка> "<сообщение коммита>" [путь ...]

Пример:
  bash agent_push.sh arena/d474d740-carnis-hub \
    "[coder] 3.5.3: пакет с новой механикой" \
    01-coder/3.5.3
EOF
  exit 2
}

[ $# -ge 2 ] || usage
BRANCH="$1"; shift
MESSAGE="$1"; shift
PATHS=("$@")

if [ -z "${GITHUB_TOKEN:-}" ]; then
  echo "ОШИБКА: не задана переменная GITHUB_TOKEN (fine-grained PAT)." >&2
  echo "       export GITHUB_TOKEN=ghp_..." >&2
  exit 1
fi

if [ ! -d "$REPO_DIR/.git" ]; then
  echo "ОШИБКА: $REPO_DIR не является git-репозиторием." >&2
  exit 1
fi

cd "$REPO_DIR"

# --- проверка состояния ---
if [ -n "$(git status --porcelain)" ] && [ ${#PATHS[@]} -eq 0 ]; then
  echo "ОШИБКА: есть незакоммиченные изменения, но пути не указаны." >&2
  git status --short >&2
  exit 1
fi

if [ ${#PATHS[@]} -gt 0 ]; then
  for p in "${PATHS[@]}"; do
    if [ ! -e "$p" ]; then
      echo "ОШИБКА: путь не найден: $p" >&2
      exit 1
    fi
  done
  git add -- "${PATHS[@]}"
fi

if git diff --cached --quiet; then
  echo "Нет изменений для коммита — нечего отправлять."
  exit 0
fi

echo "=== Файлы коммита ==="
git diff --cached --name-status
echo

WARN="$(git diff --cached --name-only | grep -E "$INTEGRATOR_OWNED" || true)"
if [ -n "$WARN" ]; then
  echo "⚠️  Внимание: затрагиваются зоны Интегратора:"
  echo "$WARN" | sed 's/^/    /'
  echo "   (обычно это нормально для отчётов, но не для правки 06-build/ и STATUS.md)"
  echo
fi

# --- коммит ---
git -c user.name="${GIT_AUTHOR_NAME:-Arena Agent}" \
    -c user.email="${GIT_AUTHOR_EMAIL:-agent@arena.local}" \
    commit -q -m "$MESSAGE"

COMMIT="$(git rev-parse --short HEAD)"
echo "Коммит: $COMMIT"

# --- push с повтором при non-fast-forward ---
# Учётные данные отдаёт helper из переменной окружения: токен не попадает ни в argv,
# ни в .git/config, ни в reflog.
CRED_HELPER='!f() { echo username=x-access-token; echo password=$GITHUB_TOKEN; }; f'
REMOTE="https://github.com/$REPO_SLUG.git"

git fetch -q origin "$BRANCH" 2>/dev/null || true

for attempt in 1 2 3; do
  echo "--- push, попытка $attempt/3 → $BRANCH"
  if git -c credential.helper="$CRED_HELPER" push "$REMOTE" "HEAD:refs/heads/$BRANCH" 2>&1 | sed 's/^/    /'; then
    echo
    echo "✅ Отправлено: $COMMIT → $BRANCH"
    echo "   GitHub Actions запустится сам, если пути задевают 01-coder/ 03-sound/ 04-artist/ 06-build/overlay.txt"
    exit 0
  fi
  echo "    push не прошёл, перебазируюсь на актуальный origin/$BRANCH…"
  git pull -q --rebase --autostash origin "$BRANCH" || {
    echo "ОШИБКА: не удалось перебазироваться — разрешите конфликт вручную и повторите." >&2
    exit 1
  }
done

echo "ОШИБКА: push не удался после 3 попыток." >&2
exit 1
