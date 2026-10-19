"""Four independent OS processes, one solver worker each, equal wall limits."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import hashlib
from support import EVIDENCE, PROJECT, dump, table

NAME='matrix_180s_seed42'

def main():
    start=time.perf_counter()
    base=EVIDENCE/NAME
    base.mkdir(exist_ok=False)
    tasks=[(q,o,m) for q in ['Q2','Q3'] for o in ['time','energy'] for m in ['greedy','aco','alns','cp_sat']]
    # Interleave questions and objectives so all conditions start early.
    tasks.sort(key=lambda t:(['greedy','aco','alns','cp_sat'].index(t[2]),t[0],t[1]))
    protocol=dict(budget_per_run_s=180,seed=42,max_concurrent_processes=4,cp_workers_per_process=1,
        budget_kind='wall clock including construction and model building; final independent validation excluded',
        greedy_q3_decoder_limit_s=20,meta_q3_first_decoder_limit_s=20,meta_q3_later_decoder_limit_s=12,
        questions=['Q2','Q3'],objectives=['time','energy'],methods=['greedy','aco','alns','cp_sat'],
        cap_on_completion_s=None,require_zero_station_lateness=True,
        paper_reference='Historical only, not same-budget; never supplied as initial solution or candidate routes',
        q3_names='Greedy + CP scheduling; ACO + CP scheduling; ALNS + CP scheduling; finite-pool CP-SAT',
        limits='One seed only. 850 routes, max 3 stops, 21 independent relay sites, up to 4 relay sorties. No global-optimality claim.',
        partial_pilot='main_180s_seed42 was interrupted while changing to concurrent orchestration; excluded entirely from final matrix',
        environment=dict(python=sys.version,platform=platform.platform(),logical_cpu_count=os.cpu_count(),
            processor=os.environ.get('PROCESSOR_IDENTIFIER'),packages={p:importlib.metadata.version(p) for p in ['ortools','numpy','scipy','numba','openpyxl','pyproj','shapely']}),
        source_sha256={str(p.relative_to(PROJECT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')})
    dump(base/'protocol.json',protocol)
    def invoke(task):
        q,o,m=task;folder=f'{q}_{o}_{m}'
        args=[sys.executable,'-u',str(Path(__file__).with_name('benchmark.py')),'one',
              '--question',q,'--objective',o,'--method',m,'--seconds','180','--seed','42','--name',f'{NAME}/{folder}']
        with (base/f'{folder}.txt').open('w',encoding='utf-8') as f:
            result=subprocess.run(args,cwd=PROJECT,stdout=f,stderr=subprocess.STDOUT,
                env={**os.environ,'PYTHONIOENCODING':'utf-8','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'},
                timeout=360)
        return folder,result.returncode
    records=[];failures=[]
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures=[executor.submit(invoke,t) for t in tasks]
        for fut in as_completed(futures):
            folder,code=fut.result()
            path=base/folder/'run.json'
            if code!=0 or not path.exists():
                failures.append(dict(folder=folder,returncode=code))
            else:
                r=json.loads(path.read_text(encoding='utf-8'));records.append(r)
                print('FINISHED',folder,r['status'],r['metrics'],flush=True)
            dump(base/'results.json',sorted(records,key=lambda r:(r['question'],r['objective'],r['method'])))
            dump(base/'progress.json',dict(completed=len(records),failed=failures,total=16,wall_s=time.perf_counter()-start))
    keys=['question','objective','method','seed','status','budget_s','search_wall_s','total_wall_s']
    metrics=['completion_s','energy_kwh','transport_sorties','relay_sorties','boxes','unique_boxes','late_boxes','hard_violations','minimum_hard_slack_s']
    table(base/'results.csv',[{k:r[k] for k in keys}|{k:(r['metrics'] or {}).get(k) for k in metrics} for r in records])
    dump(base/'completion.json',dict(complete=len(records)==16 and not failures,failed=failures,
        experiment_wall_s=time.perf_counter()-start,sum_search_wall_s=sum(r['search_wall_s'] for r in records),
        sum_total_run_wall_s=sum(r['total_wall_s'] for r in records)))
    if failures:
        raise RuntimeError(failures)

if __name__=='__main__':
    main()
