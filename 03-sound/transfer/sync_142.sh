#!/usr/bin/env bash
# CARNIS · синхронизация банка в проект (Волна 21, указ координатора)
# Правило: копировать ВСЁ, кроме архива *_w1516 и block/heart_pulse.ogg (он остаётся в проекте). УДАЛЯТЬ НИЧЕГО.
set -euo pipefail

SRC="${1:?укажите источник: <воркспейс>/assets/carnis/sounds}"
DST="${2:?укажите цель: <проект>/src/main/resources/assets/carnis/sounds}"

[ -d "$SRC" ] || { echo "источник не найден: $SRC"; exit 1; }
mkdir -p "$DST"

copied=0
while IFS= read -r -d "" f; do
  rel="${f#$SRC/}"
  case "$rel" in
    *_w1516.ogg)      continue ;;   # 14 архивных — не копировать
    block/heart_pulse.ogg) continue ;; # остаётся проектной версией 0.62 с / 24 кГц
  esac
  mkdir -p "$DST/$(dirname "$rel")"
  cp -f "$f" "$DST/$rel"
  copied=$((copied+1))
done < <(find "$SRC" -type f -name "*.ogg" -print0)

echo "скопировано из банка: $copied (ожидается 142)"
hp=0
[ -f "$DST/block/heart_pulse.ogg" ] && hp=1
echo "heart_pulse на месте (проектная версия, не перезаписывается): $hp (ожидается 1)"
legacy=0
for l in entity/flesh_amalgam_death.ogg entity/flesh_amalgam_hurt.ogg; do
  [ -f "$DST/$l" ] && legacy=$((legacy+1))
done
echo "legacy на месте (не трогать до 3.5.2): $legacy (ожидается 2)"

total=$(find "$DST" -type f -name "*.ogg" | wc -l)
echo "всего .ogg в проекте: $total (ожидается 145 = 142 банковских + 1 heart_pulse + 2 legacy)"
[ "$copied" -eq 142 ] || { echo "ОШИБКА: скопировано $copied, а не 142"; exit 2; }
[ "$hp" -eq 1 ]     || { echo "ОШИБКА: в проекте нет block/heart_pulse.ogg — сердца нет, проверить до копирования"; exit 3; }
[ "$legacy" -eq 2 ] || { echo "ОШИБКА: legacy $legacy из 2 — до 3.5.2 их удалять нельзя"; exit 4; }
[ "$total" -eq 145 ] || { echo "ОШИБКА: в проекте $total .ogg, а не 145"; exit 5; }
echo "OK"
