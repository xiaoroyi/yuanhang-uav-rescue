"""Four groups x four methods, independently from scratch, frozen 600s budgets."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys
import time
from benchmark_v2 import load, digest
from benchmark_v5 import V5
from pattern_v4 import V4
from support import PROJECT, dump, table

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',default='independent_600s_seed42')
    p.add_argument('--seconds',type=float,default=600);a=p.parse_args()
    base=V5/a.name;base.mkdir(exist_ok=False,parents=True);snapshot=base/'source_snapshot';snapshot.mkdir()
    names=['benchmark_v5.py','matrix_v5.py','benchmark_v4.py','benchmark_v2.py','benchmark.py',
        'pattern_v4.py','master_v2.py','joint_v4.py','legacy_master.py','legacy_routes.py',
        'legacy_validate.py','legacy_validate_q3.py','legacy_radio.py','legacy_terrain.py',
        'legacy_sites.py','legacy_atoms.py','support.py']
    sources={}
    for name in names:
        src=Path(__file__).with_name(name);(snapshot/name).write_bytes(src.read_bytes());sources[name]=digest(src)
    protocol=dict(task='EXP-C06',started_at=datetime.now(timezone.utc).isoformat(),questions=['Q2','Q3'],
        objectives=['time','energy'],methods=['greedy','aco','alns','cp_sat'],seed=42,
        seconds_per_configuration=a.seconds,checkpoints=[180,600],max_processes=8,cp_workers=1,
        supplied_initial_solution=False,supplied_warm_start=False,paper_solution_used=False,
        source_sha256=sources,candidate_sha256={n:digest(V4/n) for n in ['pool_q2.json','pool_q3.json','sites.json','atoms.json']},
        initialization='No feasible initial or hints. Greedy/ACO start empty; ALNS builds its own first solution within budget; CP-SAT warm=None.',
        energy_caps=dict(Q2=6000,Q3=5939.9),time_caps=dict(Q2=None,Q3=None),
        zero_station_lateness=True,original_physics_and_resources=True,relay_slots=6,
        timing='Physical input/candidate loading excluded; first-solution construction, CP model building, decoding and improvement included. Final independent validation excluded.',
        no_solution_semantics='NO_FEASIBLE_SOLUTION_FOUND means no validated solution within budget, not proof of infeasibility.',
        limits='Single instance/seed; finite independently generated physical route/site candidates retained from v4; no complete schedule imported. Q3 heuristics use CP scheduling/communication decoding. Paper budgets/candidate space differ.')
    dump(base/'protocol.json',protocol);began=time.perf_counter();records=[];errors=[];active={}
    def invoke(q,o,m):
        label=f'{q}_{o}_{m}';cmd=[sys.executable,'-u',str(Path(__file__).with_name('benchmark_v5.py')),
            '--question',q,'--objective',o,'--method',m,'--seconds',str(a.seconds),
            '--checkpoints','180,600','--name',a.name+'/'+label]
        with (base/f'{label}.txt').open('w',encoding='utf-8') as log:
            proc=subprocess.Popen(cmd,cwd=PROJECT,stdout=log,stderr=subprocess.STDOUT,
                env={**os.environ,'PYTHONIOENCODING':'utf-8','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
            active[label]=proc.pid;dump(base/f'{label}_process.json',dict(pid=proc.pid,started_at=datetime.now(timezone.utc).isoformat()))
            print('START',label,proc.pid,flush=True)
            try:code=proc.wait(timeout=a.seconds+180)
            except subprocess.TimeoutExpired:
                proc.kill();proc.wait();return dict(error=True,run=label,reason='process_timeout')
        path=base/label/'run.json'
        if code!=0 or not path.exists():return dict(error=True,run=label,returncode=code)
        return load(path)
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures=[executor.submit(invoke,q,o,m) for q in ['Q2','Q3'] for o in ['time','energy'] for m in ['greedy','aco','alns','cp_sat']]
        for future in as_completed(futures):
            try:r=future.result()
            except Exception as exc:r=dict(error=True,reason=repr(exc))
            if r.get('error'):errors.append(r);print('ERROR',r,flush=True)
            else:
                records.append(r);print('COMPLETE',r['question'],r['objective'],r['method'],r['checkpoints'][-1]['status'],flush=True)
            dump(base/'results.json',sorted(records,key=lambda r:(r['question'],r['objective'],r['method'])))
            dump(base/'progress.json',dict(completed=len(records),total=16,errors=errors,wall_s=time.perf_counter()-began))
    rows=[]
    for r in records:
        for c in r['checkpoints']:
            rows.append(dict(question=r['question'],objective=r['objective'],method=r['method'],
                checkpoint_s=c['checkpoint_s'],status=c['status'],search_wall_s=r['search_wall_s'],
                **(c['metrics'] or dict(completion_s=None,energy_kwh=None,transport_sorties=None,relay_sorties=None))))
    table(base/'results.csv',rows)
    dump(base/'completion.json',dict(complete=len(records)==16 and not errors,completed_runs=len(records),errors=errors,
        experiment_wall_s=time.perf_counter()-began,sum_search_wall_s=sum(r['search_wall_s'] for r in records),
        feasible_final_runs=sum(r['checkpoints'][-1]['metrics'] is not None for r in records)))
    assert len(records)==16 and not errors

if __name__=='__main__':main()
