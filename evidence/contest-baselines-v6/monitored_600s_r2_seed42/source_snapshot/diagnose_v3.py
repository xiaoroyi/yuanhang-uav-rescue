"""Bounded, diagnostic-only tests. Never alter or replace formal v3 records."""
import argparse
from collections import Counter
import json
import math
from pathlib import Path
import time
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint, linprog
from ortools.sat.python import cp_model as cp
from benchmark_v2 import load, V1, V2, digest
from benchmark_v3 import V3
from benchmark import route_latest, station_audit
from legacy_routes import Physics
from support import PROJECT, dump
import master_v2

DEST = V3/'failure_diagnosis'

def overview():
    DEST.mkdir(exist_ok=True, parents=True)
    P=Physics();pool=load(V1/'pool_q2.json');ids={r['id'] for r in pool}
    historical=load(V2/'q2_alignment_audit/historical_q2_economy_solution.json')
    comparison=[]
    for row in historical:
        r=row['route'];new=P.evaluate(r['model'],r['stops'])
        assert new is not None
        comparison.append(dict(id=r['id'],reconstructed_id=new['id'],in_public_pool=new['id'] in ids,
            energy_difference_kwh=new['energy']-r['energy'],duration_difference_s=new['duration']-r['duration'],
            model=r['model'],boxes=len(r['boxes']),stops=len(r['stops'])))
    runs=load(V3/'aligned_600s_seed42/results.json')
    counts=[dict(question=r['question'],method=r['method'],attempts=r['attempts'],
        decoder_calls=r['decoder_calls'],rejections=r['rejections']) for r in runs]
    report=dict(public_pool_size=len(pool),route_counts_by_model=dict(Counter(r['model'] for r in pool)),
        route_counts_by_stops=dict(Counter(len(r['stops']) for r in pool)),
        historical_q2_route_comparison=comparison,historical_q2_routes_in_pool=sum(r['in_public_pool'] for r in comparison),
        historical_q2_total_routes=len(comparison),historical_q2_station=station_audit(P,historical),
        historical_q2_resources_by_model=dict(Counter(r['route']['model'] for r in historical)),
        formal_counts=counts,scope='Historical plans only replayed to audit physical/model compatibility, not supplied to searches.')
    dump(DEST/'overview.json',report)
    print(json.dumps(report,ensure_ascii=False,indent=2),flush=True)

def relaxed(question,seconds):
    """Necessary relaxation: exact cover + aircraft workload, no timing/battery/radio."""
    P=Physics();pool=load(V1/'pool_q2.json');n=len(pool);boxes=list(P.boxes);groups=list(P.models)
    cover=np.array([[b in r['boxes'] for r in pool] for b in boxes],float)
    work=np.array([[r['duration'] if r['model']==g else 0 for r in pool] for g in groups])
    cap=6000 if question=='Q2' else 5939.9
    A=np.vstack([cover,work]);lb=np.r_[np.ones(len(boxes)),np.zeros(len(groups))]
    ub=np.r_[np.ones(len(boxes)),[P.data['M'][g]*cap for g in groups]]
    if question=='Q3':
        A=np.vstack([A,np.ones(n),[r['energy'] for r in pool]])
        lb=np.r_[lb,0,0];ub=np.r_[ub,23,68.9999]
    costs=np.array([r['energy'] for r in pool]);beg=time.perf_counter()
    res=milp(costs,integrality=np.ones(n),bounds=Bounds(np.zeros(n),np.ones(n)),constraints=LinearConstraint(A,lb,ub),
        options={'time_limit':seconds,'mip_rel_gap':0.00001})
    result=dict(question=question,status=int(res.status),message=res.message,wall_s=time.perf_counter()-beg,
        energy_kwh=None if res.fun is None else float(res.fun),
        energy_lower_bound_kwh=None if getattr(res,'mip_dual_bound',None) is None else float(res.mip_dual_bound),
        gap=None if getattr(res,'mip_gap',None) is None else float(res.mip_gap),
        scope='Necessary relaxation only: exact box coverage and aggregate aircraft work; omits actual schedule, deadlines, batteries, all radio and relay energy.')
    if res.x is not None:
        selected=[r for i,r in enumerate(pool) if res.x[i]>.5]
        result.update(routes=selected,sorties=len(selected),work_s={g:sum(r['duration'] for r in selected if r['model']==g) for g in groups})
    dump(DEST/f'{question}_necessary_relaxation.json',result)
    print(question,'RELAXED', {k:v for k,v in result.items() if k!='routes'},flush=True)

