"""Monitored independent search; all first-solution work is inside the budget."""
import argparse
from collections import defaultdict
import copy
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import random
import threading
import time
from benchmark_v2 import load, digest, key, solution_metrics, validate_solution
from benchmark import station_audit
from construction_v6 import Constructor
from window_constructor_v6 import WindowConstructor
from legacy_routes import Physics
from pattern_v4 import V4
from support import PROJECT
import master_v2
import master_v4
import joint_v4
import joint_v6

V6=PROJECT/'evidence/contest-baselines-v6'

def atomic(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+f'.{os.getpid()}.{threading.get_ident()}.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    for attempt in range(100):
        try:
            os.replace(temp,path);return
        except PermissionError:
            if attempt==99:raise
            time.sleep(.005)

def run(a):
    base=V6/a.name;base.mkdir(exist_ok=False,parents=True)
    q,o,m=a.question,a.objective,a.method
    began=time.perf_counter();deadline=began+a.seconds
    atomic(base/'clock.json',dict(started_perf=began,deadline_perf=deadline,budget_s=a.seconds,
        started_utc=datetime.now(timezone.utc).isoformat(),supplied_initial=False))
    phase='input_loading';attempts=decoders=callbacks=complete=0
    aco_iterations=alns_iterations=0
    first_repair_used=False
    best=None;trace=[];rejects=defaultdict(int);phase_started=began;ctor=None
    lock=threading.RLock();finished=threading.Event()
    cap={'Q2':6000.,'Q3':5939.9}[q] if o=='energy' else None
    targets=sorted(set(t for t in [30.,60.,180.,a.seconds] if t<=a.seconds))
    objectives=('C','E') if o=='time' else ('E','C')
    def progress():
        with lock:
            atomic(base/'search_progress.json',dict(question=q,objective=o,method=m,
                elapsed_s=time.perf_counter()-began,phase=phase,phase_elapsed_s=time.perf_counter()-phase_started,
                attempts=attempts,complete_constructions=complete,decoder_calls=decoders,callbacks=callbacks,
                aco_iterations=aco_iterations,alns_iterations=alns_iterations,
                first_solution_repair_used=first_repair_used,
                initialization='Each process constructs/repairs its own first solution inside its budget; no solution is imported.',
                constructor_stats=dict(ctor.stats) if ctor is not None else {},rejections=dict(rejects),
                has_incumbent=best is not None,trace=trace))
    def setphase(value):
        nonlocal phase,phase_started
        phase=value;phase_started=time.perf_counter();progress()
    def beat():
        while not finished.wait(2):progress()
    progress();threading.Thread(target=beat,daemon=True).start()
    P=Physics();pool=load(V4/f'pool_{q.lower()}.json');sites=load(V4/'sites.json');atoms=load(V4/'atoms.json')
    setphase('constructor_setup');ctor=Constructor(P,pool,cap);rng=random.Random(42)
    joint_v6.OUT=base/'decoders';joint_v6.OUT.mkdir()

    def retain(sol,info=None):
        nonlocal best,callbacks
        if sol is None:return False
        info=info or {};found=info.get('found_perf',time.perf_counter())-began
        callbacks+=int('found_perf' in info)
        if found>a.seconds+1e-6:return False
        metrics=solution_metrics(sol)
        if cap is not None and metrics['completion_s']>cap+1e-6:
            rejects['completion_cap']+=1;return False
        st=station_audit(P,sol['transport'])
        assert st['boxes']==st['unique_boxes']==80 and st['late_boxes']==st['hard_violations']==0
        if best is not None and key(sol,o)>=key(best,o):return False
        if best is None:
            oldphase=phase;setphase('first_solution_validation')
            first=base/'first_candidate.json';atomic(first,sol)
            validate_solution(q,first,base/'first_validation.json')
            setphase(oldphase)
            if time.perf_counter()>deadline:return False
        with lock:
            best=copy.deepcopy(sol)
            trace.append(dict(found_s=found,origin=info.get('origin','independent_construction'),attempt=attempts,**metrics))
            atomic(base/'best_solution.json',best)
            atomic(base/'best_meta.json',dict(found_s=found,solution_sha256=digest(base/'best_solution.json'),metrics=metrics))
            for t in targets:
                if found<=t:
                    atomic(base/f'checkpoint_{t:g}s_solution.json',best)
                    atomic(base/f'checkpoint_{t:g}s_meta.json',dict(checkpoint_s=t,best_found_s=found,
                        solution_sha256=digest(base/f'checkpoint_{t:g}s_solution.json'),metrics=metrics))
            progress()
        print('BEST',q,o,m,trace[-1],flush=True);return True

    def joint(routes,seconds,name,seed):
        setphase('joint_radio_and_schedule')
        left=min(seconds,deadline-time.perf_counter())
        if left<=.05:return None
        return joint_v6.solve(name=name,pool=routes,atoms=atoms,sites_override=sites,
            seconds=left,deadline=time.monotonic()+left,seed=seed,workers=1,slots=6,
            zero_late=True,max_C=cap,objectives=objectives,warm=None,
            incumbent_callback=lambda s,i:retain(s,dict(**i,origin='independent_joint_search')))

    def repair_first(proposal_ids):
        """Budgeted constraint repair, never an imported/common initial plan.

        First preserve half of the method's own proposed route groups. If this
        is impossible, relax the preserved subset. CP stops at its first feasible
        point; subsequent objective improvement belongs to the named heuristic.
        """
        nonlocal first_repair_used,template,ctor
        first_repair_used=True;setphase('budgeted_first_solution_constraint_repair')
        end=min(deadline,time.perf_counter()+90)
        records=[];repair_started=time.perf_counter()
        gen=joint_v6.iter_templates(pool,atoms,sites,time.monotonic()+max(.05,end-time.perf_counter()),42,cap)
        for ti,tpl in enumerate(gen,1):
            eligible={r['id']:r for r in tpl['pool']}
            preferred=[rid for rid in proposal_ids if rid in eligible]
            for fraction in ([.5,.25,0.] if preferred else [0.]):
                left=min(15,max(.05,end-time.perf_counter()))
                if left<=.05:return False
                keep=preferred[:int(len(preferred)*fraction)]
                def observer(result,info):
                    sol=dict(transport=master_v4.decode(P,result,retime=False),relay=copy.deepcopy(tpl['relay']),resources=[2,6])
                    joint_v6.trim_unused_relay_time(sol,atoms);joint_v4.color(sol,P)
                    return retain(sol,dict(**info,origin='independent_budgeted_constraint_repair'))
                result=master_v4.solve(P,eligible,seconds=left,workers=1,seed=42+ti,
                    objectives=('C',),fixed_D=0,max_C=tpl['horizon'],delivery_mode='batch',warm=None,
                    required_route_ids=keep,allowed_start_intervals=tpl['allowed_start_intervals'],stop_on_first=True,
                    evidence_path=base/f'first_repair_{ti:03}_{len(keep):02}.json',
                    deadline_monotonic=min(end,time.perf_counter()+left),incumbent_callback=observer)
                records.append(dict(template=ti,preserved_route_ids=keep,preserved_fraction=fraction,
                    proposal_routes=len(proposal_ids),eligible_proposal_routes=len(preferred),evidence=result['evidence']))
                atomic(base/'first_repair_protocol.json',dict(trigger_s=45.,all_work_inside_budget=True,
                    no_external_solution=True,records=records,elapsed_s=time.perf_counter()-repair_started))
                if result['selected']:observer(result,{})
                if best is not None:
                    template=tpl
                    ctor=WindowConstructor(P,template['pool'],template['horizon'],template['allowed_start_intervals'],schedule_seconds=2.,seed=42)
                    return True
                if time.perf_counter()>=end:return False
        return False

    try:
        if m=='cp_sat':
            if q=='Q2':
                setphase('cp_full_pool')
                def observe(res,info):
                    return retain(dict(transport=master_v2.decode(P,res,retime=False),relay=[],resources=[2,6]),
                        dict(**info,origin='independent_cp_sat'))
                result=master_v2.solve(P,{r['id']:r for r in pool},seconds=deadline-time.perf_counter(),
                    seed=42,workers=1,objectives=objectives,fixed_D=0,max_C=cap,delivery_mode='batch',
                    warm=None,evidence_path=base/'cp_evidence.json',deadline_monotonic=deadline,incumbent_callback=observe)
                if result['selected']:observe(result,{})
            else:
                setphase('independent_radio_templates')
                templates=joint_v6.iter_templates(pool,atoms,sites,time.monotonic()+max(.05,deadline-time.perf_counter()),42,cap)
                for index,template in enumerate(templates,1):
                    setphase('cp_template_search')
                    left=min(8,max(.05,deadline-time.perf_counter()))
                    def observe_template(result,info):
                        sol=dict(transport=master_v4.decode(P,result,retime=False),relay=copy.deepcopy(template['relay']),resources=[2,6])
                        joint_v6.trim_unused_relay_time(sol,atoms);joint_v4.color(sol,P)
                        return retain(sol,dict(**info,origin='independent_cp_template'))
                    result=master_v4.solve(P,{r['id']:r for r in template['pool']},seconds=left,
                        workers=1,seed=42+index,objectives=objectives,fixed_D=0,max_C=template['horizon'],
                        delivery_mode='batch',warm=None,allowed_start_intervals=template['allowed_start_intervals'],
                        stop_on_first=True,evidence_path=base/f'cp_template_{index:04}.json',
                        deadline_monotonic=min(deadline,time.perf_counter()+left),incumbent_callback=observe_template)
                    if result['selected']:observe_template(result,{})
                    if best is not None:break
                    if time.perf_counter()>=deadline:break
                if best is not None and deadline-time.perf_counter()>.2:
                    setphase('joint_cp_improvement_from_own_solution')
                    selected,reduced,reduction=joint_v6.reduce_coverage(pool,atoms,sites,42,seconds=min(2,deadline-time.perf_counter()))
                    atomic(base/'coverage_reduction.json',reduction);joint_v4.OUT=base/'decoders'
                    own_hint=copy.deepcopy(best)
                    own_hint['relay'].sort(key=lambda r:(r['start'],r['site']['id']))
                    for slot,row in enumerate(own_hint['relay']):row['slot']=slot
                    # This hint was discovered by this configuration within its
                    # own budget. No external/common/preflight solution is read.
                    found=joint_v4.solve(name='own_incumbent_improvement',pool=pool,atoms=reduced,
                        sites_override=selected,seconds=max(.05,deadline-time.perf_counter()),
                        deadline=time.monotonic()+max(.05,deadline-time.perf_counter()),seed=42,
                        workers=1,slots=6,zero_late=True,max_C=cap,objectives=objectives,warm=own_hint,
                        complete_warm=False,incumbent_callback=lambda s,i:retain(s,dict(**i,origin='independent_cp_improvement')))
                    retain(found)
        else:
            pheromone={};weights=[1.,1.,1.];rewards=[0.,0.,0.];uses=[0,0,0];seen={}
            templates=None;template=None;template_tries=0
            if q=='Q3':
                setphase('independent_radio_templates')
                templates=joint_v6.iter_templates(pool,atoms,sites,time.monotonic()+max(.05,deadline-time.perf_counter()),42,cap)
            while time.perf_counter()<deadline:
                if q=='Q3' and best is None and not first_repair_used and time.perf_counter()-began>=45:
                    repair_first(getattr(ctor,'last_proposal_route_ids',[]))
                    if m=='aco' and best is not None:
                        for row in best['transport']:pheromone[row['route']['id']]=2.
                    continue
                if q=='Q3' and (template is None or (best is None and
                        (getattr(ctor,'last_root_infeasible',False) or ctor.stats.get('complete_covers',0)>=24))):
                    if template is not None and getattr(ctor,'last_root_infeasible',False):
                        rejects['proven_root_infeasible_template']+=1
                    setphase('independent_radio_template')
                    template=next(templates,None);template_tries=0
                    if template is None:break
                    ctor=WindowConstructor(P,template['pool'],template['horizon'],template['allowed_start_intervals'],schedule_seconds=2.,seed=42)
                    atomic(base/'active_template.json',dict(horizon=template['horizon'],sites=template['sites'],
                        end_first=template['end_first'],route_count=len(template['pool']),coverage_reduction=template['coverage_reduction']))
                attempts+=1;fixed=();op=0
                if m=='alns' and best is not None:
                    op=rng.choices(range(3),weights=weights)[0];uses[op]+=1
                    rr=[r['route'] for r in best['transport']];k=min(len(rr),max(2,math.ceil(len(rr)*rng.uniform(.15,.45))))
                    if op==0:remove=set(rng.sample(range(len(rr)),k))
                    elif op==1:remove=set(sorted(range(len(rr)),key=lambda i:rr[i]['energy']/len(rr[i]['boxes']),reverse=True)[:k])
                    else:
                        anchor=rng.choice(rr)['stops'][0][0]
                        remove=set(sorted(range(len(rr)),key=lambda i:0 if rr[i]['stops'][0][0]==anchor else P.geo[anchor,rr[i]['stops'][0][0]][0])[:k])
                    fixed=[r for i,r in enumerate(rr) if i not in remove]
                setphase('cover_and_resource_schedule')
                mode='aco' if m=='aco' and best is not None else 'random' if m=='alns' and best is not None else 'greedy'
                if m=='aco' and best is not None:aco_iterations+=1
                if m=='alns' and best is not None:alns_iterations+=1
                rows=ctor.build(rng,deadline,mode=mode,objective=o,pheromone=pheromone,fixed=fixed,
                    cover_seconds=3.,schedule_seconds=3. if q=='Q3' else 1.)
                template_tries+=1
                if rows is None:rejects['construction_or_schedule_failed']+=1;continue
                complete+=1
                if q=='Q2':sol=dict(transport=rows,relay=[],resources=[2,6])
                else:
                    decoders+=1
                    sol=dict(transport=rows,relay=copy.deepcopy(template['relay']),resources=[2,6])
                    joint_v6.trim_unused_relay_time(sol,atoms);joint_v4.color(sol,P)
                origin='independent_own_greedy_bootstrap' if best is None and m in ('aco','alns') else f'independent_{m}_search'
                improved=retain(sol,dict(origin=origin))
                if m=='aco' and best is not None:
                    for rid in list(pheromone):pheromone[rid]=max(.03,pheromone[rid]*.92)
                    for r in best['transport']:
                        rid=r['route']['id'];pheromone[rid]=min(50,pheromone.get(rid,1)+2)
                if m=='alns' and best is not None:
                    rewards[op]+=8 if improved else 1 if sol is not None else 0
                    if attempts%20==0:
                        for j in range(3):weights[j]=.8*weights[j]+.2*(rewards[j]/max(1,uses[j])+.1)
                        rewards=[0.,0.,0.];uses=[0,0,0]
        setphase('search_finished')
        atomic(base/'worker_finished.json',dict(search_wall_s=time.perf_counter()-began,early_exit=time.perf_counter()<deadline,
            supplied_initial_solution=False,supplied_warm_start=False))
    except BaseException as exc:
        atomic(base/'worker_error.json',dict(type=type(exc).__name__,error=str(exc),elapsed_s=time.perf_counter()-began))
        raise
    finally:
        progress();finished.set()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--question',choices=['Q2','Q3'],required=True)
    p.add_argument('--objective',choices=['time','energy'],required=True)
    p.add_argument('--method',choices=['greedy','aco','alns','cp_sat'],required=True)
    p.add_argument('--seconds',type=float,default=600);p.add_argument('--name',required=True)
    run(p.parse_args())
