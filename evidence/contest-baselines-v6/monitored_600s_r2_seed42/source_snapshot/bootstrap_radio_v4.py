"""Reduce radio location symmetry by independent set-cover probes before full runs."""
import argparse
import time
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from benchmark_v2 import load,validate_solution,solution_metrics
from pattern_v4 import V4
from support import dump
import joint_v4

def main(seconds=180,warm=False,suffix=''):
    beg=time.perf_counter();ss=load(V4/'sites.json');atoms=load(V4/'atoms.json');base=load(V4/f'common_q2{suffix}.json')
    chosen=[r['route'] for r in base['transport']];pool=load(V4/'pool_q3.json');index={s['id']:i for i,s in enumerate(ss)}
    allowed=sorted(set(tuple(sorted(a['sites'])) for r in chosen for a in atoms[r['id']]))
    A=np.array([[int(s['id'] in row) for s in ss] for row in allowed],float)
    joint_v4.OUT=V4/(('preparation/radio_bootstrap_warm' if warm else 'preparation/radio_bootstrap')+suffix);records=[];found=None
    for attempt in range(4):
        rng=np.random.default_rng(42+attempt)
        costs=np.array([1+s['ready_offset']/10000+s['back']/10000 for s in ss])*(.85+.3*rng.random(len(ss)))
        res=milp(costs,integrality=np.ones(len(ss)),bounds=Bounds(np.zeros(len(ss)),np.ones(len(ss))),constraints=LinearConstraint(A,np.ones(len(A)),np.full(len(A),np.inf)),options={'time_limit':5})
        assert res.x is not None
        ids=[s['id'] for i,s in enumerate(ss) if res.x[i]>.5]
        # Include close alternatives for each selected coverage pattern, so an
        # earliest blind interval is not forced to wait for a distant location.
        candidates={s['id']:s for s in ss if s['id'] in ids}
        for sid in ids:
            origin=ss[index[sid]]
            near=sorted(ss,key=lambda s:(len(set(origin['cover'])-set(s['cover'])),s['ready_offset']))
            for s in near[:2]:candidates[s['id']]=s
        site_ids=list(candidates);left=seconds-(time.perf_counter()-beg)
        if left<1:break
        allowed_ids=set(site_ids)
        eligible=[r for r in pool if all(set(a['sites'])&allowed_ids for a in atoms[r['id']])]
        seconds_this=min(60,left)
        def observe(sol,info):dump(V4/'common_q3.json',sol)
        print('RADIO TEMPLATE',attempt,site_ids,'routes',len(eligible),flush=True)
        found=joint_v4.solve(name=f'template_{attempt:02}',pool=eligible,atoms=atoms,sites_override=ss,
            site_ids=site_ids,slots=4,seconds=seconds_this,objectives=('C',),zero_late=True,max_C=5939.9,
            workers=4,seed=42+attempt,stop_on_first=True,deadline=time.monotonic()+seconds_this,
            incumbent_callback=observe,warm=dict(transport=base['transport'],relay=[]) if warm else None)
        records.append(dict(attempt=attempt,sites=site_ids,eligible_routes=len(eligible),found=found is not None))
        dump(joint_v4.OUT/'progress.json',dict(records=records,wall_s=time.perf_counter()-beg))
        if found is not None:break
    if found is None:raise RuntimeError('No Q3 feasible initial; formal matrix remains gated')
    dump(V4/'common_q3.json',found);metrics,_=validate_solution('Q3',V4/'common_q3.json',V4/'common_q3_validation.json')
    assert metrics['completion_s']<=5939.9+1e-6
    dump(V4/'preparation/joint_summary.json',dict(wall_s=time.perf_counter()-beg,metrics=metrics,records=records,no_paper_results_used=True,
        earlier_full_site_attempts=['joint/fixed_independent_transport','joint/reschedule_independent_groups'],
        shared_common_search_limits='Earlier 240s full-site preparation plus current bounded template probes; all disclosed separately.'))
    print('COMMON Q3 VALIDATED',metrics,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=180);p.add_argument('--warm',action='store_true');p.add_argument('--suffix',default='');a=p.parse_args();main(a.seconds,a.warm,a.suffix)