def binpack(question,seconds):
    """Stronger necessary condition: fit each whole route on an aircraft by cap."""
    P=Physics();pool=load(V1/'pool_q2.json');cap=6000 if question=='Q2' else 5939.9
    model=cp.CpModel();cover={b:[] for b in P.boxes};xx=[];assign=[];q=.001
    for i,r in enumerate(pool):
        x=model.new_bool_var(f'x{i}');xx.append(x);vs=[]
        for k in range(P.data['M'][r['model']]):vs.append(model.new_bool_var(f'a{i}_{k}'))
        model.add(sum(vs)==x);assign.append(vs)
        for b in r['boxes']:cover[b].append(x)
    for b,vs in cover.items():model.add(sum(vs)==1)
    for g in P.models:
        for k in range(P.data['M'][g]):
            model.add(sum(math.floor(r['duration']/q)*assign[i][k] for i,r in enumerate(pool) if r['model']==g)<=math.ceil(cap/q))
    if question=='Q3':
        model.add(sum(xx)<=23)
        model.add(sum(math.floor(r['energy']*1e6)*xx[i] for i,r in enumerate(pool))<=math.ceil(68.9999e6))
    model.minimize(sum(math.floor(r['energy']*1e6)*xx[i] for i,r in enumerate(pool)))
    solver=cp.CpSolver();solver.parameters.num_search_workers=4;solver.parameters.random_seed=42
    solver.parameters.max_time_in_seconds=seconds;beg=time.perf_counter();status=solver.solve(model)
    result=dict(question=question,status=solver.status_name(status),wall_s=time.perf_counter()-beg,
        lower_bound_kwh=solver.best_objective_bound*1e-6,
        scope='Necessary whole-route aircraft packing only. Downward-rounded 1ms durations relax physical durations; no release times, deadlines, battery cycling, radio or relay energy.')
    if status in (cp.FEASIBLE,cp.OPTIMAL):
        selected=[r for i,r in enumerate(pool) if solver.value(xx[i])]
        result.update(routes=selected,sorties=len(selected),energy_kwh=sum(r['energy'] for r in selected))
    dump(DEST/f'{question}_binpack_relaxation.json',result)
    print(question,'PACKING',{k:v for k,v in result.items() if k!='routes'},flush=True)

def cp_feasibility(seconds):
    P=Physics();pool=load(V1/'pool_q2.json');beg=time.perf_counter()
    # Isolate objective choice: remove minimization, retain identical constraints.
    original=cp.CpModel.minimize
    cp.CpModel.minimize=lambda self,obj: self.clear_objective()
    try:
        result=master_v2.solve(P,{r['id']:r for r in pool},seconds=seconds,seed=42,workers=4,
            objectives=('C',),fixed_D=0,max_C=6000,delivery_mode='batch',warm=None,
            evidence_path=DEST/'Q2_feasibility_first_cp.json',deadline_monotonic=beg+seconds)
    finally:cp.CpModel.minimize=original
    if result['selected']:
        rows=master_v2.decode(P,result,retime=False)
        dump(DEST/'Q2_feasibility_first_solution.json',dict(transport=rows,relay=[],resources=[2,6]))
    print('Q2 FEASIBILITY FIRST',result['evidence'],flush=True)

