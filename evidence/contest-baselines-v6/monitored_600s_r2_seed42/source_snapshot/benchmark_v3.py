"""Aligned-horizon energy experiments. No paper routes/schedules used as search inputs."""
import argparse
import copy
import math
import random
import time
from collections import defaultdict
from pathlib import Path
from benchmark_v2 import load,digest,solution_metrics,key,validate_solution,RepairGreedy,V1
from benchmark import Constructor,station_audit
from support import PROJECT,dump
from legacy_routes import Physics
import master_v2
import joint_v2

V3=PROJECT/'evidence/contest-baselines-v3'
CAPS={'Q2':dict(C=6000.,E=None,N=None),'Q3':dict(C=5939.9,E=68.9999,N=23)}

def cap_errors(sol,question):
    m=solution_metrics(sol);c=CAPS[question];errors=[]
    if m['completion_s']>c['C']+1e-6:errors.append('completion_cap')
    if c['E'] is not None and m['energy_kwh']>c['E']+1e-7:errors.append('energy_cap')
    if c['N'] is not None and m['transport_sorties']>c['N']:errors.append('transport_sortie_cap')
    return errors

def run(a):
    q=a.question;method=a.method;cap=CAPS[q];base=V3/a.name;base.mkdir(parents=True,exist_ok=False)
    P=Physics();pool=load(V1/f'pool_{q.lower()}.json');sites=load(V1/'stations.json');atoms=load(V1/'atoms.json')
    ctor=Constructor(P,pool,'energy');greedy=RepairGreedy(P,pool,'energy');rng=random.Random(42)
    began=time.perf_counter();deadline=began+a.seconds;best=None;trace=[];checkpoints={};attempts=0;decoders=0;callbacks=0
    rejected=defaultdict(int);guide_updates=[];joint_v2.OUT=base/'decoders';joint_v2.OUT.mkdir()
    cp_targets=[float(s) for s in a.checkpoints.split(',')];assert max(cp_targets)==a.seconds
    def retain(sol,info=None):
        nonlocal best,callbacks
        if sol is None:return False
        info=info or {};found=info.get('found_perf',time.perf_counter())-began;callbacks+=int('found_perf' in info)
        if found>a.seconds+1e-6:return False
        violations=cap_errors(sol,q)
        if violations:
            for v in violations:rejected[v]+=1
            return False
        station=station_audit(P,sol['transport'])
        assert station['boxes']==station['unique_boxes']==80 and station['late_boxes']==station['hard_violations']==0
        if best is not None and key(sol,'energy')>=key(best,'energy'):return False
        best=copy.deepcopy(sol);m=solution_metrics(sol)
        trace.append(dict(found_s=found,origin=info.get('origin','search'),attempt=attempts,**m))
        dump(base/'best_solution.json',best)
        for target in cp_targets:
            if found<=target:
                stem=f'checkpoint_{target:g}s';dump(base/f'{stem}_solution.json',best)
                checkpoints[str(target)]=dict(checkpoint_s=target,best_found_s=found,metrics=m)
        dump(base/'search_progress.json',dict(question=q,method=method,trace=trace,cap=cap,attempts=attempts))
        print('BEST',q,method,trace[-1],flush=True);return True
    def lower_bounds(rows):
        work={g:sum(r['route']['duration'] for r in rows if r['route']['model']==g)/P.data['M'][g] for g in P.models}
        E=sum(r['route']['energy'] for r in rows)
        violations=[max(0,max(work.values())/cap['C']-1)]
        if cap['E'] is not None:violations.append(max(0,E/cap['E']-1))
        if cap['N'] is not None:violations.append(max(0,len(rows)/cap['N']-1))
        return max(violations),max(r['return'] for r in rows)/cap['C'],E
    def decode(rows):
        nonlocal decoders
        # Necessary bounds only: failed bounds prove this group cannot meet caps.
        if lower_bounds(rows)[0]>1e-9:
            rejected['necessary_work_energy_or_count_bound']+=1;return None
        left=deadline-time.perf_counter()
        if left<=.2:return None
        if q=='Q2' and max(r['return'] for r in rows)<=cap['C']+1e-6:
            return dict(transport=rows,relay=[],resources=[2,6])
        decoders+=1;seconds=min(12.,left)
        def observe(sol,info):return retain(sol,dict(**info,origin='fixed_group_cp_callback'))
        if q=='Q2':
            def observer(result,info):
                return observe(dict(transport=master_v2.decode(P,result,retime=False),relay=[],resources=[2,6]),info)
            result=master_v2.solve(P,{r['route']['id']:r['route'] for r in rows},seconds=seconds,seed=42+decoders,workers=1,
                objectives=('C',),fixed_D=0,max_C=cap['C'],delivery_mode='batch',warm=None,
                evidence_path=base/'decoders'/f'call_{decoders:05}.json',deadline_monotonic=deadline,
                incumbent_callback=observer)
            if not result['selected']:return None
            return dict(transport=master_v2.decode(P,result,retime=False),relay=[],resources=[2,6])
        chosen=[r['route'] for r in rows]
        return joint_v2.solve(name=f'call_{decoders:05}',pool=chosen,atoms={r['id']:atoms[r['id']] for r in chosen},
            sites_override=sites,seconds=seconds,slots=4,objectives=('E','C'),zero_late=True,workers=1,
            seed=42+decoders,max_C=cap['C'],max_E=cap['E'],max_transport=cap['N'],
            deadline=time.monotonic()+seconds,incumbent_callback=observe)
    # Fresh ordinary greedy initialization is part of each search budget. It is
    # only a phase-I search guide until ALL final caps and constraints pass.
    guide,_=RepairGreedy(P,pool,'time').repair(42)
    assert guide is not None
    guide_rank=lower_bounds(guide)
    if method=='cp_sat':
        if q=='Q2':
            def observer(result,info):
                return retain(dict(transport=master_v2.decode(P,result,retime=False),relay=[],resources=[2,6]),dict(**info,origin='full_pool_cp_callback'))
            result=master_v2.solve(P,{r['id']:r for r in pool},seconds=max(.1,deadline-time.perf_counter()),seed=42,
                workers=1,objectives=('E','C'),fixed_D=0,max_C=cap['C'],delivery_mode='batch',warm=None,
                evidence_path=base/'cp_evidence.json',deadline_monotonic=deadline,incumbent_callback=observer)
            if result['selected']:retain(dict(transport=master_v2.decode(P,result,retime=False),relay=[],resources=[2,6]))
        else:
            sol=joint_v2.solve(name='full_pool',pool=pool,atoms=atoms,sites_override=sites,seconds=max(.1,deadline-time.perf_counter()),
                slots=4,objectives=('E','C'),zero_late=True,workers=1,seed=42,warm=None,
                max_C=cap['C'],max_E=cap['E'],max_transport=cap['N'],deadline=time.monotonic()+max(.1,deadline-time.perf_counter()),
                incumbent_callback=lambda s,i:retain(s,dict(**i,origin='full_pool_cp_callback')))
            retain(sol)
    else:
        pheromone={};seen=set();weights=[1.,1.,1.];rewards=[0.,0.,0.];uses=[0,0,0]
        while time.perf_counter()<deadline:
            attempts+=1;operator=0
            if method=='greedy':
                rows,_=greedy.build_profile(rng,mix=[0.,.05,.15,.3,.5,.75,1.][(attempts-1)%7],
                    time_power=rng.choice([.55,.7,.85,1.]),energy_power=rng.choice([.6,.8,1.]),jitter=rng.choice([0.,.015,.035,.07]))
            elif method=='aco':rows=ctor.build(rng,mode='aco',pheromone=pheromone)
            else:
                operator=rng.choices(range(3),weights=weights)[0];uses[operator]+=1
                rr=[r['route'] for r in guide];k=max(2,math.ceil(len(rr)*rng.uniform(.15,.4)))
                if operator==0:remove=set(rng.sample(range(len(rr)),min(k,len(rr))))
                elif operator==1:remove=set(sorted(range(len(rr)),key=lambda i:rr[i]['energy']/len(rr[i]['boxes']),reverse=True)[:k])
                else:
                    anchor=rng.choice(rr)['stops'][0][0]
                    remove=set(sorted(range(len(rr)),key=lambda i:0 if rr[i]['stops'][0][0]==anchor else P.geo[anchor,rr[i]['stops'][0][0]][0])[:k])
                rows=ctor.build(rng,mode='random',fixed=[r for i,r in enumerate(rr) if i not in remove],temperature=1.5)
            if rows is None:rejected['construction_dead_end']+=1;continue
            rank=lower_bounds(rows);phase_improved=rank<guide_rank
            if phase_improved:
                guide=rows;guide_rank=rank;guide_updates.append(dict(found_s=time.perf_counter()-began,rank=rank,sorties=len(rows)))
            elif method=='alns' and best is None:
                delta=(rank[0]-guide_rank[0])*100+(rank[1]-guide_rank[1])
                temp=.1*max(.01,1-(time.perf_counter()-began)/a.seconds)
                if rng.random()<math.exp(-max(0,delta)/temp):guide=rows;guide_rank=rank
            signature=tuple(sorted(r['route']['id'] for r in rows))
            # Q2 raw schedules with same groups may differ; do not skip them.
            if q=='Q3' and signature in seen:continue
            if q=='Q3':seen.add(signature)
            sol=decode(rows);improved=retain(sol)
            if best is not None and method=='alns':guide=best['transport'];guide_rank=lower_bounds(guide)
            if method=='aco':
                for rid in list(pheromone):pheromone[rid]=max(.05,pheromone[rid]*.9)
                for row in (best['transport'] if best else guide):
                    rid=row['route']['id'];pheromone[rid]=min(20,pheromone.get(rid,1.)+1.)
            if method=='alns':
                rewards[operator]+=8. if improved else 3. if phase_improved else 1. if sol else 0.
                if attempts%25==0:
                    for j in range(3):weights[j]=.8*weights[j]+.2*(rewards[j]/max(1,uses[j])+.1)
                    rewards=[0.,0.,0.];uses=[0,0,0]
    record=dict(question=q,objective='energy',method=method,seed=42,budget_s=a.seconds,search_wall_s=time.perf_counter()-began,
        caps=cap,attempts=attempts,decoder_calls=decoders,callbacks=callbacks,rejections=dict(rejected),trace=trace,
        phase_I_guide_updates=guide_updates,checkpoints=[],paper_solution_used=False)
    verified={}
    for target in cp_targets:
        stem=f'checkpoint_{target:g}s';path=base/f'{stem}_solution.json'
        if not path.exists():
            record['checkpoints'].append(dict(checkpoint_s=target,status='NO_VALIDATED_SOLUTION_WITHIN_CAPS',metrics=None));continue
        assert not cap_errors(load(path),q)
        h=digest(path)
        if h in verified:
            metrics,audit=verified[h];dump(base/f'{stem}_validation.json',audit)
        else:
            metrics,audit=validate_solution(q,path,base/f'{stem}_validation.json');verified[h]=(metrics,audit)
        record['checkpoints'].append(dict(checkpoints[str(target)],status='VALIDATED_FEASIBLE',metrics=metrics,solution_sha256=h))
    record['total_wall_s']=time.perf_counter()-began;record['status']='COMPLETED'
    dump(base/'run.json',record);print('FINISH',q,method,record['checkpoints'],flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--question',choices=['Q2','Q3'],required=True)
    p.add_argument('--method',choices=['greedy','aco','alns','cp_sat'],required=True);p.add_argument('--seconds',type=float,default=600.)
    p.add_argument('--checkpoints',default='180,600');p.add_argument('--name',required=True);run(p.parse_args())
