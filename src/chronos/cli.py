import argparse, json
from pathlib import Path
from .ingest import SourceIndex
from .history import HistoryStore
from .kozyrev import write_registration
from .graph import KnowledgeGraph, Node, Edge

def main():
    p=argparse.ArgumentParser(prog='chronos',description='CHRONOS Ω research system')
    sub=p.add_subparsers(dest='cmd',required=True)
    a=sub.add_parser('ingest'); a.add_argument('path'); a.add_argument('--db',default='data/index/chronos.sqlite')
    s=sub.add_parser('search'); s.add_argument('query'); s.add_argument('--db',default='data/index/chronos.sqlite'); s.add_argument('--limit',type=int,default=10)
    h=sub.add_parser('history-import'); h.add_argument('csv'); h.add_argument('--db',default='data/index/history.sqlite')
    q=sub.add_parser('history-query'); q.add_argument('indicator'); q.add_argument('--geography'); q.add_argument('--db',default='data/index/history.sqlite')
    k=sub.add_parser('kz01-register'); k.add_argument('--out',default='data/kozyrev/KZ-01_preregistration.json')
    g=sub.add_parser('graph-search'); g.add_argument('term'); g.add_argument('--graph',default='data/graph/aeterna.json')
    args=p.parse_args()
    if args.cmd=='ingest':
        idx=SourceIndex(args.db); path=Path(args.path); result=idx.ingest_dir(path) if path.is_dir() else [idx.ingest_file(path)]; print(json.dumps(result,ensure_ascii=False,indent=2)); idx.close()
    elif args.cmd=='search':
        idx=SourceIndex(args.db); print(json.dumps(idx.search(args.query,args.limit),ensure_ascii=False,indent=2)); idx.close()
    elif args.cmd=='history-import':
        store=HistoryStore(args.db); print(f'Imported {store.import_csv(args.csv)} observations'); store.db.close()
    elif args.cmd=='history-query':
        store=HistoryStore(args.db); print(json.dumps(store.query(args.indicator,args.geography),ensure_ascii=False,indent=2)); store.db.close()
    elif args.cmd=='kz01-register':
        r=write_registration(args.out); print(f'{r.protocol_id} written: {args.out} ({r.status})')
    elif args.cmd=='graph-search':
        data=json.loads(Path(args.graph).read_text(encoding='utf-8')); term=args.term.casefold()
        hits=[n for n in data.get('nodes',[]) if term in (n.get('label','')+' '+n.get('id','')+' '+json.dumps(n.get('properties',{}),ensure_ascii=False)).casefold()]
        print(json.dumps(hits,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
