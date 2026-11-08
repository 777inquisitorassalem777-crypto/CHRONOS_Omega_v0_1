#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
  ХРОНОС Ω  v0.4.0
  Единый исследовательский скрипт проекта
  «Защита времени, сознания и будущего человечества»
============================================================================
  Модули:
    1. SOURCE ARCHIVE   — SQLite + SHA-256 + FTS5 (каталог источников)
    2. AETERNA MEMORY   — граф знаний цивилизаций и концепций
    3. RUSSIA HISTORIA  — исторические временные ряды
    4. KOZYREV LAB      — экспериментальный стенд KZ-01
    5. OCR ARCHIVE      — базовое извлечение текста (без внешних зависимостей)
    6. CLI              — командный интерфейс
    7. TESTS            — встроенные автоматические тесты
    8. DEMO DATA        — демонстрационная база
============================================================================
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import datetime as dt
import hashlib
import io
import json
import os
import re
import sqlite3
import sys
import textwrap
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ============================================================================
# КОНСТАНТЫ И КОНФИГУРАЦИЯ
# ============================================================================

VERSION = "0.4.0"
PROJECT_NAME = "CHRONOS_OMEGA"
DEFAULT_DB = "chronos_omega.db"
DEFAULT_DATA_DIR = "chronos_data"

EVIDENCE_LEVELS = (
    "VERIFIED",            # подтверждено надёжными источниками
    "SUPPORTED",           # существенные свидетельства
    "HYPOTHESIS",          # проверяемая гипотеза
    "TRADITIONAL_BELIEF",  # положение традиции
    "SYMBOLIC",            # метафора / символика
    "REFUTED",             # противоречит данным
    "UNKNOWN",             # недостаточно информации
)

CONSTITUTION = [
    "1. Жизнь священна: никакая практика не должна причинять вред человеку.",
    "2. Истина важнее догмы: любые утверждения подлежат проверке.",
    "3. Свобода сознания: никакого принуждения и подавления воли.",
    "4. Добро выше власти: знания не должны становиться инструментом угнетения.",
    "5. Время принадлежит жизни: задача — осмысленно проживать его.",
    "6. Знание передаётся поколениям: сохранять достижения и уроки.",
    "7. Будущее открыто: не объявлять катастрофические пророчества неизбежными.",
]


# ============================================================================
# УТИЛИТЫ
# ============================================================================

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def print_banner(title: str) -> None:
    width = 72
    print()
    print("=" * width)
    print(f"  {title}")
    print("=" * width)


# ============================================================================
# МОДУЛЬ 1: SOURCE ARCHIVE (SQLite + SHA-256 + FTS5)
# ============================================================================

