<p align="center">
  <a href="README.md">English</a> · <strong>Русский</strong>
</p>

<p align="center">
  <h1 align="center">Claude Code Delegate</h1>
</p>

<p align="center">
  <a href="https://github.com/letya999/claude-code-delegate"><img src="https://img.shields.io/badge/статус-активен-brightgreen" alt="статус"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/лицензия-MIT-blue" alt="Лицензия: MIT"></a>
  <a href="https://skills.sh"><img src="https://img.shields.io/badge/skills.sh-доступен-black" alt="skills.sh"></a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/cli-claude-purple" alt="CLI: claude">
</p>

Скилл-делегат для неинтерактивного запуска Claude Code CLI (`claude`) от [Артема Летюшева](https://github.com/letya999).

Основная команда — `scripts/delegate_claude.py`. Главный потребитель — управляющий агент или оркестратор: каждый запуск выполняет Claude Code в ограниченном подпроцессе (`claude -p`) и возвращает структурированный JSON-конверт.

---

## Одна цель, изолированный подпроцесс, нулевое доверие

Скрипт-обёртка служит детерминированным барьером безопасности между управляющим агентом и Claude Code CLI:

- **Строго неинтерактивный запуск:** Вызывает `claude -p` напрямую через `subprocess.run(..., shell=False)` без интерактивных запросов.
- **Ограничение рабочей зоны:** Задаёт рабочий каталог подпроцесса и добавляет `--add-dir <cwd>` для изоляции доступа к файлам.
- **Извлечение ответа:** Извлекает итоговый текст ответа из JSON-конверта Claude в поле `response`.
- **Верификация результатов:** Ответ считается непроверенным до независимой инспекции через diff и тесты.
- **Изоляция секретов:** Не считывает, не печатает и не передаёт `ANTHROPIC_API_KEY`, токены `~/.claude` или файлы `.env`.

## Матрица возможностей

| Параметр / Возможность | Спецификация | Поведение и гарантии |
|---|---|---|
| **Команда запуска** | `claude -p "<task>"` | Неинтерактивное выполнение в print-режиме |
| **Формат вывода** | `--output-format json` | Результат извлекается в верхнеуровневую строку `response` |
| **Ограничение каталога** | `--add-dir <cwd>` | Предоставляет Claude доступ к каталогу проекта |
| **Выбор модели** | `--model <name>` | Передаёт указанное имя модели в Claude CLI |
| **Режимы доступа** | `--permission-mode <mode>` | Поддерживает гранулярные режимы (например, `read-only`) |
| **Автономные правки** | `--always-approve` | Передаёт `--dangerously-skip-permissions` (взаимоисключающе с `--permission-mode`) |
| **Возобновление сессий** | `--session-id` / `--resume` | Продолжает существующую сессию диалога |
| **Переопределение бинарника** | Переменная `CLAUDE_BIN` | Приоритетный путь до вызова из PATH |
| **Коды возврата** | `0, 2, 65, 124, 126, 127` | Стандартизированная маршрутизация ошибок |

## Установка

Через `npx skills`:

```bash
npx skills add letya999/claude-code-delegate
```

Или клонированием в каталог скиллов:

```bash
git clone https://github.com/letya999/claude-code-delegate.git .agents/skills/claude-code-delegate
```

## Быстрый старт

### POSIX (macOS, Linux, WSL)

```bash
python3 scripts/delegate_claude.py \
  --cwd "$PWD" \
  --task "Проанализируй репозиторий и выдели самую критичную проблему." \
  --timeout 45m
```

### Windows PowerShell

```powershell
py -3 .\scripts\delegate_claude.py `
  --cwd (Get-Location).Path `
  --task "Проанализируй репозиторий и выдели самую критичную проблему." `
  --timeout 45m
```

---

<details>
<summary>Схема JSON-манифеста и интеграция с агентом</summary>

Обёртка записывает `stdout.json`, `stderr.log` и `result.json` во временный каталог:

```json
{
  "tool": "claude",
  "cwd": "C:\\work\\repo",
  "exit_code": 0,
  "output_dir": "C:\\Temp\\claude-code-delegate-xyz",
  "stdout": "C:\\Temp\\claude-code-delegate-xyz\\stdout.json",
  "stderr": "C:\\Temp\\claude-code-delegate-xyz\\stderr.log",
  "response": "Извлеченный текст ответа из полезной нагрузки Claude",
  "raw": {
    "result": "..."
  }
}
```

Если Claude завершился с кодом 0, но вернул пустой ответ или некорректный JSON, обёртка завершается с кодом `65`.

</details>

<details>
<summary>Флаги CLI и параметры запуска</summary>

| Флаг | Тип | Описание |
|---|---|---|
| `--cwd` | Путь (обязательный) | Рабочий каталог проекта. Код `2`, если каталог не существует. |
| `--task` | Строка (обязательный) | Текст задачи / промпта для передачи Claude. |
| `--timeout` | Время (по умолчанию: `45m`) | Таймаут: `90s`, `45m`, `2h` или число секунд. |
| `--model` | Строка | Модель Claude для выполнения запроса. |
| `--permission-mode` | Строка | Режим прав Claude (например, `read-only`). |
| `--always-approve` | Флаг | Передаёт `--dangerously-skip-permissions` для автономных правок. |
| `--session-id` | Строка | Идентификатор сессии для возобновления диалога. |
| `--resume` | Строка | Альтернативный флаг возобновления сессии. |
| `--output-dir` | Путь | Каталог для сохранения логов и манифеста. |

</details>

<details>
<summary>Правила безопасности и изоляция секретов</summary>

- **Защита секретов:** Никогда не считывает и не логирует `ANTHROPIC_API_KEY`, токены OAuth и `.credentials.json`.
- **Чтение по умолчанию:** Ограниченное выполнение без прав на запись, если не указаны явные флаги доступа.
- **Защита от циклов:** Делегированный Claude не должен запускать новые подпроцессы через обёртки.

</details>

<details>
<summary>Протокол независимой верификации</summary>

Ответы делегата не считаются окончательным доказательством. При изменении файлов:

1. Проверьте diff: `git diff --stat` и `git diff`.
2. Запустите тесты независимо: `pytest`, `npm test`, `cargo test`.
3. Проверьте форматирование кода и линтеры.

</details>

<details>
<summary>Набор тестов</summary>

Запуск тестов через стандартную библиотеку `unittest`:

```bash
python -m unittest discover -s tests -v
```

</details>

<details>
<summary>Точки входа скилла</summary>

- [SKILL.md](SKILL.md) — Спецификация инструкций для кодинг-агентов.
- [QUICKSTART.md](QUICKSTART.md) — Краткое руководство.
- [references/runtime-setup.md](references/runtime-setup.md) — Проверка окружения перед запуском.
- [references/headless-reference.md](references/headless-reference.md) — Справочник флагов Claude CLI.
- [.well-known/agent-skills/index.json](.well-known/agent-skills/index.json) — Индекс для каталога skills.sh.
- [dist/claude-code-delegate.zip](dist/claude-code-delegate.zip) — Архив скилла.

</details>

<details>
<summary>Лицензия</summary>

MIT License. См. полный текст в [LICENSE](LICENSE). Copyright (c) 2026 Artem Letyushev.

</details>
