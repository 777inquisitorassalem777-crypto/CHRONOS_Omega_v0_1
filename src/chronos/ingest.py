"""Local source ingestion and full-text indexing (stdlib only)."""
from __future__ import annotations
import hashlib, json, sqlite3
from pathlib import Path
from datetime import datetime, timezone

SUPPORTED = {'.txt', '.md', '.csv', '.json', '.html', '.htm', '.pdf'}

def _extract(path: Path) -> str:
    if path.suffix.lower() == '.pdf':
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError('PDF text extraction requires optional dependency: pip install chronos-omega[pdf]') from exc
        reader = PdfReader(str(path))
        return '\n'.join(page.extract_text() or '' for page in reader.pages)
    raw = path.read_text(encoding='utf-8', errors='replace')
    if path.suffix.lower() in {'.html', '.htm'}:
        from html.parser import HTMLParser
        class Text(HTMLParser):
            def __init__(self): super().__init__(); self.parts=[]; self.skip=0
            def handle_starttag(self, tag, attrs):
                if tag in {'script','style','noscript'}: self.skip += 1
            def handle_endtag(self, tag):
                if tag in {'script','style','noscript'} and self.skip: self.skip -= 1
            def handle_data(self, data):
                if not self.skip: self.parts.append(data)
        parser=Text(); parser.feed(raw); return '\n'.join(parser.parts)
    return raw

class SourceIndex:
    def __init__(self, db_path: str | Path):
        self.db_path=Path(db_path); self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db=sqlite3.connect(self.db_path)
        self.db.execute('''CREATE TABLE IF NOT EXISTS documents (
            doc_id TEXT PRIMARY KEY, path TEXT NOT NULL, title TEXT NOT NULL,
            sha256 TEXT NOT NULL, content TEXT NOT NULL, indexed_at TEXT NOT NULL)''')
        try: self.db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(doc_id UNINDEXED,title,content)")
        except sqlite3.OperationalError: self.db.execute("CREATE INDEX IF NOT EXISTS documents_title_idx ON documents(title)")
        self.db.commit()

    def ingest_file(self, path: str | Path) -> dict:
        p=Path(path)
        if p.suffix.lower() not in SUPPORTED: raise ValueError(f'unsupported file type: {p.suffix}')
        content=_extract(p); digest=hashlib.sha256(content.encode()).hexdigest(); doc_id=digest[:16]
        title=p.stem
        with self.db:
            old=self.db.execute('SELECT doc_id FROM documents WHERE path=?',(str(p.resolve()),)).fetchone()
            if old:
                self.db.execute('DELETE FROM documents_fts WHERE doc_id=?',(old[0],))
                self.db.execute('DELETE FROM documents WHERE doc_id=?',(old[0],))
            self.db.execute('INSERT OR REPLACE INTO documents VALUES (?,?,?,?,?,?)',
                (doc_id,str(p.resolve()),title,digest,content,datetime.now(timezone.utc).isoformat()))
            try: self.db.execute('INSERT INTO documents_fts(doc_id,title,content) VALUES (?,?,?)',(doc_id,title,content))
            except sqlite3.OperationalError: pass
        return {'doc_id':doc_id,'title':title,'path':str(p),'sha256':digest,'characters':len(content)}

    def ingest_dir(self, directory: str | Path, recursive=True) -> list[dict]:
        root=Path(directory); files=root.rglob('*') if recursive else root.iterdir()
        return [self.ingest_file(p) for p in sorted(files) if p.is_file() and p.suffix.lower() in SUPPORTED]

    def search(self, query: str, limit=10) -> list[dict]:
        if not query.strip(): return []
        try:
            rows=self.db.execute('''SELECT d.doc_id,d.title,d.path, snippet(documents_fts,2,'[',']','…',18)
                FROM documents_fts JOIN documents d USING(doc_id) WHERE documents_fts MATCH ? LIMIT ?''',(query,limit)).fetchall()
        except sqlite3.OperationalError:
            rows=self.db.execute('SELECT doc_id,title,path,substr(content,1,300) FROM documents WHERE content LIKE ? OR title LIKE ? LIMIT ?',
                (f'%{query}%',f'%{query}%',limit)).fetchall()
        return [dict(doc_id=r[0],title=r[1],path=r[2],snippet=r[3]) for r in rows]

    def close(self): self.db.close()
