"""Repair-aware traditional baselines with actual incumbent checkpoints.

No paper routes, schedules, or objective values are used by this runner.
"""
import argparse
from collections import defaultdict
import copy
import hashlib
import json
import math
from pathlib import Path
import random
import time

from support import PROJECT, EVIDENCE as V1, inputs, dump
from legacy_routes import Physics
from legacy_validate import check
from legacy_validate_q3 import run as radio_check
from benchmark import Constructor, due, station_audit
import master_v2
import joint_v2

V2=PROJECT/'evidence/contest-baselines-v2'

def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def solution_metrics(sol):
    return dict(completion_s=max(r['return'] for r in sol['transport']+sol['relay']),
        energy_kwh=sum(r['route']['energy'] for r in sol['transport'])+sum(r['energy'] for r in sol['relay']),
        transport_sorties=len(sol['transport']),relay_sorties=len(sol['relay']))

def key(sol,objective):
    m=solution_metrics(sol)
    C,E=round(m['completion_s'],6),round(m['energy_kwh'],9)
    return (C,E) if objective=='time' else (E,C)


class RepairGreedy(Constructor):
    """Reconstruct after a dead end; multistart scores stay greedy at each step."""
    def build_profile(self,rng,mix=1.,time_power=.7,energy_power=.8,jitter=0.):
        P=self.P;remaining=set(P.boxes)
        ua={g:[0.]*P.data['M'][g] for g in P.models}
        ba={g:[0.]*P.data['K'][g] for g in P.models}
        rows=[]
        while remaining:
            focus=min(remaining,key=lambda b:(due(P,b),-P.boxes[b]['priority'],b))
            options=[]
            for r in self.by[focus]:
                if not set(r['boxes'])<=remaining:continue
                g=r['model'];start=max(min(ua[g]),min(ba[g]))
                if start>self.latest[r['id']]+1e-7:continue
                n=len(r['boxes'])
                options.append((r,start,(start+r['duration'])/n**time_power,r['energy']/n**energy_power))
            if not options:
                return None,dict(reason='construction_dead_end',focus=focus,remaining_boxes=len(remaining),scheduled_sorties=len(rows))
            min_t=min(v[2] for v in options);min_e=min(v[3] for v in options)
            ranked=[]
            for r,start,t,e in options:
                score=(mix*t/min_t+(1-mix)*e/min_e)*(1+jitter*rng.uniform(-1,1))
                ranked.append((score,r['id'],start,r))
            _,_,start,r=min(ranked,key=lambda v:(v[0],v[1]))
            g=r['model'];u=min(range(len(ua[g])),key=ua[g].__getitem__);b=min(range(len(ba[g])),key=ba[g].__getitem__)
            uid=sorted(k for k,v in P.data['aircraft'].items() if v==g)[u]
            row=dict(route=r,start=start,orders=[list(bs) for _,bs in r['stops']],
                sortie=f'T-{len(rows)+1:03}',aircraft=uid,battery=f'{g}-BAT-{b+1:02}',
                battery_ready=start+r['duration']+r['charge'])
            row['return']=start+r['duration'];rows.append(row)
            ua[g][u]=row['return'];ba[g][b]=row['battery_ready'];remaining.difference_update(r['boxes'])
        return rows,dict(reason='complete',scheduled_sorties=len(rows),remaining_boxes=0)

    def repair(self,seed):
        attempts=[]
        for mix in ([0.,1.,.75,.5,.25] if self.objective=='energy' else [1.,.75,.5,.25,0.]):
            rows,detail=self.build_profile(random.Random(seed),mix=mix)
            attempts.append(dict(mix=mix,**detail))
            if rows is not None:return rows,attempts
        return None,attempts


def validate_solution(question,path,output):
    sol=load(path);P=Physics()
    transport=check(sol['transport'],data=inputs())
    station=station_audit(P,sol['transport'])
    assert transport['summary']['valid'],transport['errors']
    assert station['boxes']==station['unique_boxes']==80
    assert station['late_boxes']==station['hard_violations']==0,station
    radio=None
    if question=='Q3':
        radio=radio_check(path,save=False)
        assert radio['summary']['valid'],radio['errors']
        assert radio['summary']['gap_seconds']==radio['summary']['unknown_intervals']==0
    result=dict(status='passed',solution_sha256=digest(path),transport=transport,station=station,radio=radio)
    dump(output,result)
    return dict(**solution_metrics(sol),**station),result