def historical_replay(seconds):
    """Positive control: schedule historical groups only, never a baseline result."""
    P=Physics();rows=load(V2/'q2_alignment_audit/historical_q2_economy_solution.json')
    pool={r['route']['id']:r['route'] for r in rows};beg=time.perf_counter()
    result=master_v2.solve(P,pool,seconds=seconds,seed=42,workers=1,objectives=('C',),
        fixed_D=0,max_C=6000,delivery_mode='batch',warm=None,
        evidence_path=DEST/'Q2_historical_groups_positive_control.json',deadline_monotonic=beg+seconds)
    if result['selected']:
        decoded=master_v2.decode(P,result,retime=False)
        from legacy_validate import check
        from support import inputs
        audit=check(decoded,data=inputs());station=station_audit(P,decoded)
        assert audit['summary']['valid'] and station['late_boxes']==station['hard_violations']==0
        dump(DEST/'Q2_historical_groups_validation.json',dict(physical=audit,station=station,
            is_baseline_result=False,search_initialization_for_formal_runs=False))
    print('POSITIVE CONTROL',result['evidence'],flush=True)

def expanded_probe(seconds):
    """Independent single-site subset closure, diagnostic feasibility only."""
    from collections import defaultdict
    P=Physics();pool={r['id']:r for r in load(V1/'pool_q2.json')};by=defaultdict(list)
    for b in P.boxes:by[P.boxes[b]['service']].append(b)
    began=time.perf_counter();before=len(pool)
    for site,bs in by.items():
        for mask in range(1,1<<len(bs)):
            subset=[b for i,b in enumerate(bs) if mask>>i&1]
            mass=sum(P.boxes[b]['weight'] for b in subset);vol=sum(P.boxes[b]['volume_L'] for b in subset)
            for g,m in P.models.items():
                if mass>m['Q'] or vol>m['volume_L']:continue
                r=P.evaluate(g,[(site,subset)])
                if r is not None and route_latest(P,r)>=0:pool[r['id']]=r
    preparation_s=time.perf_counter()-began
    dump(DEST/'expanded_pool.json',list(pool.values()))
    dump(DEST/'expanded_pool_contract.json',dict(original_size=before,expanded_size=len(pool),
        preparation_s=preparation_s,generator='all nonempty single-site cargo subsets, all models, original physics and zero-late start feasibility; union with original 850 routes',
        no_paper_route_schedule_or_metric_inputs=True,formal_result=False))
    print('EXPANDED',len(pool),'prep',preparation_s,flush=True)
    # Feasibility first; this is a diagnostic alteration, not a timed benchmark.
    original=cp.CpModel.minimize;cp.CpModel.minimize=lambda self,obj:self.clear_objective();beg=time.perf_counter()
    try:
        result=master_v2.solve(P,pool,seconds=seconds,seed=42,workers=4,objectives=('C',),fixed_D=0,
            max_C=6000,delivery_mode='batch',warm=None,evidence_path=DEST/'Q2_expanded_feasibility.json',deadline_monotonic=beg+seconds)
    finally:cp.CpModel.minimize=original
    if result['selected']:
        rows=master_v2.decode(P,result,retime=False)
        dump(DEST/'Q2_expanded_solution.json',dict(transport=rows,relay=[],resources=[2,6]))
        from legacy_validate import check
        from support import inputs
        audit=check(rows,data=inputs());station=station_audit(P,rows)
        assert audit['summary']['valid'] and not station['late_boxes'] and not station['hard_violations']
        dump(DEST/'Q2_expanded_validation.json',dict(physical=audit,station=station,is_baseline_result=False))
    print('EXPANDED PROBE',result['evidence'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['overview','relaxed','binpack','cp_feasibility','historical_replay','expanded_probe'])
    p.add_argument('--question',choices=['Q2','Q3'],default='Q2');p.add_argument('--seconds',type=float,default=30)
    a=p.parse_args();DEST.mkdir(parents=True,exist_ok=True)
    if a.mode=='overview':overview()
    elif a.mode=='relaxed':relaxed(a.question,a.seconds)
    elif a.mode=='binpack':binpack(a.question,a.seconds)
    elif a.mode=='historical_replay':historical_replay(a.seconds)
    elif a.mode=='expanded_probe':expanded_probe(a.seconds)
    else:cp_feasibility(a.seconds)
