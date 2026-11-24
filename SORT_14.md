# SORT-14 — публикация в Releases. ⚠️ Решение не устраняет проблему

**Дата:** 2026-11-24
**Промпт:** v15 (`integrator_prompt_v15.md`, 7 501 Б, `9f3055c55ef59cea…`)
**Статус:** workflow заменён дословно. ⚠️ **Но основание для правки — фактически неверно, и это блокирует тест иначе, чем вы думаете.**

---

## 1. ⚠️ ГЛАВНОЕ: релизы GitHub лежат в том же Azure

Вы пишете: *«Релизные файлы лежат на `objects.githubusercontent.com` — проверил из песочницы, отвечает»*. **Проверил — не отвечает, и файл лежит не там.**

### 1.1. Что я измерил из песочницы

| Хост | Ответ |
|---|---|
| `github.com` | **200** |
| `codeload.github.com` | 301 |
| `objects.githubusercontent.com` | **000** |
| `release-assets.githubusercontent.com` | **000** |
| `raw.githubusercontent.com` | **000** |
| `productionresultssa12.blob.core.windows.net` | **000** |
| `releaseassetproduction.blob.core.windows.net` | **000** |

`objects.githubusercontent.com`: TLS-хендшейк обрывается — `OpenSSL SSL_connect: SSL_ERROR_SYSCALL`, ровно как с `blob.core.windows.net`. То есть из **моей** песочницы он недоступен так же, как артефакты.

### 1.2. Куда реально ведёт ссылка на релизный файл

Взял живой публичный релиз (`cli/cli` v2.40.0) и проследил редиректы:

```
https://github.com/cli/cli/releases/download/v2.40.0/gh_2.40.0_linux_amd64.tar.gz
  → 302 → objects.githubusercontent.com/github-production-release-asset-2e65be/...
          (подпись AWS4-HMAC — S3)
```

Реальный файл отдаётся и через `release-assets.githubusercontent.com`. Декодировал JWT из его query-строки:

```json
{"iss":"github.com",
 "aud":"release-assets.githubusercontent.com",
 "path":"releaseassetproduction.blob.core.windows.net"}
```

**Вот ключевое:** `path` = **`releaseassetproduction.blob.core.windows.net`**. Релизные файлы GitHub физически хранятся **в том же Azure Blob Storage**, что и артефакты прогонов — только другой аккаунт.

### 1.3. Что из этого следует

**Ваше решение не устраняет причину.** Если у заказчика блокируется/режется `*.blob.core.windows.net` в целом — скачивание релиза упрётся в тот же барьер (через `release-assets.githubusercontent.com` → `releaseassetproduction.blob.core.windows.net`).

**Честная оговорка:** это не доказательство провала у заказчика. Возможны варианты:

- у него режется **конкретный** аккаунт (`productionresultssa12…`), а не весь домен — тогда релиз пройдёт;
- блокируется по SNI/DDI-списку именно `release-assets.githubusercontent.com` — тогда нет;
- **VPN «не помогает»** — а вы пишете, что пробовали. Если exit-нода тоже не проходит, это скорее говорит о том, что дело **не в блокировке провайдера**, а в чём-то на стороне заказчика (антивирус, корпоративный прокси, hosts-файл, локальный фильтр). Стоит это проверить прежде, чем менять инфраструктуру.

**Проверить фактически может только заказчик** — нажав кнопку после этой правки. Я из песочницы могу утверждать только то, что измерил выше.

---

## 2. Workflow заменён — дословно

YAML извлечён из промпта программно, сверен побайтово.

| Параметр | v8 | **v15** |
|---|---:|---:|
| Байт | 2 525 | **3 791** |
| SHA-256 | `5f680812cbc3efb9…` | `4e37daad15305034…` |
| Строк | 75 | 97 |

**`diff` с текстом промпта = 0 различий** (3 791 = 3 791 Б).

### 2.1. YAML проверен парсером (PyYAML, в отдельном venv)