def prepare_initial():
    base=V2/'common_initial';base.mkdir(exist_ok=False,parents=True)
    began=time.perf_counter();P=Physics();manifest=dict(no_paper_results_used=True,runs=[])
    q3_rows=None
    for question in ['Q2','Q3']:
        pool=load(V1/f'pool_{question.lower()}.json')
        for objective in ['time','energy']:
            ctor=RepairGreedy(P,pool,objective)
            rows,attempts=ctor.repair(42)
            assert rows is not None,attempts
            assert check(rows,data=inputs())['summary']['valid']
            assert not station_audit(P,rows)['late_boxes']
            dump(base/f'{question}_{objective}_transport.json',dict(transport=rows,relay=[],resources=[2,6]))
            manifest['runs'].append(dict(question=question,objective=objective,repair_attempts=attempts,
                transport_signature=sorted(r['route']['id'] for r in rows)))
            if question=='Q2':
                dump(base/f'Q2_{objective}.json',dict(transport=rows,relay=[],resources=[2,6]))
            else:
                if q3_rows is not None:
                    assert sorted(r['route']['id'] for r in rows)==sorted(r['route']['id'] for r in q3_rows)
                q3_rows=rows
    sites=load(V1/'stations.json');atoms=load(V1/'atoms.json')
    chosen=[r['route'] for r in q3_rows]
    joint_v2.OUT=base/'cp_bootstrap'
    callbacks=[]
    def observe(sol,info):
        audit=station_audit(P,sol['transport'])
        assert audit['boxes']==80 and not audit['late_boxes'] and not audit['hard_violations']
        callbacks.append(dict(**info,**solution_metrics(sol)))
    sol=joint_v2.solve(name='neutral_time',pool=chosen,atoms={r['id']:atoms[r['id']] for r in chosen},
        sites_override=sites,seconds=30,slots=4,objectives=('C',),zero_late=True,workers=1,seed=43,
        deadline=time.monotonic()+30,incumbent_callback=observe)
    assert sol is not None,'Neutral joint bootstrap did not find a feasible solution'
    assert callbacks,'Q3 incumbent hook was not exercised'
    for objective in ['time','energy']:dump(base/f'Q3_{objective}.json',sol)
    manifest['joint_callback_count']=len(callbacks)
    for question in ['Q2','Q3']:
        for objective in ['time','energy']:
            name=f'{question}_{objective}'
            metrics,_=validate_solution(question,base/f'{name}.json',base/f'{name}_validation.json')
            manifest.setdefault('validated_initials',[]).append(dict(name=name,sha256=digest(base/f'{name}.json'),metrics=metrics))
    manifest['common_preprocessing_wall_s']=time.perf_counter()-began
    manifest['excluded_from_per_method_search_budget']=True
    dump(base/'manifest.json',manifest)
    print('COMMON INITIALS VERIFIED',manifest['validated_initials'],flush=True)