class SourceArchive:
    """
    Каталог источников с SHA-256-проверкой происхождения,
    полнотекстовым поиском (FTS5) и метаданными.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    # ---------- схема ----------
    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript("""
        PRAGMA journal_mode = WAL;
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS sources (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            author      TEXT,
            date_str    TEXT,
            url         TEXT,
            doi         TEXT,
            src_type    TEXT NOT NULL,
            evidence    TEXT NOT NULL DEFAULT 'UNKNOWN',
            summary     TEXT,
            notes       TEXT,
            content     TEXT,
            file_path   TEXT,
            sha256      TEXT,
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_sources_evidence ON sources(evidence);
        CREATE INDEX IF NOT EXISTS idx_sources_type     ON sources(src_type);

        CREATE VIRTUAL TABLE IF NOT EXISTS sources_fts
        USING fts5(title, author, summary, content, summary='sources',
                   content_rowid='id');

        CREATE TRIGGER IF NOT EXISTS sources_ai AFTER INSERT ON sources BEGIN
            INSERT INTO sources_fts(rowid, title, author, summary, content)
            VALUES (new.id, new.title, new.author, new.summary, new.content);
        END;

        CREATE TRIGGER IF NOT EXISTS sources_ad AFTER DELETE ON sources BEGIN
            INSERT INTO sources_fts(sources_fts, rowid, title, author, summary, content)
            VALUES ('delete', old.id, old.title, old.author, old.summary, old.content);
        END;

        CREATE TRIGGER IF NOT EXISTS sources_au AFTER UPDATE ON sources BEGIN
            INSERT INTO sources_fts(sources_fts, rowid, title, author, summary, content)
            VALUES ('delete', old.id, old.title, old.author, old.summary, old.content);
            INSERT INTO sources_fts(rowid, title, author, summary, content)
            VALUES (new.id, new.title, new.author, new.summary, new.content);
        END;

        CREATE TABLE IF NOT EXISTS audit_log (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            action     TEXT NOT NULL,
            source_id  INTEGER,
            detail     TEXT,
            created_at TEXT NOT NULL
        );
        """)
        self.conn.commit()

    # ---------- CRUD ----------
    def add_source(self, *, title: str, author: Optional[str] = None,
                   date_str: Optional[str] = None, url: Optional[str] = None,
                   doi: Optional[str] = None, src_type: str = "article",
                   evidence: str = "UNKNOWN", summary: Optional[str] = None,
                   notes: Optional[str] = None, content: Optional[str] = None,
                   file_path: Optional[Path] = None) -> int:
        sha = None
        if file_path and Path(file_path).exists():
            sha = sha256_file(Path(file_path))
        ts = now_iso()
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO sources
            (title, author, date_str, url, doi, src_type, evidence,
             summary, notes, content, file_path, sha256, created_at, updated_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (title, author, date_str, url, doi, src_type, evidence,
              summary, notes, content,
              str(file_path) if file_path else None,
              sha, ts, ts))
        self.conn.commit()
        sid = cur.lastrowid
        self._audit("ADD_SOURCE", sid, f"title={title!r}")
        return sid

    def get_source(self, source_id: int) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM sources WHERE id=?", (source_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def update_evidence(self, source_id: int, evidence: str) -> bool:
        if evidence not in EVIDENCE_LEVELS:
            raise ValueError(f"Недопустимый уровень: {evidence}")
        cur = self.conn.cursor()
        cur.execute("""
            UPDATE sources SET evidence=?, updated_at=? WHERE id=?
        """, (evidence, now_iso(), source_id))
        self.conn.commit()
        self._audit("UPDATE_EVIDENCE", source_id, f"evidence={evidence}")
        return cur.rowcount > 0

    def list_sources(self, limit: int = 50, offset: int = 0,
                     evidence: Optional[str] = None,
                     src_type: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM sources WHERE 1=1"
        params: List[Any] = []
        if evidence:
            sql += " AND evidence=?"
            params.append(evidence)
        if src_type:
            sql += " AND src_type=?"
            params.append(src_type)
        sql += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]

    def search(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT s.id, s.title, s.author, s.evidence, s.src_type, s.summary,
                   rank
            FROM sources_fts f
            JOIN sources s ON s.id = f.rowid
            WHERE sources_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit))
        return [dict(r) for r in cur.fetchall()]

    def count(self) -> int:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sources")
        return cur.fetchone()[0]

    # ---------- аудит ----------
    def _audit(self, action: str, source_id: Optional[int], detail: str) -> None:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO audit_log (action, source_id, detail, created_at)
            VALUES (?,?,?,?)
        """, (action, source_id, detail, now_iso()))
        self.conn.commit()

    def audit_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT * FROM audit_log ORDER BY id DESC LIMIT ?
        """, (limit,))
        return [dict(r) for r in cur.fetchall()]

    def close(self) -> None:
        self.conn.close()


# ============================================================================
# МОДУЛЬ 2: AETERNA MEMORY (граф знаний)
# ============================================================================

@dataclass
class KnowledgeNode:
    id: str
    kind: str           # person | civilization | text | concept | discovery | event
    label: str
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeEdge:
    source: str
    target: str
    relation: str       # influenced | authored | belonged_to | discovered | ...
    evidence: str = "UNKNOWN"
    source_ref: Optional[str] = None   # id источника в SourceArchive


class AeternaMemory:
    """
    Граф знаний: цивилизации → поколения → личности → тексты → концепции → открытия.
    Каждая связь имеет уровень доказательности и ссылку на источник.
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS kg_nodes (
            id    TEXT PRIMARY KEY,
            kind  TEXT NOT NULL,
            label TEXT NOT NULL,
            data  TEXT NOT NULL DEFAULT '{}'
        );
        CREATE INDEX IF NOT EXISTS idx_nodes_kind ON kg_nodes(kind);

        CREATE TABLE IF NOT EXISTS kg_edges (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            source     TEXT NOT NULL,
            target     TEXT NOT NULL,
            relation   TEXT NOT NULL,
            evidence   TEXT NOT NULL DEFAULT 'UNKNOWN',
            source_ref TEXT,
            UNIQUE(source, target, relation)
        );
        CREATE INDEX IF NOT EXISTS idx_edges_src ON kg_edges(source);
        CREATE INDEX IF NOT EXISTS idx_edges_tgt ON kg_edges(target);
        """)
        self.conn.commit()

    # ---------- узлы ----------
    def upsert_node(self, node: KnowledgeNode) -> None:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO kg_nodes(id, kind, label, data)
            VALUES (?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                kind=excluded.kind, label=excluded.label, data=excluded.data
        """, (node.id, node.kind, node.label, json.dumps(node.data, ensure_ascii=False)))
        self.conn.commit()

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM kg_nodes WHERE id=?", (node_id,))
        r = cur.fetchone()
        if not r:
            return None
        return KnowledgeNode(id=r["id"], kind=r["kind"], label=r["label"],
                             data=json.loads(r["data"]))

    def search_nodes(self, query: str, kind: Optional[str] = None,
                     limit: int = 30) -> List[KnowledgeNode]:
        sql = "SELECT * FROM kg_nodes WHERE (id LIKE ? OR label LIKE ?)"
        params: List[Any] = [f"%{query}%", f"%{query}%"]
        if kind:
            sql += " AND kind=?"
            params.append(kind)
        sql += " LIMIT ?"
        params.append(limit)
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return [KnowledgeNode(id=r["id"], kind=r["kind"], label=r["label"],
                              data=json.loads(r["data"])) for r in cur.fetchall()]

    # ---------- рёбра ----------
    def add_edge(self, edge: KnowledgeEdge) -> None:
        if edge.evidence not in EVIDENCE_LEVELS:
            raise ValueError(f"Недопустимый уровень: {edge.evidence}")
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO kg_edges(source, target, relation, evidence, source_ref)
            VALUES (?,?,?,?,?)
            ON CONFLICT(source, target, relation) DO UPDATE SET
                evidence=excluded.evidence, source_ref=excluded.source_ref
        """, (edge.source, edge.target, edge.relation,
              edge.evidence, edge.source_ref))
        self.conn.commit()

    def neighbors(self, node_id: str, max_depth: int = 1) -> Dict[str, Any]:
        """Возвращает узел и его соседей (до max_depth)."""
        visited: Dict[str, Dict[str, Any]] = {}
        frontier = {node_id}
        for _ in range(max_depth):
            if not frontier:
                break
            cur = self.conn.cursor()
            placeholders = ",".join("?" * len(frontier))
            cur.execute(f"""
                SELECT source, target, relation, evidence, source_ref
                FROM kg_edges
                WHERE source IN ({placeholders}) OR target IN ({placeholders})
            """, list(frontier) + list(frontier))
            next_front: set = set()
            for r in cur.fetchall():
                for endpoint in (r["source"], r["target"]):
                    if endpoint not in visited:
                        visited[endpoint] = {"edges": []}
                        next_front.add(endpoint)
                visited[r["source"]]["edges"].append({
                    "to": r["target"], "relation": r["relation"],
                    "evidence": r["evidence"], "source_ref": r["source_ref"],
                })
                visited[r["target"]]["edges"].append({
                    "to": r["source"], "relation": r["relation"],
                    "evidence": r["evidence"], "source_ref": r["source_ref"],
                })
            frontier = next_front - set(visited)
        return visited

    def stats(self) -> Dict[str, int]:
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM kg_nodes")
        n_nodes = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM kg_edges")
        n_edges = cur.fetchone()[0]
        return {"nodes": n_nodes, "edges": n_edges}

    def close(self) -> None:
        self.conn.close()


# ============================================================================
# МОДУЛЬ 3: RUSSIA HISTORIA (временные ряды)
# ============================================================================

class RussiaHistoria:
    """
    Импорт и запрос исторических временных рядов (CSV).
    Формат CSV: year,indicator,geography,value,unit,source_ref,notes
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS history_series (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            year        INTEGER NOT NULL,
            indicator   TEXT NOT NULL,
            geography   TEXT NOT NULL DEFAULT 'Russia',
            value       REAL,
            unit        TEXT,
            source_ref  TEXT,
            notes       TEXT,
            imported_at TEXT NOT NULL,
            UNIQUE(year, indicator, geography)
        );
        CREATE INDEX IF NOT EXISTS idx_hist_year ON history_series(year);
        CREATE INDEX IF NOT EXISTS idx_hist_ind  ON history_series(indicator);
        CREATE INDEX IF NOT EXISTS idx_hist_geo  ON history_series(geography);
        """)
        self.conn.commit()

    def import_csv(self, csv_text: str) -> int:
        """Импорт CSV-текста. Возвращает количество добавленных строк."""
        reader = csv.DictReader(io.StringIO(csv_text))
        ts = now_iso()
        cur = self.conn.cursor()
        added = 0
        for row in reader:
            try:
                year = int(row["year"])
                value = float(row["value"]) if row.get("value") not in (None, "") else None
            except (KeyError, ValueError):
                continue
            cur.execute("""
                INSERT INTO history_series
                (year, indicator, geography, value, unit, source_ref, notes, imported_at)
                VALUES (?,?,?,?,?,?,?,?)
                ON CONFLICT(year, indicator, geography) DO UPDATE SET
                    value=excluded.value, unit=excluded.unit,
                    source_ref=excluded.source_ref, notes=excluded.notes,
                    imported_at=excluded.imported_at
            """, (year,
                  row.get("indicator", "unknown"),
                  row.get("geography", "Russia"),
                  value,
                  row.get("unit"),
                  row.get("source_ref"),
                  row.get("notes"),
                  ts))
            added += 1
        self.conn.commit()
        return added

    def query(self, indicator: str, geography: str = "Russia",
              year_from: Optional[int] = None,
              year_to: Optional[int] = None) -> List[Dict[str, Any]]:
        sql = ("SELECT * FROM history_series "
               "WHERE indicator=? AND geography=?")
        params: List[Any] = [indicator, geography]
        if year_from is not None:
            sql += " AND year>=?"
            params.append(year_from)
        if year_to is not None:
            sql += " AND year<=?"
            params.append(year_to)
        sql += " ORDER BY year"
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]

    def indicators(self) -> List[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT indicator FROM history_series ORDER BY indicator")
        return [r[0] for r in cur.fetchall()]

    def close(self) -> None:
        self.conn.close()


# ============================================================================
# МОДУЛЬ 4: KOZYREV LAB (экспериментальный стенд KZ-01)
# ============================================================================

@dataclass
class KZ01Measurement:
    run_id: str
    mode: str                # engine_off | gyro_spin | rotor_locked | static_mass
    timestamp: str
    temperature_c: float
    vibration_rms: float
    emf_uv: float
    tilt_mrad: float
    weight_delta_mg: float
    notes: str = ""


class KozyrevLab:
    """
    Экспериментальный стенд KZ-01.
    Регистрация запусков, измерений, хешей исходных данных.
    Статус: ПРОЕКТ ПРОТОКОЛА (не зарегистрирован).
    """

    def __init__(self, db_path: Path):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS kz_runs (
            run_id       TEXT PRIMARY KEY,
            protocol     TEXT NOT NULL DEFAULT 'KZ-01',
            mode         TEXT NOT NULL,
            created_at   TEXT NOT NULL,
            raw_hash     TEXT,
            notes        TEXT
        );

        CREATE TABLE IF NOT EXISTS kz_measurements (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id          TEXT NOT NULL,
            mode            TEXT NOT NULL,
            timestamp       TEXT NOT NULL,
            temperature_c   REAL,
            vibration_rms   REAL,
            emf_uv          REAL,
            tilt_mrad       REAL,
            weight_delta_mg REAL,
            notes           TEXT,
            FOREIGN KEY(run_id) REFERENCES kz_runs(run_id)
        );
        CREATE INDEX IF NOT EXISTS idx_kz_run ON kz_measurements(run_id);
        """)
        self.conn.commit()

    def register_run(self, run_id: str, mode: str,
                     raw_data: bytes, notes: str = "") -> str:
        h = sha256_bytes(raw_data)
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO kz_runs(run_id, protocol, mode, created_at, raw_hash, notes)
            VALUES (?,?,?,?,?,?)
        """, (run_id, "KZ-01", mode, now_iso(), h, notes))
        self.conn.commit()
        return h

    def add_measurement(self, m: KZ01Measurement) -> int:
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO kz_measurements
            (run_id, mode, timestamp, temperature_c, vibration_rms,
             emf_uv, tilt_mrad, weight_delta_mg, notes)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (m.run_id, m.mode, m.timestamp, m.temperature_c,
              m.vibration_rms, m.emf_uv, m.tilt_mrad,
              m.weight_delta_mg, m.notes))
        self.conn.commit()
        return cur.lastrowid

    def run_summary(self, run_id: str) -> Dict[str, Any]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM kz_runs WHERE run_id=?", (run_id,))
        run = cur.fetchone()
        if not run:
            return {}
        cur.execute("""
            SELECT COUNT(*),
                   AVG(temperature_c), AVG(vibration_rms),
                   AVG(emf_uv), AVG(tilt_mrad), AVG(weight_delta_mg)
            FROM kz_measurements WHERE run_id=?
        """, (run_id,))
        stats = cur.fetchone()
        return {
            "run": dict(run),
            "n_measurements": stats[0],
            "avg_temperature_c": stats[1],
            "avg_vibration_rms": stats[2],
            "avg_emf_uv": stats[3],
            "avg_tilt_mrad": stats[4],
            "avg_weight_delta_mg": stats[5],
        }

    def list_runs(self) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM kz_runs ORDER BY created_at DESC")
        return [dict(r) for r in cur.fetchall()]

    def export_json(self, run_id: str) -> str:
        summary = self.run_summary(run_id)
        return json.dumps(summary, ensure_ascii=False, indent=2)

    def close(self) -> None:
        self.conn.close()


# ============================================================================
# МОДУЛЬ 5: OCR ARCHIVE (базовое извлечение текста)
# ============================================================================

class OcrArchive:
    """
    Упрощённый парсер текстовых форматов без внешних зависимостей.
    Поддерживает: .txt, .md, .csv, .json, .html (очистка тегов).
    Для PDF/DOCX/изображений — заглушка с предупреждением.
    """

    SUPPORTED_TEXT = {".txt", ".md", ".csv", ".json", ".log"}
    SUPPORTED_HTML = {".html", ".htm"}
    NEEDS_EXTERNAL = {".pdf", ".docx", ".png", ".jpg", ".jpeg", ".tiff"}

    @classmethod
    def extract(cls, path: Path) -> Tuple[str, str]:
        """
        Возвращает (text, status).
        status: 'ok' | 'html_cleaned' | 'unsupported' | 'empty'
        """
        if not path.exists():
            return ("", "missing")
        suffix = path.suffix.lower()
        if suffix in cls.SUPPORTED_TEXT:
            return (path.read_text(encoding="utf-8", errors="ignore"), "ok")
        if suffix in cls.SUPPORTED_HTML:
            raw = path.read_text(encoding="utf-8", errors="ignore")
            cleaned = re.sub(r"<[^>]+>", " ", raw)
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            return (cleaned, "html_cleaned")
        if suffix in cls.NEEDS_EXTERNAL:
            return ("", "unsupported")
        return ("", "unsupported")


# ============================================================================
# МОДУЛЬ 6: ДЕМО-ДАННЫЕ
# ============================================================================

DEMO_HISTORY_CSV = """\
year,indicator,geography,value,unit,source_ref,notes
1795,population,Russia,37.6,mln,RiStat,первая ревизия
1858,population,Russia,74.0,mln,RiStat,
1897,population,Russia,125.6,mln,RiStat,перепись
1926,population,Russia,92.7,mln,RiStat,перепись СССР
1959,population,Russia,117.2,mln,RiStat,перепись
1989,population,Russia,147.0,mln,RiStat,перепись
2002,population,Russia,145.2,mln,RiStat,перепись
2010,population,Russia,142.9,mln,RiStat,перепись
2021,population,Russia,143.4,mln,RiStat,перепись
1999,gdp_real_growth,Russia,6.4,percent,Maddison,
2000,gdp_real_growth,Russia,10.0,percent,Maddison,
2008,gdp_real_growth,Russia,5.2,percent,Maddison,
2009,gdp_real_growth,Russia,-7.8,percent,Maddison,кризис
2015,gdp_real_growth,Russia,-2.0,percent,Maddison,
2020,gdp_real_growth,Russia,-2.7,percent,Maddison,пандемия
2022,gdp_real_growth,Russia,-1.2,percent,Maddison,
"""

DEMO_NODES: List[KnowledgeNode] = [
    KnowledgeNode("civilization:slavic", "civilization",
                  "Славянская цивилизация", {"region": "Eurasia"}),
    KnowledgeNode("civilization:chinese", "civilization",
                  "Китайская цивилизация", {"region": "East Asia"}),
    KnowledgeNode("civilization:indian", "civilization",
                  "Индийская цивилизация", {"region": "South Asia"}),
    KnowledgeNode("civilization:western", "civilization",
                  "Западная цивилизация", {"region": "Europe/Atlantic"}),
    KnowledgeNode("person:kozyrev", "person",
                  "Николай Александрович Козырев",
                  {"born": 1908, "died": 1983, "field": "astrophysics"}),
    KnowledgeNode("person:blavatsky", "person",
                  "Елена Петровна Блаватская",
                  {"born": 1831, "died": 1891, "movement": "Theosophy"}),
    KnowledgeNode("person:gurджиев", "person",
                  "Георгий Иванович Гурджиев",
                  {"born": 1866, "died": 1949, "movement": "Fourth Way"}),
    KnowledgeNode("person:papus", "person",
                  "Папюс (Жерар Анкосс)",
                  {"born": 1865, "died": 1916, "movement": "Occultism"}),
    KnowledgeNode("person:crowley", "person",
                  "Алистер Кроули",
                  {"born": 1875, "died": 1947, "movement": "Thelema"}),
    KnowledgeNode("text:secret_doctrine", "text",
                  "Тайная доктрина",
                  {"author": "person:blavatsky", "year": 1888}),
    KnowledgeNode("text:cause_mechanics", "text",
                  "Причинная механика",
                  {"author": "person:kozyrev", "year": 1958}),
    KnowledgeNode("concept:i_ching", "concept",
                  "И-Цзин (Книга Перемен)",
                  {"tradition": "chinese", "elements": 64}),
    KnowledgeNode("concept:gunas", "concept",
                  "Гуны (саттва, раджас, тамас)",
                  {"tradition": "vedic"}),
    KnowledgeNode("concept:chrono_magic", "concept",
                  "Хрономагия",
                  {"definition": "символическая работа со временем"}),
    KnowledgeNode("discovery:quantum_arrow", "discovery",
                  "Квантовая стрела времени (гипотеза)",
                  {"status": "HYPOTHESIS", "year": 2026}),
]

DEMO_EDGES: List[KnowledgeEdge] = [
    KnowledgeEdge("person:kozyrev", "text:cause_mechanics",
                  "authored", "VERIFIED"),
    KnowledgeEdge("person:blavatsky", "text:secret_doctrine",
                  "authored", "VERIFIED"),
    KnowledgeEdge("text:cause_mechanics", "concept:chrono_magic",
                  "inspired", "HYPOTHESIS"),
    KnowledgeEdge("concept:i_ching", "civilization:chinese",
                  "belonged_to", "VERIFIED"),
    KnowledgeEdge("concept:gunas", "civilization:indian",
                  "belonged_to", "VERIFIED"),
    KnowledgeEdge("person:kozyrev", "discovery:quantum_arrow",
                  "precursor_of", "HYPOTHESIS"),
    KnowledgeEdge("person:crowley", "civilization:western",
                  "belonged_to", "VERIFIED"),
    KnowledgeEdge("person:papus", "civilization:western",
                  "belonged_to", "VERIFIED"),
]


# ============================================================================
# МОДУЛЬ 7: CLI
# ============================================================================

class ChronosCLI:
    """Командный интерфейс проекта."""

    def __init__(self, data_dir: Path):
        self.data_dir = ensure_dir(Path(data_dir))
        self.db = self.data_dir / DEFAULT_DB
        self.archive = SourceArchive(self.db)
        self.memory = AeternaMemory(self.db)
        self.history = RussiaHistoria(self.db)
        self.lab = KozyrevLab(self.db)

    # ---------- команды ----------
    def cmd_init(self) -> None:
        print_banner(f"Инициализация {PROJECT_NAME} v{VERSION}")
        print(f"  Каталог данных : {self.data_dir}")
        print(f"  База данных    : {self.db}")
        print(f"  Источников     : {self.archive.count()}")
        ns = self.memory.stats()
        print(f"  Граф знаний    : {ns['nodes']} узлов, {ns['edges']} связей")
        print(f"  Конституция    : {len(CONSTITUTION)} принципов")
        print("  Готово.")

    def cmd_demo(self) -> None:
        print_banner("Загрузка демонстрационных данных")
        # источники
        demo_sources = [
            ("Причинная механика (1958)", "Н. А. Козырев", "1958",
             None, None, "book", "VERIFIED",
             "Раннее изложение теории и экспериментальной программы."),
            ("The Secret Doctrine (1888)", "H. P. Blavatsky", "1888",
             None, None, "book", "VERIFIED",
             "Первое издание основного труда теософии."),
            ("Куранты Спасской башни: остановка 6 ноября 2026", "Interfax",
             "2026-11-06", "https://interfax.ru", None, "news", "VERIFIED",
             "Плановое техобслуживание до 16 ноября."),
            ("BTI 2026 — Russia Country Report", "Bertelsmann Stiftung",
             "2026", None, None, "report", "SUPPORTED",
             "Анализ политической системы России."),
            ("Neural correlates of perceptual biases in duration perception",
             "Shirzhiyan, Glasauer", "2026-11-02", None,
             "10.1152/jn.00440.2025", "article", "VERIFIED",
             "Нейронные корреляты искажений восприятия длительности."),
        ]
        for s in demo_sources:
            self.archive.add_source(
                title=s[0], author=s[1], date_str=s[2], url=s[3],
                doi=s[4], src_type=s[5], evidence=s[6], summary=s[7],
            )
        print(f"  Добавлено источников: {len(demo_sources)}")

        # граф
        for n in DEMO_NODES:
            self.memory.upsert_node(n)
        for e in DEMO_EDGES:
            self.memory.add_edge(e)
        ns = self.memory.stats()
        print(f"  Граф знаний: {ns['nodes']} узлов, {ns['edges']} связей")

        # история
        added = self.history.import_csv(DEMO_HISTORY_CSV)
        print(f"  Исторических рядов импортировано: {added}")

        # KZ-01 демо-запуск
        run_id = "KZ-01-DEMO-001"
        raw = json.dumps({"demo": True, "created": now_iso()}).encode()
        self.lab.register_run(run_id, "engine_off", raw,
                              notes="Демонстрационный запуск, не реальный эксперимент")
        for i in range(5):
            m = KZ01Measurement(
                run_id=run_id, mode="engine_off",
                timestamp=now_iso(),
                temperature_c=22.0 + i * 0.1,
                vibration_rms=0.012 + i * 0.001,
                emf_uv=0.5 + i * 0.05,
                tilt_mrad=0.001,
                weight_delta_mg=0.0,
                notes="демо",
            )
            self.lab.add_measurement(m)
        print(f"  KZ-01 демо-запуск зарегистрирован: {run_id}")
        print("  Готово.")

    def cmd_search(self, query: str) -> None:
        print_banner(f"Поиск: {query!r}")
        results = self.archive.search(query)
        if not results:
            print("  Ничего не найдено.")
            return
        for r in results:
            print(f"  [{r['id']}] {r['title']}")
            print(f"      автор: {r['author'] or '-'} | "
                  f"уровень: {r['evidence']} | тип: {r['src_type']}")
            if r["summary"]:
                print(f"      {r['summary'][:120]}")

    def cmd_graph_search(self, query: str) -> None:
        print_banner(f"Граф знаний: {query!r}")
        nodes = self.memory.search_nodes(query)
        if not nodes:
            print("  Узлы не найдены.")
            return
        for n in nodes:
            print(f"  [{n.id}] ({n.kind}) {n.label}")
            nb = self.memory.neighbors(n.id, max_depth=1)
            edges = nb.get(n.id, {}).get("edges", [])
            for e in edges[:8]:
                print(f"      -- {e['relation']} --> {e['to']}  "
                      f"[{e['evidence']}]")

    def cmd_history_query(self, indicator: str, geography: str = "Russia") -> None:
        print_banner(f"Временной ряд: {indicator} / {geography}")
        rows = self.history.query(indicator, geography)
        if not rows:
            print("  Ряд не найден.")
            return
        for r in rows:
            print(f"  {r['year']}  {r['value']!s:>8}  {r['unit'] or ''}")

    def cmd_kz_list(self) -> None:
        print_banner("KZ-01: список запусков")
        runs = self.lab.list_runs()
        if not runs:
            print("  Запусков нет.")
            return
        for r in runs:
            print(f"  {r['run_id']}  mode={r['mode']}  "
                  f"hash={r['raw_hash'][:12]}…  {r['created_at']}")

    def cmd_kz_summary(self, run_id: str) -> None:
        print_banner(f"KZ-01 сводка: {run_id}")
        s = self.lab.run_summary(run_id)
        if not s:
            print("  Запуск не найден.")
            return
        print(json.dumps(s, ensure_ascii=False, indent=2))

    def cmd_audit(self) -> None:
        print_banner("Журнал аудита (последние 20)")
        for r in self.archive.audit_history(20):
            print(f"  {r['created_at']}  {r['action']:<18} "
                  f"src={r['source_id']}  {r['detail']}")

    def cmd_constitution(self) -> None:
        print_banner(f"{PROJECT_NAME} — Конституция")
        for line in CONSTITUTION:
            print(f"  {line}")

    def cmd_status(self) -> None:
        print_banner(f"{PROJECT_NAME} v{VERSION} — статус")
        print(f"  Каталог данных : {self.data_dir}")
        print(f"  База данных    : {self.db}  ({self.db.stat().st_size} байт)"
              if self.db.exists() else "  База данных    : (не создана)")
        print(f"  Источников     : {self.archive.count()}")
        ns = self.memory.stats()
        print(f"  Граф знаний    : {ns['nodes']} узлов, {ns['edges']} связей")
        print(f"  Индикаторов    : {len(self.history.indicators())}")
        print(f"  KZ-01 запусков : {len(self.lab.list_runs())}")

    def cmd_export(self, out_path: Path) -> None:
        print_banner(f"Экспорт состояния в {out_path}")
        payload = {
            "project": PROJECT_NAME,
            "version": VERSION,
            "generated_at": now_iso(),
            "sources_count": self.archive.count(),
            "graph": self.memory.stats(),
            "history_indicators": self.history.indicators(),
            "kz_runs": self.lab.list_runs(),
            "constitution": CONSTITUTION,
        }
        out_path = Path(out_path)
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"  Сохранено: {out_path}")

    def close(self) -> None:
        self.archive.close()
        self.memory.close()
        self.history.close()
        self.lab.close()


# ============================================================================
# МОДУЛЬ 8: ТЕСТЫ
# ============================================================================

class ChronosTests(unittest.TestCase):
    """Встроенные автоматические тесты."""

    def setUp(self) -> None:
        import tempfile
        self.tmp = Path(tempfile.mkdtemp(prefix="chronos_test_"))
        self.db = self.tmp / "test.db"

    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    # ---------- SourceArchive ----------
    def test_archive_add_and_search(self):
        a = SourceArchive(self.db)
        sid = a.add_source(title="Квантовая стрела времени",
                           author="Garcia-Pintos",
                           src_type="article",
                           evidence="VERIFIED",
                           summary="Управление временной асимметрией")
        self.assertGreater(sid, 0)
        self.assertEqual(a.count(), 1)
        res = a.search("квантовая")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], sid)
        a.close()

    def test_archive_evidence_validation(self):
        a = SourceArchive(self.db)
        sid = a.add_source(title="X", src_type="article")
        with self.assertRaises(ValueError):
            a.update_evidence(sid, "NOT_A_LEVEL")
        a.close()

    def test_archive_audit(self):
        a = SourceArchive(self.db)
        a.add_source(title="Y", src_type="article")
        log = a.audit_history(5)
        self.assertGreaterEqual(len(log), 1)
        a.close()

    # ---------- AeternaMemory ----------
    def test_graph_upsert_and_neighbors(self):
        g = AeternaMemory(self.db)
        g.upsert_node(KnowledgeNode("p:koz", "person", "Козырев"))
        g.upsert_node(KnowledgeNode("t:cm", "text", "Причинная механика"))
        g.add_edge(KnowledgeEdge("p:koz", "t:cm", "authored", "VERIFIED"))
        nb = g.neighbors("p:koz", max_depth=1)
        self.assertIn("p:koz", nb)
        self.assertIn("t:cm", nb)
        g.close()

    def test_graph_edge_evidence(self):
        g = AeternaMemory(self.db)
        g.upsert_node(KnowledgeNode("a", "person", "A"))
        g.upsert_node(KnowledgeNode("b", "person", "B"))
        with self.assertRaises(ValueError):
            g.add_edge(KnowledgeEdge("a", "b", "knows", "WRONG"))
        g.close()

    # ---------- RussiaHistoria ----------
    def test_history_import_and_query(self):
        h = RussiaHistoria(self.db)
        csv_text = ("year,indicator,geography,value,unit,source_ref,notes\n"
                    "2000,population,Russia,146.0,mln,X,\n"
                    "2010,population,Russia,142.9,mln,X,\n")
        added = h.import_csv(csv_text)
        self.assertEqual(added, 2)
        rows = h.query("population")
        self.assertEqual(len(rows), 2)
        self.assertEqual(h.indicators(), ["population"])
        h.close()

    # ---------- KozyrevLab ----------
    def test_kz_register_and_measure(self):
        lab = KozyrevLab(self.db)
        raw = b"demo"
        h = lab.register_run("R1", "engine_off", raw)
        self.assertEqual(len(h), 64)
        m = KZ01Measurement(run_id="R1", mode="engine_off",
                            timestamp=now_iso(),
                            temperature_c=22.0, vibration_rms=0.01,
                            emf_uv=0.5, tilt_mrad=0.001,
                            weight_delta_mg=0.0)
        lab.add_measurement(m)
        s = lab.run_summary("R1")
        self.assertEqual(s["n_measurements"], 1)
        self.assertAlmostEqual(s["avg_temperature_c"], 22.0)
        lab.close()

    # ---------- OCR ----------
    def test_ocr_text(self):
        p = self.tmp / "sample.txt"
        p.write_text("Привет, ХРОНОС!", encoding="utf-8")
        text, status = OcrArchive.extract(p)
        self.assertEqual(status, "ok")
        self.assertIn("ХРОНОС", text)

    def test_ocr_html(self):
        p = self.tmp / "sample.html"
        p.write_text("<p>Текст <b>жирный</b></p>", encoding="utf-8")
        text, status = OcrArchive.extract(p)
        self.assertEqual(status, "html_cleaned")
        self.assertNotIn("<", text)

    def test_ocr_unsupported(self):
        p = self.tmp / "sample.pdf"
        p.write_bytes(b"%PDF-1.4 fake")
        text, status = OcrArchive.extract(p)
        self.assertEqual(status, "unsupported")
        self.assertEqual(text, "")

    # ---------- CLI интеграция ----------
    def test_cli_init_demo_status(self):
        cli = ChronosCLI(self.tmp / "data")
        cli.cmd_init()
        cli.cmd_demo()
        cli.cmd_status()
        cli.cmd_search("Козырев")
        cli.cmd_graph_search("kozyrev")
        cli.cmd_history_query("population")
        cli.cmd_kz_list()
        cli.cmd_kz_summary("KZ-01-DEMO-001")
        cli.cmd_audit()
        cli.cmd_constitution()
        out = self.tmp / "export.json"
        cli.cmd_export(out)
        self.assertTrue(out.exists())
        cli.close()


# ============================================================================
# ТОЧКА ВХОДА
# ============================================================================

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="chronos_omega_v04",
        description="ХРОНОС Ω v0.4.0 — единый исследовательский скрипт",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Примеры:
          python chronos_omega_v04.py init
          python chronos_omega_v04.py demo
          python chronos_omega_v04.py status
          python chronos_omega_v04.py search "Козырев"
          python chronos_omega_v04.py graph-search blavatsky
          python chronos_omega_v04.py history population
          python chronos_omega_v04.py kz-list
          python chronos_omega_v04.py kz-summary KZ-01-DEMO-001
          python chronos_omega_v04.py audit
          python chronos_omega_v04.py export state.json
          python chronos_omega_v04.py constitution
          python chronos_omega_v04.py tests
        """),
    )
    p.add_argument("--data-dir", default=DEFAULT_DATA_DIR,
                   help="каталог данных (по умолчанию chronos_data)")
    sub = p.add_subparsers(dest="cmd")

    sub.add_parser("init", help="инициализация проекта")
    sub.add_parser("demo", help="загрузка демонстрационных данных")
    sub.add_parser("status", help="текущее состояние")

    sp = sub.add_parser("search", help="полнотекстовый поиск по источникам")
    sp.add_argument("query")

    sp = sub.add_parser("graph-search", help="поиск по графу знаний")
    sp.add_argument("query")

    sp = sub.add_parser("history", help="исторический временной ряд")
    sp.add_argument("indicator")
    sp.add_argument("--geography", default="Russia")

    sub.add_parser("kz-list", help="список запусков KZ-01")

    sp = sub.add_parser("kz-summary", help="сводка запуска KZ-01")
    sp.add_argument("run_id")

    sub.add_parser("audit", help="журнал аудита")
    sub.add_parser("constitution", help="конституция проекта")

    sp = sub.add_parser("export", help="экспорт состояния в JSON")
    sp.add_argument("out")

    sub.add_parser("tests", help="запуск встроенных тестов")
    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.cmd:
        parser.print_help()
        return 0

    if args.cmd == "tests":
        suite = unittest.TestLoader().loadTestsFromTestCase(ChronosTests)
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        return 0 if result.wasSuccessful() else 1

    cli = ChronosCLI(data_dir=args.data_dir)
    try:
        if args.cmd == "init":
            cli.cmd_init()
        elif args.cmd == "demo":
            cli.cmd_demo()
        elif args.cmd == "status":
            cli.cmd_status()
        elif args.cmd == "search":
            cli.cmd_search(args.query)
        elif args.cmd == "graph-search":
            cli.cmd_graph_search(args.query)
        elif args.cmd == "history":
            cli.cmd_history_query(args.indicator, args.geography)
        elif args.cmd == "kz-list":
            cli.cmd_kz_list()
        elif args.cmd == "kz-summary":
            cli.cmd_kz_summary(args.run_id)
        elif args.cmd == "audit":
            cli.cmd_audit()
        elif args.cmd == "constitution":
            cli.cmd_constitution()
        elif args.cmd == "export":
            cli.cmd_export(Path(args.out))
        else:
            parser.print_help()
    finally:
        cli.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())