"""Independent relay-window enumeration followed by a small transport CP model."""
from collections import defaultdict
import argparse
import itertools
import math
import time
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from pattern_v4 import V4
from benchmark_v2 import load,validate_solution,solution_metrics
from support import dump
from legacy_routes import Physics,charge
import master_v4
import joint_v4

def intersect(a,b):
    pieces=sorted((max(x,z),min(y,w)) for x,y in a for z,w in b if max(x,z)<=min(y,w))
    merged=[]
    for lo,hi in pieces:
        if merged and lo<=merged[-1][1]+1:merged[-1]=(merged[-1][0],max(merged[-1][1],hi))
        else:merged.append((lo,hi))
    return merged

def relay(site,start,finish,slot):
    e=site['fly_energy']+1.1*(finish-start-site['arrival_offset'])/3600
    r=dict(sortie=f'INIT-R-{slot+1:03}',slot=slot,site=site,start=start,arrival=start+site['arrival_offset'],
        link_complete=start+site['ready_offset'],service_end=finish,energy=e,SOC=1-e/3.2,charge=charge(1-e/3.2,1800))
    r['return']=finish+site['back'];r['component_ready']=r['return']+r['charge'];r['aircraft_ready']=r['return']+300
    return r

def main(seconds=240):
    begin=time.perf_counter();P=Physics();ss=load(V4/'sites.json');atoms=load(V4/'atoms.json');pool=load(V4/'pool_q3.json');warm=load(V4/'common_q2_compact.json')
    target=[r['route'] for r in warm['transport']];allowed=sorted(set(tuple(sorted(a['sites'])) for r in target for a in atoms[r['id']]))
    A=np.array([[int(s['id'] in row) for s in ss] for row in allowed],float);sets=[]
    for seed in range(5):
        rng=np.random.default_rng(100+seed);cost=np.array([100+s['back']/10000 for s in ss])+rng.random(len(ss))
        res=milp(cost,integrality=np.ones(len(ss)),bounds=Bounds(np.zeros(len(ss)),np.ones(len(ss))),constraints=LinearConstraint(A,np.ones(len(A)),np.full(len(A),np.inf)),options={'time_limit':3})
        if res.x is not None:
            loc=[s for i,s in enumerate(ss) if res.x[i]>.5]
            if len(loc)<=4:sets.append(loc)
            print('WINDOW SITE SET',seed,[s['id'] for s in loc],flush=True)
    directory=V4/'preparation/window_bootstrap';directory.mkdir(parents=True,exist_ok=True);records=[];attempt=0
    for loc in sets:
        # Repeat one location if the cover uses only two points.
        if len(loc)==2:loc=loc+[loc[0]]
        for order in itertools.permutations(loc,3):
            for end_first in [1500,1800,1200,2100,2400]:
                if time.perf_counter()-begin>seconds:raise RuntimeError('Window bootstrap budget exhausted; gate stays closed')
                first=relay(order[0],0.,end_first,0);last_start=math.ceil(first['aircraft_ready']*10-1e-7)/10
                middle_end=math.floor((5939.9-order[1]['back'])*10+1e-7)/10
                last_end=math.floor((5939.9-order[2]['back'])*10+1e-7)/10
                rr=[first,relay(order[1],0.,middle_end,1),relay(order[2],last_start,last_end,2)]
                if any(r['service_end']<r['link_complete'] or r['energy']>2.56 or r['energy']<=0 for r in rr):continue
                intervals={}
                for r in pool:
                    windows=[(0,math.floor((5939.9-r['duration'])*10+1e-7))]
                    for a in atoms[r['id']]:
                        cand=[]
                        for v in rr:
                            if v['site']['id'] not in a['sites']:continue
                            lo=math.ceil(v['link_complete']*10-1e-7)-math.floor(a['a']*10+1e-7)
                            hi=math.floor(v['service_end']*10+1e-7)-math.ceil(a['b']*10-1e-7)
                            if lo<=hi:cand.append((lo,hi))
                        windows=intersect(windows,cand)
                        if not windows:break
                    if windows:intervals[r['id']]=sorted(set(windows))
                possible=[r for r in pool if r['id'] in intervals]
                if set(b for r in possible for b in r['boxes'])!=set(P.boxes):continue
                attempt+=1;left=seconds-(time.perf_counter()-begin);budget=min(3,left)
                result=master_v4.solve(P,{r['id']:r for r in possible},seconds=budget,workers=4,seed=42+attempt,
                    objectives=('C',),fixed_D=0,max_C=5939.9,delivery_mode='batch',warm=warm['transport'],
                    allowed_start_intervals=intervals,stop_on_first=True,evidence_path=directory/f'call_{attempt:03}.json',
                    deadline_monotonic=time.perf_counter()+budget)
                records.append(dict(attempt=attempt,sites=[s['id'] for s in order],end_first=end_first,routes=len(possible),status=result['evidence']))
                dump(directory/'progress.json',dict(records=records,wall_s=time.perf_counter()-begin))
                if not result['selected']:continue
                transport=master_v4.decode(P,result,retime=False);sol=dict(transport=transport,relay=rr,resources=[2,6]);joint_v4.color(sol,P)
                dump(V4/'common_q3.json',sol);metrics,_=validate_solution('Q3',V4/'common_q3.json',V4/'common_q3_validation.json')
                assert metrics['completion_s']<=5939.9+1e-6
                dump(V4/'preparation/joint_summary.json',dict(wall_s=time.perf_counter()-begin,records=records,metrics=metrics,
                    no_paper_results_used=True,source='Independent set cover plus enumerated three-relay windows; CP transport schedule and full independent validation.'))
                print('COMMON Q3 VALIDATED',metrics,flush=True);return
    raise RuntimeError('No enumerated window template yielded feasible Q3; gate stays closed')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=240);a=p.parse_args();main(a.seconds)
