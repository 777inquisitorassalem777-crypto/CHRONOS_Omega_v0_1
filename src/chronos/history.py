"""Historical time-series storage and validation."""
import csv, sqlite3
from pathlib import Path
from datetime import date

REQUIRED={'series_id','date','indicator','value','unit','geography','source_id','evidence_class'}
ALLOWED={'empirical','historical','interpretive','tradition','hypothesis','unsupported'}

class HistoryStore:
    def __init__(self, db_path):
        self.db=sqlite3.connect(db_path); self.db.execute('''CREATE TABLE IF NOT EXISTS observations (
            series_id TEXT, date TEXT, indicator TEXT, value REAL, unit TEXT, geography TEXT,
            source_id TEXT, evidence_class TEXT, note TEXT DEFAULT '', PRIMARY KEY(series_id,date,geography))'''); self.db.commit()
    def import_csv(self, path):
        inserted=0
        with open(path,encoding='utf-8-sig',newline='') as f:
            reader=csv.DictReader(f)
            if not REQUIRED.issubset(reader.fieldnames or []): raise ValueError(f'missing columns: {sorted(REQUIRED-set(reader.fieldnames or []))}')
            rows=[]
            for n,r in enumerate(reader,2):
                date.fromisoformat(r['date'])
                if r['evidence_class'] not in ALLOWED: raise ValueError(f'row {n}: invalid evidence_class')
                if not r['source_id'].strip(): raise ValueError(f'row {n}: source_id required')
                rows.append((r['series_id'],r['date'],r['indicator'],float(r['value']),r['unit'],r['geography'],r['source_id'],r['evidence_class'],r.get('note','')))
        with self.db:
            self.db.executemany('INSERT OR REPLACE INTO observations VALUES (?,?,?,?,?,?,?,?,?)',rows)
        return len(rows)
    def query(self, indicator, geography=None):
        sql='SELECT series_id,date,indicator,value,unit,geography,source_id,evidence_class,note FROM observations WHERE indicator=?'; args=[indicator]
        if geography: sql+=' AND geography=?'; args.append(geography)
        sql+=' ORDER BY date'
        return [dict(zip(['series_id','date','indicator','value','unit','geography','source_id','evidence_class','note'],r)) for r in self.db.execute(sql,args)]