def run_one(args):
    q,o,m=args.question,args.objective,args.method
    base=V2/args.name;base.mkdir(exist_ok=False,parents=True)
    checkpoints=sorted(set(float(v) for v in args.checkpoints.split(',')))
    assert min(checkpoints)>0 and max(checkpoints)==args.seconds
    P=Physics();pool=load(V1/f'pool_{q.lower()}.json');sites=load(V1/'stations.json');atoms=load(V1/'atoms.json')
    ctor=Constructor(P,pool,o);greedy=RepairGreedy(P,pool,o);rng=random.Random(args.seed)
    initial_path=V2/'common_initial'/f'{q}_{o}.json'
    initial=load(initial_path)
    # The shared initial solution has already passed full independent validation.
    assert load(initial_path.with_name(initial_path.stem+'_validation.json'))['status']=='passed'
    began=time.perf_counter();deadline=began+args.seconds
    best=None;trace=[];attempts=0;failures=0;decoder_calls=0;callback_count=0;checkpoint_meta={}
    callback_errors=[]
    joint_v2.OUT=base/'decoders'
    joint_v2.OUT.mkdir()
    def retain(sol,info=None):
        nonlocal best,callback_count
        info=info or {}
        found=info.get('found_perf',time.perf_counter())-began
        callback_count+=int('found_perf' in info)
        if found>args.seconds+1e-6 or sol is None:return False
        station=station_audit(P,sol['transport'])
        assert station['boxes']==station['unique_boxes']==80 and not station['late_boxes'] and not station['hard_violations']
        if best is not None and key(sol,o)>=key(best,o):return False
        best=copy.deepcopy(sol);metrics=solution_metrics(sol)
        trace.append(dict(found_s=found,iteration=attempts,origin=info.get('origin','search'),**metrics))
        dump(base/'best_solution.json',best)
        for cp in checkpoints:
            if found<=cp:
                name=f'checkpoint_{cp:g}s'
                dump(base/f'{name}_solution.json',best)
                checkpoint_meta[str(cp)]=dict(checkpoint_s=cp,best_found_s=found,status='PENDING_FINAL_VALIDATION',metrics=metrics)
        dump(base/'search_progress.json',dict(question=q,objective=o,method=m,attempts=attempts,callbacks=callback_count,
            elapsed_s=time.perf_counter()-began,trace=trace,checkpoints=checkpoint_meta))
        print('BEST',q,o,m,trace[-1],flush=True)
        return True
    retain(initial,dict(origin='shared_repaired_greedy_initial'))
    current=copy.deepcopy(initial)
    def decode(rows,sub_seconds=12.):
        nonlocal decoder_calls
        if q=='Q2':return dict(transport=rows,relay=[],resources=[2,6])
        remaining=deadline-time.perf_counter()
        if remaining<=.25:return None
        decoder_calls+=1;chosen=[r['route'] for r in rows]
        def observer(sol,info):
            return retain(sol,dict(**info,origin='cp_schedule_incumbent'))
        return joint_v2.solve(name=f'call_{decoder_calls:04}',pool=chosen,
            atoms={r['id']:atoms[r['id']] for r in chosen},sites_override=sites,seconds=min(sub_seconds,remaining),
            slots=4,objectives=('C',) if o=='time' else ('E',),zero_late=True,workers=1,
            seed=args.seed+decoder_calls,deadline=time.monotonic()+min(sub_seconds,remaining),incumbent_callback=observer)
    if m=='cp_sat':
        if q=='Q2':
            def observer(res,info):
                sol=dict(transport=master_v2.decode(P,res,retime=False),relay=[],resources=[2,6])
                return retain(sol,dict(**info,origin='cp_full_pool_incumbent'))
            result=master_v2.solve(P,{r['id']:r for r in pool},seconds=max(.1,deadline-time.perf_counter()),
                seed=args.seed,workers=1,objectives=('C',) if o=='time' else ('E',),fixed_D=0,delivery_mode='batch',
                warm=initial['transport'],evidence_path=base/'cp_evidence.json',deadline_monotonic=deadline,incumbent_callback=observer)
            if result['selected']:
                retain(dict(transport=master_v2.decode(P,result,retime=False),relay=[],resources=[2,6]),dict(origin='cp_final'))
        else:
            result=joint_v2.solve(name='full_pool',pool=pool,atoms=atoms,sites_override=sites,
                seconds=max(.1,deadline-time.perf_counter()),slots=4,objectives=('C',) if o=='time' else ('E',),
                zero_late=True,workers=1,seed=args.seed,warm=initial,complete_warm=True,
                deadline=time.monotonic()+max(.1,deadline-time.perf_counter()),
                incumbent_callback=lambda sol,info:retain(sol,dict(**info,origin='cp_full_pool_incumbent')))
            if result:retain(result,dict(origin='cp_final'))
    else:
        pheromone={};seen=set();weights=[1.,1.,1.];rewards=[0.,0.,0.];uses=[0,0,0]
        while time.perf_counter()<deadline:
            attempts+=1;operator=0
            if m=='greedy':
                mixes=[0.,.05,.15,.3,.5,.75,1.] if o=='energy' else [1.,.85,.7,.5,.3,.15,0.]
                mix=mixes[(attempts-1)%len(mixes)]
                rows,_=greedy.build_profile(rng,mix=mix,time_power=rng.choice([.55,.7,.85,1.]),
                    energy_power=rng.choice([.6,.8,1.]),jitter=rng.choice([0.,.015,.035,.07]))
            elif m=='aco':rows=ctor.build(rng,mode='aco',pheromone=pheromone)
            else:
                operator=rng.choices(range(3),weights=weights)[0];uses[operator]+=1
                rr=[x['route'] for x in current['transport']]
                k=max(2,math.ceil(len(rr)*rng.uniform(.15,.4)))
                if operator==0:remove=set(rng.sample(range(len(rr)),min(k,len(rr))))
                elif operator==1:remove=set(sorted(range(len(rr)),key=lambda i:rr[i]['energy']/len(rr[i]['boxes']),reverse=True)[:k])
                else:
                    anchor=rng.choice(rr)['stops'][0][0]
                    remove=set(sorted(range(len(rr)),key=lambda i:0 if rr[i]['stops'][0][0]==anchor else P.geo[anchor,rr[i]['stops'][0][0]][0])[:k])
                fixed=[r for i,r in enumerate(rr) if i not in remove]
                rows=ctor.build(rng,mode='random',fixed=fixed,temperature=1.5)
            if rows is None:
                failures+=1
                continue
            signature=tuple(sorted(r['route']['id'] for r in rows))
            if q=='Q3' and signature in seen:continue
            if q=='Q3':seen.add(signature)
            sol=decode(rows)
            improved=retain(sol)
            if sol:
                if key(sol,o)<key(current,o):current=sol
                elif m=='alns':
                    delta=key(sol,o)[0]-key(current,o)[0]
                    temperature=(100. if o=='time' else 1.)*max(.01,1-(time.perf_counter()-began)/args.seconds)
                    if rng.random()<math.exp(-max(0,delta)/temperature):current=sol
                if m=='aco':
                    for rid in list(pheromone):pheromone[rid]=max(.05,pheromone[rid]*.9)
                    for row in best['transport']:
                        rid=row['route']['id'];pheromone[rid]=min(20,pheromone.get(rid,1.)+1.)
                if m=='alns':rewards[operator]+=8. if improved else 1.
            if m=='alns' and attempts%25==0:
                for j in range(3):weights[j]=.8*weights[j]+.2*(rewards[j]/max(1,uses[j])+.1)
                rewards=[0.,0.,0.];uses=[0,0,0]
    search_wall=time.perf_counter()-began
    record=dict(question=q,objective=o,method=m,seed=args.seed,budget_s=args.seconds,search_wall_s=search_wall,
        attempts=attempts,failed_constructions=failures,decoder_calls=decoder_calls,incumbent_callbacks=callback_count,
        initial_sha256=digest(initial_path),trace=trace,checkpoints=[],status='COMPLETED',
        algorithm_version='v2_repaired_greedy_shared_initial_callbacks',checkpoint_comparison='same uninterrupted search',
        objective_comparison_tolerance=dict(time_s=1e-6,energy_kwh=1e-9))
    verified={}
    for cp in checkpoints:
        name=f'checkpoint_{cp:g}s';path=base/f'{name}_solution.json'
        assert path.exists(),'Shared initial should guarantee a saved candidate'
        h=digest(path)
        if h in verified:
            metrics,audit=verified[h]
            dump(base/f'{name}_validation.json',audit)
        else:
            metrics,audit=validate_solution(q,path,base/f'{name}_validation.json');verified[h]=(metrics,audit)
        row=checkpoint_meta[str(cp)]
        record['checkpoints'].append(dict(row,status='VALIDATED_FEASIBLE',metrics=metrics,solution_sha256=h,
            validation_file=f'{name}_validation.json'))
    record['total_wall_s']=time.perf_counter()-began
    dump(base/'run.json',record)
    print('FINISH',q,o,m,record['checkpoints'],flush=True)
    return record


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['prepare','one'])
    parser.add_argument('--question',choices=['Q2','Q3'],default='Q2');parser.add_argument('--objective',choices=['time','energy'],default='time')
    parser.add_argument('--method',choices=['greedy','aco','alns','cp_sat'],default='greedy')
    parser.add_argument('--seconds',type=float,default=600);parser.add_argument('--checkpoints',default='180,600')
    parser.add_argument('--seed',type=int,default=42);parser.add_argument('--name',default='pilot')
    args=parser.parse_args()
    if args.action=='prepare':prepare_initial()
    else:run_one(args)
