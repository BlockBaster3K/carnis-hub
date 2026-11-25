# Handshake — Звук

- Прочитал: `00-board/ROADMAP_sound.md` + `00-board/README.md` + `00-board/STATUS.md`
- Коммит, на котором читал: `3b828411d39bde38fbf24d3e030619a4bb8e5ec6`
- Задача понята: (1) пересобрать `03-sound/transfer/SHA256SUMS_delta22.txt` по фактическому состоянию диска — там три расхождения: мёртвое имя `block/pulsing_heart_beat.ogg` (рабочее — `block/heart_pulse.ogg`, хеш тот же) и два неверных SHA у пары `bone_scythe_*`; (2) подготовить **предложение** по `bone_scythe` к 3.6.0 (события, пути, stream, без pitch/volume, плюс требование к Кодеру о захардкоженном `OSSIFIED_SCYTHE_*` в `ScytheItem`/`CombatItemEvents`) — в 3.5.3 **не сдавать**, `sounds.json` не править.
- Готов приступить: да
- Вопросы к Архитектору: нет

## Замечания по инфраструктуре (не правлю, зона не моя)

1. `tools/sound_check.py` и `tools/sound_metrics.py` по умолчанию ищут банк в `/home/user/hub5/03-sound` — при другом каталоге `sound_check.py` **молча печатает «все проверки пройдены»** на пустом банке (0 файлов, «файла нет»), а `sound_metrics.py` падает с `System error` (libsndfile не открывает OGG). Проверки выполнил напрямую: `sound_check.py "/home/user/hubwork/03-sound"` → 159/159 совпало; метрики — своим декодером (ffmpeg), результаты в отчёте.
2. Рекомендация (в отчёт, решение за владельцем): научить `sound_check.py` падать, если файлов 0, а ожидалось больше; путь к банку брать от расположения скрипта, а не из константы.
