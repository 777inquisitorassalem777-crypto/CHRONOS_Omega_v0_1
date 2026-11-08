import csv, json
from pathlib import Path
from chronos.ingest import SourceIndex
from chronos.history import HistoryStore
from chronos.kozyrev import KZ01Registration, write_registration


def test_ingest_and_search(tmp_path):
    source=tmp_path/'note.md'; source.write_text('# Entropy\nThe arrow of time and entropy.',encoding='utf-8')
    idx=SourceIndex(tmp_path/'idx.sqlite')
    result=idx.ingest_file(source)
    assert result['sha256'] and idx.search('entropy')[0]['doc_id']==result['doc_id']
    idx.close()

def test_ingest_deduplicates_path(tmp_path):
    source=tmp_path/'note.txt'; source.write_text('first content')
    idx=SourceIndex(tmp_path/'idx.sqlite'); idx.ingest_file(source)
    source.write_text('second content'); idx.ingest_file(source)
    assert len(idx.db.execute('select * from documents').fetchall())==1
    idx.close()

def test_history_import_and_query(tmp_path):
    f=tmp_path/'history.csv'
    f.write_text('series_id,date,indicator,value,unit,geography,source_id,evidence_class,note\nS1,2000-01-01,population,10,million,Russia,S1,historical,archival series\n',encoding='utf-8')
    store=HistoryStore(tmp_path/'h.sqlite'); assert store.import_csv(f)==1
    assert store.query('population')[0]['value']==10
    store.db.close()

def test_history_rejects_missing_provenance(tmp_path):
    f=tmp_path/'bad.csv'
    f.write_text('series_id,date,indicator,value,unit,geography,source_id,evidence_class,note\nS1,2000-01-01,population,10,million,Russia,,historical,\n')
    store=HistoryStore(tmp_path/'h.sqlite')
    try:
        store.import_csv(f); assert False, 'expected ValueError'
    except ValueError as e: assert 'source_id required' in str(e)
    store.db.close()

def test_kz01_registration_is_explicitly_draft(tmp_path):
    out=tmp_path/'kz.json'; r=write_registration(out)
    data=json.loads(out.read_text())
    assert r.validate()==[] and data['status']=='DRAFT_NOT_PREREGISTERED'

