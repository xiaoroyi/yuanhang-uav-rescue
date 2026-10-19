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
from benchmark_v4 import CAPS
from pattern_v4 import V4 as V3
from benchmark_v2 import V1,load,digest
from support import PROJECT,dump,table

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',default='corrected_600s_seed42');p.add_argument('--seconds',type=float,default=600)
    p.add_argument('--checkpoints',default='180,600');a=p.parse_args();base=V3/a.name;base.mkdir(exist_ok=False,parents=True)
    source=base/'source_snapshot';source.mkdir();files={}
    names=['benchmark_v4.py','matrix_v4.py','pattern_v4.py','prepare_joint_v4.py','bootstrap_radio_v4.py','dense_sites_v4.py','add_variant_v4.py','window_bootstrap_v4.py','tighten_initial_v4.py','master_v4.py','benchmark_v2.py','benchmark.py','master_v2.py','joint_v4.py','joint_v2.py','legacy_master.py',
        'legacy_routes.py','legacy_validate.py','legacy_validate_q3.py','legacy_radio.py','legacy_terrain.py','legacy_sites.py','legacy_atoms.py','support.py']
    for name in names:
        original=Path(__file__).with_name(name);raw=original.read_bytes();(source/name).write_bytes(raw);files[name]=hashlib.sha256(raw).hexdigest()
    for q in ['q2','q3']:
        audit=load(V3/f'common_{q}_validation.json')
        assert audit['status']=='passed' and audit['solution_sha256']==digest(V3/f'common_{q}.json')
        from benchmark_v4 import cap_errors
        assert not cap_errors(load(V3/f'common_{q}.json'),q.upper())
    protocol=dict(task='EXP-C05',questions=['Q2','Q3'],objective='energy',methods=['greedy','aco','alns','cp_sat'],caps=CAPS,
        seed=42,seconds_per_configuration=a.seconds,checkpoints=[float(v) for v in a.checkpoints.split(',')],
        max_processes=4,cp_workers=1,source_sha256=files,
        candidate_sha256={name:digest(V3/name) for name in ['pool_q2.json','pool_q3.json','sites.json','atoms.json','common_q2.json','common_q3.json','classes.json','patterns.json','common_q2_validation.json','common_q3_validation.json']},
        question_2_cap_source=dict(type='user_choice',verbatim='统一100分钟（6000秒）；论文节能方案满足，作为新的统一对照口径（推荐）',
            original_paper_cap_recovered=False,meaning='new common benchmark horizon, not claimed as recovered original solver cap'),
        question_3_caps_source=dict(max_C=5939.9,max_E=None,max_transport=None,relay_slots=6,
            reason='Retain declared comparison horizon; remove local-search outcome thresholds. Slots are a shared finite modeling setting, distinct from physical 2 relay aircraft/6 components.'),
        no_paper_routes_schedules_or_objective_values_used_for_search=True,
        initializer='Shared independently generated and fully validated feasible initial. Common preprocessing cost separately disclosed, excluded from each 600s improvement budget. Initial retention is not a method-specific achievement.',
        algorithm_adaptation='Cap-aware EDF construction/repair, greedy randomized restarts, ACO pheromones over up to 32 candidates, adaptive three-operator ALNS, Q3 shared 10s CP decoder; CP-SAT same pool and warm initial. All labels disclose shared feasibility support.',
        preserved_time_runs='evidence/contest-baselines-v2/main_600s_seed42: eight time-objective runs unchanged; not rerun or charged as new runs.',
        limits='Finite public route/site pool, one seed, shared initialization, historical paper budgets differ; compare current method improvement conditional on same common inputs, not stand-alone pure algorithm performance.',
        common_preprocessing=load(V3/'preparation/summary.json'),
        platform=platform.platform(),python=sys.version)
    dump(base/'protocol.json',protocol);began=time.perf_counter();records=[];errors=[]
    def invoke(q,m):
        label=f'{q}_energy_{m}';cmd=[sys.executable,'-u',str(Path(__file__).with_name('benchmark_v4.py')),
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
