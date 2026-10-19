"""Corrected energy comparison, shared independently validated feasible initials."""
import argparse
from collections import defaultdict
import copy
import math
import random
import time
from benchmark_v2 import load,digest,solution_metrics,key,validate_solution
from benchmark import due,route_latest,station_audit
from pattern_v4 import V4
from legacy_routes import Physics
from support import dump
import master_v2
import joint_v4

CAPS={'Q2':dict(C=6000.,E=None,N=None),'Q3':dict(C=5939.9,E=None,N=None)}

def cap_errors(sol,q):
    return ['completion_cap'] if solution_metrics(sol)['completion_s']>CAPS[q]['C']+1e-6 else []

class CapConstructor:
    """EDF randomized construction with forward cap checks, including fixed repairs."""
    def __init__(self,P,pool,cap):
        self.P=P;self.pool=pool;self.cap=cap;self.by=defaultdict(list);self.latest={}
        for r in pool:
            self.latest[r['id']]=min(route_latest(P,r),cap-r['duration'])
            for b in r['boxes']:self.by[b].append(r)
    def build(self,rng,mix,mode='greedy',pheromone=None,fixed=()):
        P=self.P;remaining=set(P.boxes);ua={g:[0.]*P.data['M'][g] for g in P.models};ba={g:[0.]*P.data['K'][g] for g in P.models}
        fixedbox={b:r for r in fixed for b in r['boxes']};reserved=set(fixedbox);rows=[]
        while remaining:
            focus=min(remaining,key=lambda b:(due(P,b),-P.boxes[b]['priority'],b));forced=fixedbox.get(focus);opts=[]
            for r in ([forced] if forced else self.by[focus]):
                bs=set(r['boxes'])
                if not bs<=remaining or (not forced and bs&reserved):continue
                g=r['model'];start=max(min(ua[g]),min(ba[g]))
                if start>self.latest[r['id']]+1e-7:continue
                opts.append((r,start,(start+r['duration'])/len(bs)**rng.choice([.7,.85,1.]),r['energy']/len(bs)**.8))
            if not opts:return None
            mt=min(x[2] for x in opts);me=min(x[3] for x in opts)
            rated=sorted([(mix*t/mt+(1-mix)*e/me,r['id'],r,s) for r,s,t,e in opts],key=lambda v:(v[0],v[1]))
            if mode=='aco':
                choices=rated[:min(32,len(rated))];weights=[pheromone.get(v[1],1.)/(v[0]/choices[0][0])**2 for v in choices]
                _,_,r,start=rng.choices(choices,weights=weights)[0]
            elif mode=='random':
                choices=rated[:min(20,len(rated))];_,_,r,start=rng.choices(choices,weights=[math.exp(-i/3) for i in range(len(choices))])[0]
            else:_,_,r,start=min(rated,key=lambda v:v[0]*(1+rng.uniform(-.08,.08)))
            g=r['model'];u=min(range(len(ua[g])),key=ua[g].__getitem__);b=min(range(len(ba[g])),key=ba[g].__getitem__)
            row=dict(route=r,start=start,orders=[list(bs) for _,bs in r['stops']],sortie=f'T-{len(rows)+1:03}',
                aircraft=sorted(k for k,v in P.data['aircraft'].items() if v==g)[u],battery=f'{g}-BAT-{b+1:02}',battery_ready=start+r['duration']+r['charge'])
            row['return']=start+r['duration'];rows.append(row);ua[g][u]=row['return'];ba[g][b]=row['battery_ready']
            remaining.difference_update(r['boxes']);reserved.difference_update(r['boxes'])
        return rows

