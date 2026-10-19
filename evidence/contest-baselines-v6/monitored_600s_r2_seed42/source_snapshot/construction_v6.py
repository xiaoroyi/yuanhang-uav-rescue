"""Backtracking physical-route construction; no saved solution or answer inputs.

Selection uses exact box coverage, a fail-first box, and necessary resource
energetic cuts.  The three heuristic modes differ in branch choice. Scheduling
is a separate bounded list-search; a failed prefix does not discard its entire
search tree. All work is charged to the caller's absolute perf_counter deadline.
"""
import math
import random
import time
import warnings
from collections import defaultdict
import numpy as np
from scipy.optimize import linprog, OptimizeWarning

from benchmark import due, route_latest


class Constructor:
    def __init__(self, P, pool, cap=None):
        self.P = P
        self.pool = list(pool)
        self.cap = cap
        self.boxes = sorted(P.boxes)
        self.bi = {b: i for i, b in enumerate(self.boxes)}
        self.full = (1 << len(self.boxes)) - 1
        self.masks = [sum(1 << self.bi[b] for b in r['boxes']) for r in self.pool]
        self.latest = [min(route_latest(P, r), (cap-r['duration']) if cap is not None else math.inf) for r in self.pool]
        self.by = [[] for _ in self.boxes]
        for i, r in enumerate(self.pool):
            if self.latest[i] >= -1e-7:
                for b in r['boxes']:
                    self.by[self.bi[b]].append(i)
        self.rid = {r['id']: i for i, r in enumerate(self.pool)}
        self.groups = list(P.models)
        self.cuts = []
        if cap is not None:
            for g in self.groups:
                for T in sorted(set([1800., 2400., 3000., 3600., 4200., 4800., 5400., cap])):
                    if T > cap: continue
                    for battery in [False, True]:
                        stock = P.data['K' if battery else 'M'][g]
                        coeff = [min(r['duration'] + (r['charge'] if battery else 0), max(0., T-self.latest[i])) if r['model'] == g else 0. for i, r in enumerate(self.pool)]
                        self.cuts.append((T*stock, coeff))
        self.stats = defaultdict(int)
        self.cover_matrix=np.array([[float(b in r['boxes']) for r in self.pool] for b in self.boxes])
        self.cut_matrix=np.array([coeff for _,coeff in self.cuts]) if self.cuts else None

    def cover(self, rng, deadline, mode='greedy', objective='energy', pheromone=None,
              fixed=(), max_nodes=25000, excluded=()):
        """Return a new exact cover, using bounded backtracking rather than CP."""
        self.last_root_infeasible = False
        pheromone = pheromone or {}
        fixed_idx = [self.rid[r['id']] for r in fixed]
        used = 0
        chosen = []
        cuts = [0.]*len(self.cuts)
        loads = {g: 0. for g in self.groups}
        forbidden = set(excluded)
        costs=np.array([(r['energy'] if objective=='energy' else r['duration']/self.P.data['M'][r['model']]) * rng.uniform(.75,1.25) for r in self.pool])
        if mode=='aco':
            costs=np.array([x/max(.1,pheromone.get(r['id'],1.))**.2 for x,r in zip(costs,self.pool)])
        for i in fixed_idx:
            if self.masks[i] & used: return None
            chosen.append(i); used |= self.masks[i]
            loads[self.pool[i]['model']] += self.pool[i]['duration']
            cuts = [v+c[i] for v, (_, c) in zip(cuts, self.cuts)]
        nodes = 0

        def visit(occupied):
            nonlocal nodes
            nodes += 1
            if nodes > max_nodes or time.perf_counter() >= deadline: return None
            if occupied == self.full:
                signature = tuple(sorted(chosen))
                if signature in forbidden: return None
                self.stats['complete_covers'] += 1
                return [self.pool[i] for i in chosen]
            # A continuous relaxation only guides/prunes the heuristic's own
            # branch choices. It never returns a discrete cover or schedule.
            available=[i for i,m in enumerate(self.masks) if not m&occupied and self.latest[i]>=-1e-7]
            remaining=[b for b in range(len(self.boxes)) if not occupied>>b&1]
            if not available:return None
            self.stats['lp_checks']+=1
            with warnings.catch_warnings():
                # SciPy forwards this supported HiGHS option but advertises it
                # as unrecognized; suppress ONLY this exact forwarding notice.
                warnings.filterwarnings('ignore',
                    message=r"Unrecognized options detected: \{'threads': 1\}\. These will be passed to HiGHS verbatim\.",
                    category=OptimizeWarning)
                relax=linprog(costs[available],
                    A_ub=self.cut_matrix[:,available] if self.cuts else None,
                    b_ub=np.array([limit-v for v,(limit,_) in zip(cuts,self.cuts)]) if self.cuts else None,
                    A_eq=self.cover_matrix[np.ix_(remaining,available)],b_eq=np.ones(len(remaining)),
                    bounds=(0.,1.),method='highs',options={
                        'time_limit':max(.01,min(.5,deadline-time.perf_counter())), 'threads':1})
            if relax.x is None:
                self.stats['lp_infeasible' if relax.status==2 else 'lp_timeout']+=1
                if relax.status==2 and nodes==1:
                    # A root relaxation proves this entire current template
                    # (or ALNS fixed subset) impossible, not merely one branch.
                    self.last_root_infeasible=True
                    self.stats['root_lp_infeasible']+=1
                return None
            lp={i:x for i,x in zip(available,relax.x)}
            best = None
            for b in range(len(self.boxes)):
                if occupied >> b & 1: continue
                feasible = []
                for i in self.by[b]:
                    if self.masks[i] & occupied: continue
                    if any(v+c[i] > limit+1e-6 for v, (limit,c) in zip(cuts,self.cuts)): continue
                    feasible.append(i)
                if not feasible:
                    self.stats['uncovered_dead_end'] += 1
                    return None
                rank = (len(feasible), due(self.P,self.boxes[b]), b)
                if best is None or rank < best[0]: best = (rank, feasible)
                if len(feasible) == 1: break
            options = best[1]
            score = {}
            for i in options:
                r = self.pool[i]; g=r['model']; n=len(r['boxes'])
                work = r['duration']/self.P.data['M'][g]
                load = loads[g]/self.P.data['M'][g]
                # Account for future aircraft bottlenecks, not just flight energy.
                if objective == 'energy':
                    score[i] = (r['energy'] + work/1500. + load*r['duration']/6e6)/n
                else:
                    score[i] = (work + .45*load + 20*r['energy'])/n
            if mode == 'aco':
                ranked = []
                available = list(options)
                while available:
                    weights = [(max(.01,lp.get(i,0))**3)*max(.01,pheromone.get(self.pool[i]['id'],1.))/max(1e-9,score[i])**2 for i in available]
                    i=rng.choices(available,weights=weights)[0]; available.remove(i);ranked.append(i)
            else:
                jitter = .55 if mode in ('random','alns') else .18
                ranked = sorted(options,key=lambda i:score[i]*rng.uniform(1-jitter,1+jitter)/max(.03,lp.get(i,0))**2)
            for i in ranked:
                r=self.pool[i];g=r['model'];chosen.append(i);loads[g]+=r['duration']
                for k,(_,c) in enumerate(self.cuts):cuts[k]+=c[i]
                result=visit(occupied|self.masks[i])
                for k,(_,c) in enumerate(self.cuts):cuts[k]-=c[i]
                loads[g]-=r['duration'];chosen.pop()
                if result is not None:return result
            self.stats['backtracks'] += 1
            return None
        result=visit(used)
        self.stats['nodes'] += nodes
        return result

    def schedule(self, routes, deadline, max_nodes=100000):
        """Feasibility-preserving aircraft and battery list-search by model."""
        P=self.P; result=[]; nodes=0
        for g in self.groups:
            jobs=[r for r in routes if r['model']==g]
            if not jobs:continue
            ids=sorted(k for k,v in P.data['aircraft'].items() if v==g)
            latest=[min(route_latest(P,r),self.cap-r['duration'] if self.cap is not None else math.inf) for r in jobs]
            memo=set()
            def visit(mask,ua,ba,rows):
                nonlocal nodes
                nodes+=1
                if not mask:return rows
                if nodes > max_nodes or time.perf_counter()>=deadline:return None
                key=(mask,tuple(sorted(round(x,6) for x in ua)),tuple(sorted(round(x,6) for x in ba)))
                if key in memo:return None
                memo.add(key)
                u=min(range(len(ua)),key=ua.__getitem__);b=min(range(len(ba)),key=ba.__getitem__)
                start=max(ua[u],ba[b]); opts=[i for i in range(len(jobs)) if mask>>i&1]
                if any(start>latest[i]+1e-7 for i in opts):return None
                if self.cap is not None and sum(jobs[i]['duration'] for i in opts)>sum(max(0,self.cap-x) for x in ua)+1e-7:return None
                for i in sorted(opts,key=lambda i:(latest[i],-jobs[i]['duration'])):
                    r=jobs[i];us=ua.copy();bs=ba.copy();ret=start+r['duration'];ready=ret+r['charge']
                    us[u]=ret;bs[b]=ready
                    row=dict(route=r,start=start,orders=[list(x) for _,x in r['stops']],sortie='T',aircraft=ids[u],battery=f'{g}-BAT-{b+1:02}',battery_ready=ready)
                    row['return']=ret
                    found=visit(mask^(1<<i),us,bs,rows+[row])
                    if found is not None:return found
                return None
            found=visit((1<<len(jobs))-1,[0.]*len(ids),[0.]*P.data['K'][g],[])
            if found is None:
                self.stats['schedule_failures']+=1;self.stats['schedule_nodes']+=nodes
                return None
            result.extend(found)
        for i,row in enumerate(sorted(result,key=lambda row:(row['start'],row['route']['id'])),1):row['sortie']=f'T-{i:03}'
        self.stats['scheduled_covers']+=1;self.stats['schedule_nodes']+=nodes
        return result

    def build(self, rng, deadline, mode='greedy', objective='energy', pheromone=None,
              fixed=(), cover_seconds=1., schedule_seconds=.5):
        selected=self.cover(rng,min(deadline,time.perf_counter()+cover_seconds),mode,objective,pheromone,fixed)
        if selected is None:return None
        return self.schedule(selected,min(deadline,time.perf_counter()+schedule_seconds))


