"""Eight aligned energy runs, 4 isolated single-worker processes, frozen protocol."""
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import zipfile
from benchmark_v3 import V3,CAPS
from benchmark_v2 import V1,load,digest
from support import PROJECT,dump,table

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',default='aligned_600s_seed42');p.add_argument('--seconds',type=float,default=600)
    p.add_argument('--checkpoints',default='180,600');a=p.parse_args();base=V3/a.name;base.mkdir(exist_ok=False,parents=True)
    source=base/'source_snapshot';source.mkdir();files={}
    names=['benchmark_v3.py','matrix_v3.py','benchmark_v2.py','benchmark.py','master_v2.py','joint_v2.py','legacy_master.py',
        'legacy_routes.py','legacy_validate.py','legacy_validate_q3.py','legacy_radio.py','legacy_terrain.py','legacy_sites.py','legacy_atoms.py','support.py']
    for name in names:
        original=Path(__file__).with_name(name);raw=original.read_bytes();(source/name).write_bytes(raw);files[name]=hashlib.sha256(raw).hexdigest()
    archive=PROJECT/'references/modeling/verified-release-code-and-results.zip'
    with zipfile.ZipFile(archive) as z:
        name=next(n for n in z.namelist() if n.endswith('f455d04d2d9c7614ab/input_contract.json'))
        raw=z.read(name);(base/'historical_q3_input_contract.json').write_bytes(raw)
    protocol=dict(task='EXP-C03',questions=['Q2','Q3'],objective='energy',methods=['greedy','aco','alns','cp_sat'],caps=CAPS,
        seed=42,seconds_per_configuration=a.seconds,checkpoints=[float(v) for v in a.checkpoints.split(',')],
        max_processes=4,cp_workers=1,source_sha256=files,
        candidate_sha256={name:digest(V1/name) for name in ['pool_q2.json','pool_q3.json','stations.json','atoms.json']},
        question_2_cap_source=dict(type='user_choice',verbatim='统一100分钟（6000秒）；论文节能方案满足，作为新的统一对照口径（推荐）',
            original_paper_cap_recovered=False,meaning='new common benchmark horizon, not claimed as recovered original solver cap'),
        question_3_caps_source=dict(archive=str(archive.relative_to(PROJECT)),member=name,sha256=hashlib.sha256(raw).hexdigest(),
            max_C=5939.9,max_E=68.9999,max_transport=23,relay_slots=4),
        no_paper_routes_schedules_or_objective_values_used_for_search=True,
        initializer='Fresh time-scored greedy construction inside each search budget. Outside-cap transport plans are phase-I guides only, never feasible checkpoints.',
        algorithm_adaptation='Necessary work/energy/count screening; ALNS/ACO use phase-I violation guidance until feasible; Q2 constructive methods may call shared fixed-group CP scheduling (12s maximum) if list schedule exceeds horizon but work bound allows it. Q3 also uses shared joint CP scheduling.',
        preserved_time_runs='evidence/contest-baselines-v2/main_600s_seed42: eight time-objective runs unchanged; not rerun or charged as new runs.',
        limits='Only constraints/metric definitions aligned; 850-route pool, 21 sites and search budgets still differ from historical paper; single seed. Failure is budget/pool-limited, not original infeasibility.',
        platform=platform.platform(),python=sys.version)
    dump(base/'protocol.json',protocol);began=time.perf_counter();records=[];errors=[]
    def invoke(q,m):
        label=f'{q}_energy_{m}';cmd=[sys.executable,'-u',str(Path(__file__).with_name('benchmark_v3.py')),
            '--question',q,'--method',m,'--seconds',str(a.seconds),'--checkpoints',a.checkpoints,'--name',a.name+'/'+label]
        with (base/f'{label}.txt').open('w',encoding='utf-8') as f:
            run=subprocess.run(cmd,cwd=PROJECT,stdout=f,stderr=subprocess.STDOUT,timeout=a.seconds+180,
                env={**os.environ,'PYTHONIOENCODING':'utf-8','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1'})
        path=base/label/'run.json'
        return load(path) if run.returncode==0 and path.exists() else dict(error=True,run=label,returncode=run.returncode)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures=[executor.submit(invoke,q,m) for q in ['Q2','Q3'] for m in ['greedy','aco','alns','cp_sat']]
        for future in as_completed(futures):
            result=future.result()
            if result.get('error'):errors.append(result)
            else:records.append(result);print('COMPLETE',result['question'],result['method'],[(c['checkpoint_s'],c['status'],c['metrics']) for c in result['checkpoints']],flush=True)
            dump(base/'results.json',sorted(records,key=lambda r:(r['question'],r['method'])))
            dump(base/'progress.json',dict(completed=len(records),errors=errors,total=8,wall_s=time.perf_counter()-began))
    rows=[]
    for r in records:
        for c in r['checkpoints']:
            metrics=c['metrics'] or dict(completion_s=None,energy_kwh=None,transport_sorties=None,relay_sorties=None,boxes=None,unique_boxes=None,late_boxes=None,hard_violations=None,minimum_hard_slack_s=None)
            rows.append(dict(question=r['question'],method=r['method'],checkpoint_s=c['checkpoint_s'],status=c['status'],
                search_wall_s=r['search_wall_s'],**metrics))
    table(base/'results.csv',rows)
    dump(base/'completion.json',dict(complete=len(records)==8 and not errors,completed_runs=len(records),errors=errors,
        experiment_wall_s=time.perf_counter()-began,sum_search_wall_s=sum(r['search_wall_s'] for r in records),
        feasible_final_runs=sum(r['checkpoints'][-1]['metrics'] is not None for r in records)))
    if errors:raise RuntimeError(errors)

if __name__=='__main__':main()
