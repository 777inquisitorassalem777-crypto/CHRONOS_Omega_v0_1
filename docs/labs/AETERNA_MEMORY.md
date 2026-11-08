# AETERNA MEMORY — граф знаний и памяти

## Сущности
`Person`, `Civilization`, `Generation`, `Place`, `Event`, `Text`, `Edition`, `Concept`, `ScientificDiscovery`, `Institution`, `Tradition`, `Experiment`, `Dataset`, `Claim`, `Source`.

## Связи
`AUTHORED`, `TRANSLATED`, `INFLUENCED`, `CRITIQUED`, `PRECEDED`, `CONTEMPORARY_WITH`, `LOCATED_IN`, `PART_OF`, `DISCOVERED`, `REPLICATED`, `CONTRADICTS`, `SUPPORTS`, `CITES`, `DERIVED_FROM`, `TRANSMITTED_TO`, `VARIANT_OF`.

## Обязательные свойства ребра
`source_id`, `valid_time`, `recorded_time`, `relation_type`, `evidence_class`, `confidence_note`, `directionality`, `curator`, `created_at`. Связь «влиял на» без исторического свидетельства хранится как гипотеза, а не факт.

## Минимальный графовый профиль
- Каждая сущность имеет устойчивый ID и альтернативные имена.
- Каждое утверждение имеет один или несколько источников либо помечается как неподтверждённое.
- Различать время события и время записи/публикации.
- Поддерживать противоречащие версии и разные историографические позиции.
- Вести append-only журнал изменений, контрольные суммы импортированных файлов и версии схемы.

## Экспорт
JSON-LD для обмена; CSV для таблиц; GraphML для визуализации; позднее Neo4j/ArangoDB или PostgreSQL с таблицами узлов/рёбер. На старте — переносимая JSON Lines модель без привязки к вендору.