```
YAML валиден
name: build-jar
permissions: {'contents': 'write'}
inputs: ['package']
шаги: Checkout, Set up JDK 17, Set up Gradle, Resolve package,
      Unpack project package, Build, Report jar version,
      Publish release with jar, Upload jar
```

Всё на месте: `contents: write`, input `package`, шаг публикации между `Report` и `Upload`.

---

## 3. ⚠️ Workflow permissions — **проверить не смог**

Вы просили проверить Actions → General → Workflow permissions. **Все три эндпоинта вернули 403:**

| Эндпоинт | Ответ |
|---|---|
| `actions/permissions` | `Resource not accessible by integration` (403) |
| `actions/permissions/workflow` | 403 |
| `actions/permissions/selected-actions` | 403 |

Мой токен имеет `admin: true` на репозитории, но эти настройки через API закрыты (нужен другой scope). **Ничего не правил.**

### 3.1. Что это значит

Работает или нет — станет известно **только на первом прогоне**. Если в нём `Publish release` упадёт с **403**, причина — «Read repository contents…» в настройках. Это настройка заказчика, не моя и не workflow.

**Как заказчику проверить заранее:** Settings → Actions → General → Workflow permissions → должно быть **«Read and write permissions»**.

### 3.2. Дополнительный риск: повторные запуски

`gh release create` создаёт релиз с тегом `v<версия>-run<run_id>`. Тег уникален для прогона, поэтому **повторный прогон создаст ещё один релиз**, а не упадёт на «tag exists». Накопится мусор, но запуск не сломается. **Не правил** — вставлено дословно.

---

## 4. «Релиз создан / не создан»

**На момент отчёта: НЕ СОЗДАН.** Релизов в репозитории нет, тегов нет.

| Проверка | Результат |
|---|---|
| `gh release list` | пусто |
| Теги | пусто |
| Прогон не запускал | ✅ как вы и просили |

**Релиз создастся только первым прогоном** после merge. Run ID, тег и ссылку запишу по факту.

### 4.1. Прямая ссылка, где он появится

```
https://github.com/BlockBaster3K/carnis-hub/releases
```

Файл: **`carnis-3.5.1.jar`** (не `Source code`).

---

## 5. Заказчику

- **Где будет лежать jar:** `github.com/BlockBaster3K/carnis-hub/releases`
- **Что качать:** файл **`carnis-3.5.1.jar`** из последнего релиза. **Не** `Source code (zip)` / `Source code (tar.gz)`.
- **Артефакт прогона остался** и никуда не делся, но он в Azure и у вас не открывается — это не наша ошибка и не поломка workflow.
- ⚠️ **Честное предупреждение:** физически релизные файлы GitHub тоже хранятся в Azure (`releaseassetproduction.blob.core.windows.net`). Если у вас режется весь домен `*.blob.core.windows.net` — релиз не поможет. Это станет видно сразу: страница релиза откроется, а скачивание не пойдёт.
- **Если не пойдёт и релиз** — напишите точный текст ошибки и что именно открылось. Тогда причина не в GitHub, и надо смотреть ваш антивирус/прокси/hosts, потому что VPN, по вашим словам, тоже не помогает.

---

## 6. Заморозка

Остальное — стоп. Эта правка — единственное исключение, как вы и указали. Файлы результатов принимаю только по вашей прямой команде.

---

## 7. Контроль (`SORT_14.md`)

| Пункт | Статус |
|---|---|
| `build.yml` заменён, `diff` = 0 | ✅ 3 791 Б, побайтово |
| YAML валиден | ✅ проверен парсером |
| `active` | ⏳ подтвержу после merge |
| inputs `package` на месте | ✅ в YAML есть |
| Workflow permissions | ⚠️ **проверить не смог — 403 на всех эндпоинтах**; сообщаю, не правлю |
| «Релиз создан/не создан» | ✅ **не создан** — релизов и тегов нет, прогон не запускал |
| Прямая ссылка на релиз | ✅ `…/carnis-hub/releases` |
| Прогон не запускал | ✅ |
