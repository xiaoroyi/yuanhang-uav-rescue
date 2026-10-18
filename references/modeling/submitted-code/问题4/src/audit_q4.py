from pathlib import Path
import sys,json,csv,hashlib,shutil
from decimal import Decimal
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]; PROJECT=ROOT.parent; OUT=ROOT/'results'; Q3=PROJECT/'问题3/results'
sys.path.insert(0,str(PROJECT/'问题3/src'))
from setup_q3 import inputs

def read(p):return json.loads(Path(p).read_text(encoding='utf-8'),parse_float=Decimal)
def rows(p):return list(csv.DictReader(Path(p).open(encoding='utf-8-sig',newline='')))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def default(x):
    if isinstance(x,Decimal):return str(x)
    if isinstance(x,Path):return str(x)
    if isinstance(x,set):return sorted(x)
    if hasattr(x,'numerator'):return str(x)
    raise TypeError(type(x))
def dump(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,default=default),encoding='utf-8')
def table(p,v):
    if not v:return
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(v[0]));w.writeheader();w.writerows({k:json.dumps(x,ensure_ascii=False,default=default) if isinstance(x,(list,dict)) else x for k,x in r.items()} for r in v)

def audit(replay=True):
    OUT.mkdir(parents=True,exist_ok=True)
    sol=read(Q3/'solution_q3.json');ints=rows(Q3/'communication_intervals_q3.csv');pts=rows(Q3/'communication_event_points_q3.csv')
    errors=[];by=defaultdict(list)
    for n,p in enumerate(pts):by[(p['sortie'],Decimal(p['time']))].append((n,p))
    for key,group in by.items():
        if len({p['source'] for _,p in group})!=1:errors.append(dict(code='duplicate_source',key=str(key),rows=group))
    # Adjacent phase boundaries can differ only by last-bit float arithmetic; flag source disagreement without merging resource times.
    near=[]
    for tid in {p['sortie'] for p in pts}:
        series=sorted((Decimal(p['time']),p['source'],p['phase']) for p in pts if p['sortie']==tid)
        for a,b in zip(series,series[1:]):
            if 0< b[0]-a[0] < Decimal('1e-8') and a[2]!=b[2]:
                near.append(dict(sortie=tid,a=a,b=b))
                if a[1]!=b[1]:errors.append(dict(code='near_duplicate_source',sortie=tid,a=a,b=b))
    trs={r['sortie']:r for r in sol['transport']}; rel={r['sortie']:r for r in sol['relay']}
    for r in ints+pts:
        if r['sortie'] not in trs or r['source'] not in {'G01',*rel}:errors.append(dict(code='source_id',row=r))
    # Exact serialization ledger; geometry validator replay deterministically chooses and certifies actual source records.
    selected_files=['solution_q3.json','communication_intervals_q3.csv','communication_event_points_q3.csv','communication_certificates.jsonl','deliveries_q3.csv','transport_trips_q3.csv','relay_trips_q3.csv','input_audit.json','config.json']
    manifest={'files':{str(Q3/f):sha(Q3/f) for f in selected_files},'q3_code':{str(p):sha(p) for p in (PROJECT/'问题3/src').glob('*.py')}}
    snapshot=OUT/'q3_snapshot';snapshot.mkdir(exist_ok=True)
    for f in selected_files:shutil.copy2(Q3/f,snapshot/f)
    replay_result=None;records_match=None
    if replay:
        from validate_q3 import run
        replaydir=OUT/'q3_replay';replaydir.mkdir(exist_ok=True);shutil.copy2(Q3/'solution_q3.json',replaydir/'solution_q3.json')
        replay_result=run(replaydir/'solution_q3.json',save=True)
        records_match={f:rows(Q3/f)==rows(replaydir/f) for f in ('communication_intervals_q3.csv','communication_event_points_q3.csv')}
        if not replay_result['summary']['valid']:errors.append(dict(code='q3_invalid'))
        if not all(records_match.values()):errors.append(dict(code='replay_actual_source_changed',detail=records_match))
    summary=dict(valid=not errors,errors=errors,interval_records=len(ints),event_records=len(pts),unique_exact_events=len(by),duplicated_event_records=len(pts)-len(by),near_duplicate_boundaries=near,all_actual_sources_single=True if not errors else False,replay= None if replay_result is None else replay_result['summary'],actual_records_replay_match=records_match)
    dump(OUT/'q3_snapshot_manifest.json',manifest);dump(OUT/'q3_interface_audit.json',summary)
    print(json.dumps(summary,ensure_ascii=False,default=default),flush=True)
    assert not errors,errors
    return sol,ints,pts

if __name__=='__main__':audit()
