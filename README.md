# ХРОНОС Ω v0.3.0

**Рабочая исследовательская система; доказательность и происхождение данных обязательны.** Python 3.10+, стандартная библиотека, внешние зависимости для ядра не нужны.

## Быстрый запуск

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# Linux/macOS: source .venv/bin/activate
pip install -e .
python -m chronos --help
```

Если не устанавливать пакет, используйте `PYTHONPATH=src python -m chronos ...`.

## Функции v0.3.0

- **Загрузка и индексирование:** TXT, Markdown, CSV, JSON, HTML и текстовые PDF в локальный SQLite (PDF: `pip install -e .[pdf]`; сканы требуют отдельного OCR-процесса); SHA-256 для содержимого; полнотекстовый поиск FTS5 (если поддерживается SQLite) с резервным поиском LIKE.
- **AETERNA MEMORY:** граф знаний в JSON, поиск узлов по названию/ID/свойствам; связи требуют существующие конечные узлы и допустимые классы доказательности в Python API.
- **RUSSIA HISTORIA:** импорт CSV временных рядов в SQLite, ISO-даты, числовые значения, обязательные source_id и evidence_class; сортированный запрос по индикатору и географии.
- **KOZYREV LAB:** KZ-01 preregistration draft, четыре экспериментальных условия, ослепление анализа, рандомизация, ковариаты, план анализа, правила исключения и безопасность.

## Команды

```bash
# Индексировать отдельный документ или каталог
PYTHONPATH=src python -m chronos ingest data/arcana

# Поиск по индексу
PYTHONPATH=src python -m chronos search 'Blavatsky'

# Импортировать проверенный исторический CSV
PYTHONPATH=src python -m chronos history-import path/to/observations.csv

# Получить временной ряд
PYTHONPATH=src python -m chronos history-query population --geography Russia

# Сформировать черновик KZ-01
PYTHONPATH=src python -m chronos kz01-register

# Поиск по графу
PYTHONPATH=src python -m chronos graph-search Kozyrev
```

Индекс по умолчанию находится в `data/index/`; SQLite-файлы локальные и не включаются в релиз.

## Данные и ограничения

`data/history/observations_template.csv` — только заголовок схемы, не набор исторических данных. Не импортируйте оценки без проверяемого источника, единиц измерения, географии и методологии. Каждое наблюдение должно иметь source_id. Не смешивайте текущие границы и исторические территории без явной нормализации.

`data/graph/aeterna.json` — небольшой демонстрационный граф; его связи не заменяют библиографическую проверку. Расширяйте `data/source_register.csv` и указывайте точную редакцию/страницу/архивный шифр.

`docs/protocols/KZ-01.md` и `data/kozyrev/KZ-01_preregistration.json` имеют статус **DRAFT_NOT_PREREGISTERED**. Они не означают, что опыт выполнен или зарегистрирован. До эксперимента необходимо зафиксировать конструкцию, калибровку, RPM, стабилизацию, минимальный эффект, размер выборки, статистический код и внешнюю временную метку регистрации. Положительный сдвиг весов сам по себе не доказывает изменение свойств времени.

## Тесты

```bash
pip install -r requirements-dev.txt
PYTHONPATH=src pytest -q
```

## Структура

- `src/chronos/` — ядро, импорт/поиск, граф, исторические ряды, KZ-01, CLI.
- `data/` — реестр источников, шаблоны, граф, протокол.
- `docs/` — методология, лаборатории, этика и протоколы.
- `tests/` — автоматические тесты.
- `reports/` — отчёты и журнал изменений.
