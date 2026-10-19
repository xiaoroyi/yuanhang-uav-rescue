"""Independent 600s searches: no supplied feasible solution, hints, or paper answer."""
import argparse
from collections import defaultdict
import copy
import math
import random
import time
from benchmark_v4 import CapConstructor, CAPS
from benchmark_v2 import load, digest, solution_metrics, key, validate_solution
from benchmark import station_audit
from pattern_v4 import V4
from legacy_routes import Physics
from support import PROJECT, dump
import master_v2
import joint_v4

V5 = PROJECT / 'evidence/contest-baselines-v5'

def run(a):
    q, objective, method = a.question, a.objective, a.method
    cap = CAPS[q]['C'] if objective == 'energy' else None
    base = V5 / a.name
    base.mkdir(exist_ok=False, parents=True)
    # These are individual physical route/site candidates, not a feasible schedule.
    P = Physics(); pool = load(V4 / f'pool_{q.lower()}.json')
    sites = load(V4 / 'sites.json'); atoms = load(V4 / 'atoms.json')
    ctor = CapConstructor(P, pool, cap if cap is not None else float('inf'))
    rng = random.Random(42); began = time.perf_counter(); deadline = began + a.seconds
    best = None; trace = []; checkpoints = {}; rejects = defaultdict(int)
    attempts = decoders = callbacks = complete_constructions = 0
    targets = [float(t) for t in a.checkpoints.split(',')]
    joint_v4.OUT = base / 'decoders'; joint_v4.OUT.mkdir()
    seen = {}; last_progress = began
    objectives = ('C', 'E') if objective == 'time' else ('E', 'C')

    def progress():
        dump(base / 'search_progress.json', dict(question=q, objective=objective, method=method,
            elapsed_s=time.perf_counter()-began, attempts=attempts, decoder_calls=decoders,
            complete_constructions=complete_constructions, callbacks=callbacks,
            rejections=dict(rejects), has_incumbent=best is not None, trace=trace))

    def retain(sol, info=None):
        nonlocal best, callbacks
        if sol is None: return False
        info = info or {}; found = info.get('found_perf', time.perf_counter())-began
        callbacks += int('found_perf' in info)
        if found > a.seconds+1e-6: return False
        if cap is not None and solution_metrics(sol)['completion_s'] > cap+1e-6:
            rejects['completion_cap'] += 1; return False
        audit = station_audit(P, sol['transport'])
        assert audit['boxes'] == audit['unique_boxes'] == 80
        assert audit['late_boxes'] == audit['hard_violations'] == 0
        if best is not None and key(sol, objective) >= key(best, objective): return False
        best = copy.deepcopy(sol); metrics = solution_metrics(sol)
        trace.append(dict(found_s=found, origin=info.get('origin', 'independent_search'),
            attempt=attempts, **metrics))
        dump(base / 'best_solution.json', best)
        for t in targets:
            if found <= t:
                dump(base / f'checkpoint_{t:g}s_solution.json', best)
                checkpoints[str(t)] = dict(checkpoint_s=t, best_found_s=found, metrics=metrics)
        progress(); print('BEST', q, objective, method, trace[-1], flush=True)
        return True

    def decode(rows):
        nonlocal decoders
        left = deadline-time.perf_counter()
        if left < .2: return None
        if q == 'Q2': return dict(transport=rows, relay=[], resources=[2,6])
        sig = tuple(sorted(r['route']['id'] for r in rows))
        if seen.get(sig, 0) >= 3: return None
        seen[sig] = seen.get(sig, 0)+1; decoders += 1; seconds = min(10, left)
        # No hint: this decoder solves the method's selected routes from scratch.
        return joint_v4.solve(name=f'call_{decoders:05}', pool=[r['route'] for r in rows],
            atoms=atoms, sites_override=sites, seconds=seconds, slots=6, objectives=objectives,
            zero_late=True, workers=1, seed=42+decoders, max_C=cap, warm=None,
            deadline=time.monotonic()+seconds,
            incumbent_callback=lambda s,i:retain(s,dict(**i,origin='independent_joint_decoder')))

    progress(); print('START_NO_INITIAL', q, objective, method, flush=True)
    if method == 'cp_sat':
        if q == 'Q2':
            def observe(result, info):
                return retain(dict(transport=master_v2.decode(P,result,retime=False),relay=[],resources=[2,6]),
                    dict(**info,origin='independent_full_pool_cp'))
            result = master_v2.solve(P, {r['id']:r for r in pool}, seconds=deadline-time.perf_counter(),
                seed=42, workers=1, objectives=objectives, fixed_D=0, max_C=cap,
                delivery_mode='batch', warm=None, evidence_path=base/'cp_evidence.json',
                deadline_monotonic=deadline, incumbent_callback=observe)
            if result['selected']:
                retain(dict(transport=master_v2.decode(P,result,retime=False),relay=[],resources=[2,6]))
        else:
            retain(joint_v4.solve(name='full_pool', pool=pool, atoms=atoms, sites_override=sites,
                seconds=deadline-time.perf_counter(), slots=6, objectives=objectives,
                zero_late=True, workers=1, seed=42, warm=None, complete_warm=False,
                max_C=cap, deadline=time.monotonic()+max(.1,deadline-time.perf_counter()),
                incumbent_callback=lambda s,i:retain(s,dict(**i,origin='independent_full_pool_cp'))))
    else:
        pheromone = {}; weights = [1.,1.,1.]; rewards = [0.,0.,0.]; uses = [0,0,0]
        while time.perf_counter() < deadline:
            attempts += 1; op = 0; fixed = ()
            # ALNS must construct its own first solution inside the same budget.
            if method == 'alns' and best is not None:
                op = rng.choices(range(3),weights=weights)[0]; uses[op] += 1
                rr = [r['route'] for r in best['transport']]
                k = max(2,math.ceil(len(rr)*rng.uniform(.1,.35)))
                if op == 0: remove = set(rng.sample(range(len(rr)),k))
                elif op == 1:
                    remove = set(sorted(range(len(rr)),key=lambda i:rr[i]['energy']/len(rr[i]['boxes']),reverse=True)[:k])
                else:
                    anchor = rng.choice(rr)['stops'][0][0]
                    remove = set(sorted(range(len(rr)),key=lambda i:0 if rr[i]['stops'][0][0]==anchor else P.geo[anchor,rr[i]['stops'][0][0]][0])[:k])
                fixed = [r for i,r in enumerate(rr) if i not in remove]
            rows = ctor.build(rng,mix=rng.choice([0,.2,.5,.8,1.]),
                mode='aco' if method=='aco' else 'random' if method=='alns' else 'greedy',
                pheromone=pheromone,fixed=fixed)
            if rows is None: rejects['construction_dead_end'] += 1
            else:
                complete_constructions += 1; sol = decode(rows); improved = retain(sol)
                if method == 'aco' and best is not None:
                    for rid in list(pheromone): pheromone[rid] = max(.05,pheromone[rid]*.95)
                    for r in best['transport']:
                        rid = r['route']['id']; pheromone[rid] = min(30,pheromone.get(rid,1)+1)
                if method == 'alns' and best is not None:
                    rewards[op] += 8 if improved else 1 if sol else 0
                    if attempts % 25 == 0:
                        for j in range(3): weights[j] = .8*weights[j]+.2*(rewards[j]/max(1,uses[j])+.1)
                        rewards=[0.,0.,0.]; uses=[0,0,0]
            if time.perf_counter()-last_progress >= 15:
                progress(); last_progress = time.perf_counter()
    search_wall = time.perf_counter()-began; progress()
    record = dict(question=q,objective=objective,method=method,seed=42,budget_s=a.seconds,
        search_wall_s=search_wall,completion_cap_s=cap,attempts=attempts,decoder_calls=decoders,
        callbacks=callbacks,complete_constructions=complete_constructions,rejections=dict(rejects),
        trace=trace,checkpoints=[],supplied_initial_solution=False,supplied_warm_start=False,
        paper_solution_used=False,status='COMPLETED')
    verified = {}
    for t in targets:
        path = base / f'checkpoint_{t:g}s_solution.json'
        if not path.exists():
            record['checkpoints'].append(dict(checkpoint_s=t,status='NO_FEASIBLE_SOLUTION_FOUND',
                metrics=None,best_found_s=None,solution_sha256=None))
            continue
        sha = digest(path)
        if sha in verified:
            metrics,audit = verified[sha]; dump(base/f'checkpoint_{t:g}s_validation.json',audit)
        else:
            metrics,audit = validate_solution(q,path,base/f'checkpoint_{t:g}s_validation.json')
            verified[sha] = (metrics,audit)
        assert cap is None or metrics['completion_s'] <= cap+1e-6
        record['checkpoints'].append(dict(checkpoints[str(t)],status='VALIDATED_FEASIBLE',
            metrics=metrics,solution_sha256=sha))
    record['total_wall_s'] = time.perf_counter()-began
    dump(base/'run.json',record); print('FINISH',q,objective,method,record['checkpoints'][-1],flush=True)

if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--question',choices=['Q2','Q3'],required=True)
    p.add_argument('--objective',choices=['time','energy'],required=True)
    p.add_argument('--method',choices=['greedy','aco','alns','cp_sat'],required=True)
    p.add_argument('--seconds',type=float,default=600);p.add_argument('--checkpoints',default='180,600')
    p.add_argument('--name',required=True);run(p.parse_args())
