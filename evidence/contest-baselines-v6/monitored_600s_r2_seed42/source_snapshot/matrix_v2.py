"""Run 16 conditions with 4 isolated single-worker processes; freeze sources."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from support import PROJECT,EVIDENCE as V1,dump,table

V2=PROJECT/'evidence/contest-baselines-v2'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--name',default='main_600s_seed42')
    parser.add_argument('--seconds',type=float,default=600);parser.add_argument('--checkpoints',default='180,600')
    parser.add_argument('--pilot',action='store_true');a=parser.parse_args()
    base=V2/a.name;base.mkdir(exist_ok=False,parents=True)
    start=time.perf_counter()
    methods=['greedy','aco','alns','cp_sat']
    tasks=[(q,o,m) for q in ['Q2','Q3'] for o in ['time','energy'] for m in methods]
    if a.pilot:tasks=[t for t in tasks if t[1]=='energy' or t[2]=='greedy']
    source=base/'source_snapshot';source.mkdir()
    names=['benchmark_v2.py','master_v2.py','joint_v2.py','benchmark.py','support.py','legacy_routes.py',
           'legacy_radio.py','legacy_terrain.py','legacy_sites.py','legacy_atoms.py','legacy_validate.py','legacy_validate_q3.py',
           'matrix_v2.py']
    sources={}
    for name in names:
        original=Path(__file__).with_name(name);raw=original.read_bytes();(source/name).write_bytes(raw)
        sources[name]=hashlib.sha256(raw).hexdigest()
    protocol=dict(questions=['Q2','Q3'],objectives=['time','energy'],methods=methods,seed=42,
        seconds_per_configuration=a.seconds,checkpoints=[float(x) for x in a.checkpoints.split(',')],
        same_uninterrupted_search_checkpoints=True,max_concurrent_processes=4,cp_workers_per_process=1,
        common_initial='Four independently rebuilt, fully validated repaired-greedy/EDF solutions shared by all methods, no paper results; construction cost reported separately.',
        common_initial_manifest=json.loads((V2/'common_initial/manifest.json').read_text(encoding='utf-8')),
        greedy_change='Dead-end restart with time/energy score-weight changes, then greedy multistart construction; no constraint relaxation.',
        frozen_candidate_files={p:hashlib.sha256((V1/p).read_bytes()).hexdigest() for p in ['pool_q2.json','pool_q3.json','stations.json','atoms.json']},
        source_sha256=sources,source_snapshot='source_snapshot/',
        task_count=len(tasks),checkpoint_semantics='Last physically reconstructed incumbent found no later than the threshold; callbacks record discovery time before extraction. Independent validation occurs after the search.',
        proof_scope='Finite 850-route/21-site/4-relay-slot model only; single seed; historical paper results remain external references.',
        environment=dict(python=sys.version,platform=platform.platform(),logical_cpu=os.cpu_count(),processor=os.environ.get('PROCESSOR_IDENTIFIER'),
            packages={name:importlib.metadata.version(name) for name in ['ortools','numpy','scipy','numba','openpyxl','pyproj','shapely']}))
    dump(base/'protocol.json',protocol)
    def invoke(task):
        q,o,m=task;folder=f'{q}_{o}_{m}'
        cmd=[sys.executable,'-u',str(Path(__file__).with_name('benchmark_v2.py')),'one','--question',q,
            '--objective',o,'--method',m,'--seconds',str(a.seconds),'--checkpoints',a.checkpoints,
            '--seed','42','--name',f'{a.name}/{folder}']
        with (base/f'{folder}.txt').open('w',encoding='utf-8') as f:
            result=subprocess.run(cmd,cwd=PROJECT,stdout=f,stderr=subprocess.STDOUT,
                timeout=a.seconds+180,env={**os.environ,'PYTHONIOENCODING':'utf-8','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
        path=base/folder/'run.json'
        if result.returncode!=0 or not path.exists():return dict(folder=folder,error=True,exit_code=result.returncode)
        return json.loads(path.read_text(encoding='utf-8'))
    records=[];failed=[]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures=[executor.submit(invoke,t) for t in tasks]
        for future in as_completed(futures):
            result=future.result()
            if result.get('error'):failed.append(result)
            else:
                records.append(result)
                print('COMPLETE',result['question'],result['objective'],result['method'],[(c['checkpoint_s'],c['metrics']) for c in result['checkpoints']],flush=True)
            dump(base/'results.json',sorted(records,key=lambda r:(r['question'],r['objective'],r['method'])))
            dump(base/'progress.json',dict(completed=len(records),failed=failed,total=len(tasks),wall_s=time.perf_counter()-start))
    rows=[]
    for r in records:
        for c in r['checkpoints']:
            rows.append({k:r[k] for k in ['question','objective','method','seed','budget_s','search_wall_s','total_wall_s']}|
                {k:c[k] for k in ['checkpoint_s','best_found_s','status','solution_sha256']}|c['metrics'])
    table(base/'results.csv',rows)
    dump(base/'completion.json',dict(complete=len(records)==len(tasks) and not failed,expected_runs=len(tasks),completed_runs=len(records),
        failed=failed,experiment_wall_s=time.perf_counter()-start,sum_search_wall_s=sum(r['search_wall_s'] for r in records),
        sum_total_wall_s=sum(r['total_wall_s'] for r in records)))
    if failed:raise RuntimeError(failed)

if __name__=='__main__':main()