def run(a):
    q=a.question;method=a.method;cap=CAPS[q];base=V4/a.name;base.mkdir(exist_ok=False,parents=True)
    P=Physics();pool=load(V4/f'pool_{q.lower()}.json');sites=load(V4/'sites.json');atoms=load(V4/'atoms.json')
    initial_path=V4/f'common_{q.lower()}.json';initial=load(initial_path)
    initial_audit=load(V4/f'common_{q.lower()}_validation.json')
    assert initial_audit['status']=='passed' and initial_audit['solution_sha256']==digest(initial_path) and not cap_errors(initial,q)
    ctor=CapConstructor(P,pool,cap['C']);rng=random.Random(42);began=time.perf_counter();deadline=began+a.seconds
    best=None;trace=[];checkpoints={};attempts=0;decoders=0;callbacks=0;reject=defaultdict(int)
    targets=[float(t) for t in a.checkpoints.split(',')];assert max(targets)==a.seconds
    joint_v4.OUT=base/'decoders';joint_v4.OUT.mkdir();seen={}
    def retain(sol,info=None):
        nonlocal best,callbacks
        if sol is None:return False
        info=info or {};found=info.get('found_perf',time.perf_counter())-began;callbacks+=int('found_perf' in info)
        if found>a.seconds+1e-6:return False
        if cap_errors(sol,q):reject['completion_cap']+=1;return False
        audit=station_audit(P,sol['transport'])
        assert audit['boxes']==audit['unique_boxes']==80 and audit['late_boxes']==audit['hard_violations']==0
        if best is not None and key(sol,'energy')>=key(best,'energy'):return False
        best=copy.deepcopy(sol);m=solution_metrics(sol);trace.append(dict(found_s=found,origin=info.get('origin','search'),attempt=attempts,**m))
        dump(base/'best_solution.json',best)
        for t in targets:
            if found<=t:
                dump(base/f'checkpoint_{t:g}s_solution.json',best);checkpoints[str(t)]=dict(checkpoint_s=t,best_found_s=found,metrics=m)
        dump(base/'search_progress.json',dict(question=q,method=method,attempts=attempts,trace=trace));print('BEST',q,method,trace[-1],flush=True)
        return True
    retain(initial,dict(origin='shared_independent_validated_initial'))
    def decode(rows):
        nonlocal decoders
        left=deadline-time.perf_counter()
        if left<.2:return None
        if q=='Q2':return dict(transport=rows,relay=[],resources=[2,6])
        sig=tuple(sorted(r['route']['id'] for r in rows))
        # Retry a group after UNKNOWN, at most three times; never treat it as infeasible.
        if seen.get(sig,0)>=3:return None
        seen[sig]=seen.get(sig,0)+1;decoders+=1;seconds=min(10,left)
        return joint_v4.solve(name=f'call_{decoders:05}',pool=[r['route'] for r in rows],atoms=atoms,sites_override=sites,
            seconds=seconds,slots=6,objectives=('E','C'),zero_late=True,workers=1,seed=42+decoders,max_C=cap['C'],
            warm=dict(transport=rows,relay=[]),deadline=time.monotonic()+seconds,
            incumbent_callback=lambda s,i:retain(s,dict(**i,origin='joint_cp_decoder')))
    if method=='cp_sat':
        if q=='Q2':
            def observer(r,i):return retain(dict(transport=master_v2.decode(P,r,retime=False),relay=[],resources=[2,6]),dict(**i,origin='full_pool_cp'))
            result=master_v2.solve(P,{r['id']:r for r in pool},seconds=deadline-time.perf_counter(),seed=42,workers=1,
                objectives=('E','C'),fixed_D=0,max_C=cap['C'],delivery_mode='batch',warm=initial['transport'],
                evidence_path=base/'cp_evidence.json',deadline_monotonic=deadline,incumbent_callback=observer)
            if result['selected']:retain(dict(transport=master_v2.decode(P,result,retime=False),relay=[],resources=[2,6]))
        else:
            result=joint_v4.solve(name='full_pool',pool=pool,atoms=atoms,sites_override=sites,seconds=deadline-time.perf_counter(),slots=6,
                objectives=('E','C'),zero_late=True,workers=1,seed=42,warm=initial,complete_warm=True,
                max_C=cap['C'],deadline=time.monotonic()+max(.1,deadline-time.perf_counter()),
                incumbent_callback=lambda s,i:retain(s,dict(**i,origin='full_pool_cp')))
            retain(result)
    else:
        pheromone={r['route']['id']:1. for r in initial['transport']};weights=[1.,1.,1.];rewards=[0.,0.,0.];uses=[0,0,0]
        while time.perf_counter()<deadline:
            attempts+=1;op=0;fixed=()
            if method=='alns':
                op=rng.choices(range(3),weights=weights)[0];uses[op]+=1;rr=[r['route'] for r in best['transport']]
                k=max(2,math.ceil(len(rr)*rng.uniform(.1,.35)))
                if op==0:remove=set(rng.sample(range(len(rr)),k))
                elif op==1:remove=set(sorted(range(len(rr)),key=lambda i:rr[i]['energy']/len(rr[i]['boxes']),reverse=True)[:k])
                else:
                    anchor=rng.choice(rr)['stops'][0][0];remove=set(sorted(range(len(rr)),key=lambda i:0 if rr[i]['stops'][0][0]==anchor else P.geo[anchor,rr[i]['stops'][0][0]][0])[:k])
                fixed=[r for i,r in enumerate(rr) if i not in remove]
            rows=ctor.build(rng,mix=rng.choice([0,.2,.5,.8,1.]),mode='aco' if method=='aco' else 'random' if method=='alns' else 'greedy',pheromone=pheromone,fixed=fixed)
            if rows is None:reject['construction_dead_end']+=1;continue
            sol=decode(rows);improved=retain(sol)
            if method=='aco':
                for rid in list(pheromone):pheromone[rid]=max(.05,pheromone[rid]*.95)
                for r in best['transport']:pheromone[r['route']['id']]=min(30,pheromone.get(r['route']['id'],1)+1)
            if method=='alns':
                rewards[op]+=8 if improved else 1 if sol else 0
                if attempts%25==0:
                    for j in range(3):weights[j]=.8*weights[j]+.2*(rewards[j]/max(1,uses[j])+.1)
                    rewards=[0.,0.,0.];uses=[0,0,0]
    record=dict(question=q,objective='energy',method=method,seed=42,budget_s=a.seconds,search_wall_s=time.perf_counter()-began,
        caps=cap,attempts=attempts,decoder_calls=decoders,callbacks=callbacks,rejections=dict(reject),trace=trace,checkpoints=[],
        paper_solution_used=False,shared_initial_sha256=digest(initial_path),shared_initial_metrics=solution_metrics(initial))
    verified={}
    for t in targets:
        path=base/f'checkpoint_{t:g}s_solution.json';assert not cap_errors(load(path),q);h=digest(path)
        if h in verified:m,audit=verified[h];dump(base/f'checkpoint_{t:g}s_validation.json',audit)
        else:m,audit=validate_solution(q,path,base/f'checkpoint_{t:g}s_validation.json');verified[h]=(m,audit)
        record['checkpoints'].append(dict(checkpoints[str(t)],status='VALIDATED_FEASIBLE',metrics=m,solution_sha256=h))
    record['total_wall_s']=time.perf_counter()-began;record['status']='COMPLETED';dump(base/'run.json',record)
    print('FINISH',q,method,record['checkpoints'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--question',choices=['Q2','Q3'],required=True);p.add_argument('--method',choices=['greedy','aco','alns','cp_sat'],required=True)
    p.add_argument('--seconds',type=float,default=600);p.add_argument('--checkpoints',default='180,600');p.add_argument('--name',required=True);run(p.parse_args())