if __name__ == '__main__':
    import argparse,json
    from pathlib import Path
    from legacy_routes import Physics
    from benchmark import station_audit
    from support import PROJECT,dump
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=30);p.add_argument('--cap',type=float,default=6000)
    p.add_argument('--method',default='greedy');p.add_argument('--objective',default='energy');p.add_argument('--name',default='construction_probe')
    a=p.parse_args();P=Physics();pool=json.loads((PROJECT/'evidence/contest-baselines-v4/pool_q2.json').read_text(encoding='utf-8'))
    c=Constructor(P,pool,a.cap if a.cap else None);rng=random.Random(42);beg=time.perf_counter();deadline=beg+a.seconds;attempts=0;found=None
    while time.perf_counter()<deadline:
        attempts+=1;rows=c.build(rng,deadline,mode=a.method,objective=a.objective)
        if rows is not None:
            found=dict(transport=rows,relay=[],resources=[2,6]);break
    report=dict(attempts=attempts,elapsed_s=time.perf_counter()-beg,stats=dict(c.stats),found=found is not None)
    if found is not None:
        report.update(energy_kwh=sum(r['route']['energy'] for r in rows),completion_s=max(r['return'] for r in rows),station_audit=station_audit(P,rows))
        dump(PROJECT/'evidence/contest-baselines-v6'/a.name/'solution.json',found)
    dump(PROJECT/'evidence/contest-baselines-v6'/a.name/'diagnostic.json',report);print(report,flush=True)
