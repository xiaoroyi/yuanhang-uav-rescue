"""Independently generated bounded baseline pool; no paper routes or starts loaded.

Run prepare first, then run. Source helpers reproduce the paper's physical model.
Q3 constructive/metaheuristic route choices share a CP scheduling decoder. Thus
their reported names explicitly include +CP; they are problem adaptations.
"""
import argparse
from collections import Counter, defaultdict
import copy
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import platform
import random
import sys
import time

from support import EVIDENCE, OUT, CACHE, PROJECT, FORWARD, INVERSE, inputs, dump, table
from legacy_routes import Physics
import legacy_master
import legacy_joint
from legacy_radio import Radio
from legacy_sites import relay_metrics
from legacy_atoms import build_route
from legacy_validate import check
from legacy_validate_q3 import run as check_q3


def due(P, b):
    x = P.boxes[b]
    return min(x['expected_s'], x['hard_due'] or math.inf)


def route_latest(P, r):
    m = P.models[r['model']]
    return min(due(P,b)-r['arrivals'][i]-m['handover']-m['handover_box']*len(bs)
               for i, (_,bs) in enumerate(r['stops']) for b in bs)


def prepare():
    began = time.perf_counter()
    CACHE.mkdir(exist_ok=True, parents=True)
    P = Physics()
    pool = {}
    def add(g, stops):
        r = P.evaluate(g, stops)
        if r and route_latest(P, r)>=0:
            pool[r['id']] = r
    by = defaultdict(list)
    for b,x in P.boxes.items():
        by[x['service']].append(b)
        for g in P.models:
            add(g, [(x['service'],[b])])
    rng = random.Random(20261019)
    # Several independent first-fit decreasing/EDF partitions, not Q1 or paper batches.
    for site, ids in sorted(by.items()):
        for g,m in P.models.items():
            orders = [sorted(ids, key=lambda b:(due(P,b), b)),
                      sorted(ids, key=lambda b:(-P.boxes[b]['weight'], b)),
                      sorted(ids, key=lambda b:(-P.boxes[b]['volume_L'], b))]
            for order in orders:
                remaining = list(order)
                while remaining:
                    batch=[]
                    for b in remaining:
                        if P.evaluate(g, [(site,batch+[b])]) is not None:
                            batch.append(b)
                    if not batch:
                        break
                    add(g, [(site,batch)])
                    remaining=[b for b in remaining if b not in batch]
    base_count = len(pool)
    # Geometric nearest-neighbour visits, random cargo subsets, independent seed.
    nodes=sorted(by)
    for trial in range(2600):
        g=rng.choice(sorted(P.models))
        a=rng.choice(nodes)
        near=sorted([s for s in nodes if s!=a], key=lambda s:P.geo[a,s][0])[:5]
        order=[a]+rng.sample(near, rng.choice([0,1,1,2]))
        stops=[]
        for s in order:
            ids=list(by[s]);rng.shuffle(ids)
            if rng.random()<.5:
                ids.sort(key=lambda b: due(P,b))
            batch=[]
            for b in ids:
                if rng.random()<.15:
                    continue
                candidate=stops+[(s,batch+[b])]
                if P.evaluate(g,candidate) is not None:
                    batch.append(b)
            if batch:
                stops.append((s,batch))
        if stops:
            add(g,stops)
        if len(pool)>=850:
            break
    routes=list(pool.values())
    dump(EVIDENCE/'pool_q2.json',routes)
    print('POOL',len(routes),'base',base_count,flush=True)
    data=inputs(); radio=Radio(data)
    xy=[n['xy'] for n in data['nodes'].values()]
    xs=[p[0] for p in xy];ys=[p[1] for p in xy]
    points=[(n['lon'],n['lat']) for n in data['nodes'].values()]
    # 4 km tiles: the highest DEM cell in each tile. No historical relay sites.
    for x in range(math.floor(min(xs)/4000)*4000, math.ceil(max(xs)/4000)*4000, 4000):
        for y in range(math.floor(min(ys)/4000)*4000, math.ceil(max(ys)/4000)*4000, 4000):
            lo,lt=INVERSE.transform([x,x+4000],[y,y+4000])
            cc=[max(0,min(len(data['lon'])-1,int((v-data['lon'][0])/(data['lon'][1]-data['lon'][0])+.5))) for v in lo]
            rr=[max(0,min(len(data['lat'])-1,int((data['lat'][0]-v)/(data['lat'][0]-data['lat'][1])+.5))) for v in lt]
            r0,r1=min(rr),max(rr)+1;c0,c1=min(cc),max(cc)+1
            import numpy as np
            ir,ic=np.unravel_index(np.argmax(data['dem'][r0:r1,c0:c1]),(r1-r0,c1-c0))
            points.append((float(data['lon'][c0+ic]),float(data['lat'][r0+ir])))
    sites=[]
    for lon,lat in points:
        st=relay_metrics(data,lon,lat,300)
        if st and st['max_service']>0 and radio.point(data['gateway'],[st['x'],st['y'],st['z']],'backhaul')['valid']:
            st['id']=f'B{len(sites)+1:03}'
            sites.append(st)
    dump(EVIDENCE/'stations.json',sites)
    atoms={};q3=[]
    for i,r in enumerate(routes):
        aa,_=build_route(r,P,radio,sites,max_block=3600)
        if all(a['sites'] for a in aa):
            atoms[r['id']]=aa;q3.append(r)
        if i%50==0:
            print('RADIO',i,len(routes),'retained',len(q3),'seconds',round(time.perf_counter()-began,1),flush=True)
    dump(EVIDENCE/'pool_q3.json',q3)
    dump(EVIDENCE/'atoms.json',atoms)
    # Historical values only enter the reporting file, never a baseline input.
    import csv
    with (PROJECT/'references/modeling/release/accepted_metrics.csv').open(encoding='utf-8-sig') as f:
        historical=list(csv.DictReader(f))
    dump(EVIDENCE/'historical_reference.json',historical)
    manifest=dict(preprocessing_wall_s=time.perf_counter()-began, pool_q2=len(routes),pool_q3=len(q3),
                  stations=len(sites),atoms=sum(map(len,atoms.values())),preprocessing_seed=20261019,
                  max_stops=3,site_generation='nodes plus highest DEM cell in 4km tiles; AGL 300m',
                  no_historical_routes_or_times=True,python=sys.version,platform=platform.platform(),logical_cpu=os.cpu_count(),
                  sources={str(p.relative_to(PROJECT)):hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in [OUT/'normalized_inputs.json',OUT/'terrain_evidence_all.json',EVIDENCE/'pool_q2.json',EVIDENCE/'pool_q3.json',EVIDENCE/'stations.json',EVIDENCE/'atoms.json']})
    dump(EVIDENCE/'preparation.json',manifest)
    print('PREPARATION',manifest,flush=True)


class Constructor:
    def __init__(self,P,pool,objective):
        self.P=P;self.pool=pool;self.objective=objective
        self.by=defaultdict(list)
        self.latest={r['id']:route_latest(P,r) for r in pool}
        for r in pool:
            for b in r['boxes']:
                self.by[b].append(r)

    def build(self,rng,mode='greedy',pheromone=None,fixed=(),temperature=1.):
        P=self.P;remaining=set(P.boxes)
        ua={g:[0.]*P.data['M'][g] for g in P.models}
        ba={g:[0.]*P.data['K'][g] for g in P.models}
        rows=[]
        # Fixed route prefix is rescheduled; destroyed cargo is reinserted into pool routes.
        def append(r,start):
            g=r['model'];u=min(range(len(ua[g])),key=ua[g].__getitem__);b=min(range(len(ba[g])),key=ba[g].__getitem__)
            uid=sorted(k for k,v in P.data['aircraft'].items() if v==g)[u]
            row=dict(route=r,start=start,orders=[list(bs) for _,bs in r['stops']],
                     sortie=f'T-{len(rows)+1:03}',aircraft=uid,battery=f'{g}-BAT-{b+1:02}',
                     battery_ready=start+r['duration']+r['charge'])
            row['return']=start+r['duration'];rows.append(row)
            ua[g][u]=row['return'];ba[g][b]=row['battery_ready'];remaining.difference_update(r['boxes'])
        fixed_by_box={b:r for r in fixed for b in r['boxes']}
        reserved=set(fixed_by_box)
        while remaining:
            focus=min(remaining,key=lambda b:(due(P,b),-P.boxes[b]['priority'],b))
            options=[]
            forced=fixed_by_box.get(focus)
            for r in ([forced] if forced else self.by[focus]):
                if not set(r['boxes'])<=remaining:
                    continue
                if not forced and set(r['boxes']) & reserved:
                    continue
                g=r['model'];start=max(min(ua[g]),min(ba[g]))
                if start>self.latest[r['id']]+1e-7:
                    continue
                n=len(r['boxes'])
                score=((start+r['duration'])/n**.7 if self.objective=='time' else r['energy']/n**.8)
                options.append((score,start,r))
            if not options:
                return None
            options.sort(key=lambda v:(v[0],v[2]['id']))
            choices=options[:min(10,len(options))]
            if mode=='greedy':
                chosen=choices[0]
            elif mode=='aco':
                weights=[pheromone.get(v[2]['id'],1.)/(v[0]/choices[0][0])**3 for v in choices]
                chosen=rng.choices(choices,weights=weights)[0]
            else:
                chosen=rng.choices(choices,weights=[math.exp(-i/max(.2,temperature)) for i in range(len(choices))])[0]
            _,start,r=chosen;append(r,start);reserved.difference_update(r['boxes'])
        return rows


def score(sol,objective):
    C=max(r['return'] for r in sol['transport']+sol['relay'])
    E=sum(r['route']['energy'] for r in sol['transport'])+sum(r['energy'] for r in sol['relay'])
    return (C,E) if objective=='time' else (E,C)


def station_audit(P,rows):
    values=[]
    for row in rows:
        r=row['route'];m=P.models[r['model']]
        for i,(_,bs) in enumerate(r['stops']):
            t=row['start']+r['arrivals'][i]+m['handover']+m['handover_box']*len(bs)
            for b in bs:
                values.append(dict(box=b,complete=t,expected=P.boxes[b]['expected_s'],hard=P.boxes[b]['hard_due']))
    return dict(boxes=len(values),unique_boxes=len({v['box'] for v in values}),
                late_boxes=sum(v['complete']>v['expected']+1e-6 for v in values),
                hard_violations=sum(v['hard'] is not None and v['complete']>v['hard']+1e-6 for v in values),
                minimum_hard_slack_s=min(v['hard']-v['complete'] for v in values if v['hard'] is not None))


def run_one(question,objective,method,seconds,seed,output,common_time_hint=False):
    output.mkdir(exist_ok=False,parents=True)
    P=Physics();pool=json.loads((EVIDENCE/f'pool_{question.lower()}.json').read_text(encoding='utf-8'))
    sites=json.loads((EVIDENCE/'stations.json').read_text(encoding='utf-8'))
    atoms=json.loads((EVIDENCE/'atoms.json').read_text(encoding='utf-8'))
    ctor=Constructor(P,pool,objective);rng=random.Random(seed)
    began=time.perf_counter();deadline=began+seconds;best=None;first=None;trace=[];attempts=0
    decoder_calls=0;decoder_status=[];failed_constructions=0;anneal_accepted=0
    weights=[1.,1.,1.];rewards=[0.,0.,0.];used=[0,0,0]
    legacy_joint.OUT=output/'decoder'
    legacy_joint.OUT.mkdir()
    def decode(rows,budget,decode_objective=None):
        nonlocal decoder_calls
        if question=='Q2':
            return dict(transport=rows,relay=[],resources=[2,6])
        if time.perf_counter()>=deadline:
            return None
        decoder_calls+=1
        chosen=[r['route'] for r in rows]
        sol=legacy_joint.solve(name='latest',pool=chosen,atoms={r['id']:atoms[r['id']] for r in chosen},sites_override=sites,
                seconds=max(.05,budget),slots=4,objectives=('C',) if (decode_objective or objective)=='time' else ('E',),
                zero_late=True,workers=1,seed=seed+decoder_calls,deadline=time.monotonic()+max(.05,min(budget,deadline-time.perf_counter())))
        path=legacy_joint.OUT/'latest/solver_evidence.json'
        if path.exists():
            ev=json.loads(path.read_text(encoding='utf-8'));decoder_status.append(ev)
        return sol
    def retain(sol):
        nonlocal best,first
        if sol is None:
            return False
        audit=station_audit(P,sol['transport'])
        assert audit['boxes']==audit['unique_boxes']==80 and not audit['late_boxes'] and not audit['hard_violations'],audit
        if best is None or score(sol,objective)<score(best,objective):
            best=copy.deepcopy(sol)
            elapsed=time.perf_counter()-began
            if first is None:
                first=elapsed
            trace.append(dict(elapsed_s=elapsed,objective=list(score(sol,objective)),iteration=attempts))
            dump(output/'best_solution.json',best)
            print('BEST',question,objective,method,trace[-1],flush=True)
            return True
        return False
    if method=='cp_sat':
        if question=='Q2':
            # A neutral constructive hint is allowed; no paper incumbent is used.
            initial=ctor.build(rng)
            if initial is None and common_time_hint:
                initial=Constructor(P,pool,'time').build(random.Random(seed))
            if initial:
                retain(dict(transport=initial,relay=[],resources=[2,6]))
            res=legacy_master.solve(P,{r['id']:r for r in pool},seconds=max(.05,deadline-time.perf_counter()),seed=seed,
                    workers=1,objectives=('C',) if objective=='time' else ('E',),fixed_D=0,
                    delivery_mode='batch',warm=initial,evidence_path=output/'cp_evidence.json',deadline_monotonic=deadline)
            if res['selected']:
                retain(dict(transport=legacy_master.decode(P,res,retime=False),relay=[],resources=[2,6]))
            elif initial:
                retain(dict(transport=initial,relay=[],resources=[2,6],fallback='common_greedy_incumbent'))
        else:
            initial=ctor.build(rng)
            if initial is None and common_time_hint:
                initial=Constructor(P,pool,'time').build(random.Random(seed))
            if initial:
                retain(decode(initial,min(20.,deadline-time.perf_counter()),decode_objective='time' if common_time_hint else None))
            sol=legacy_joint.solve(name='full_pool',pool=pool,atoms=atoms,sites_override=sites,
                seconds=max(.05,deadline-time.perf_counter()),slots=4,objectives=('C',) if objective=='time' else ('E',),
                zero_late=True,workers=1,seed=seed,warm=best,deadline=time.monotonic()+max(.05,deadline-time.perf_counter()))
            retain(sol)
    else:
        pheromone={};current=None;seen=set()
        # Q3 greedily fixes cargo groups; CP then resolves continuous communication scheduling.
        while time.perf_counter()<deadline:
            attempts+=1
            operator=0
            if attempts==1:
                rows=ctor.build(rng)
            elif method=='alns' and current is not None:
                operator=rng.choices(range(3),weights=weights)[0];used[operator]+=1
                rr=[x['route'] for x in current['transport']]
                k=max(2,math.ceil(len(rr)*rng.uniform(.15,.4)))
                if operator==0:
                    remove=set(rng.sample(range(len(rr)),min(k,len(rr))))
                elif operator==1:
                    remove=set(sorted(range(len(rr)),key=lambda i:rr[i]['energy']/len(rr[i]['boxes']),reverse=True)[:k])
                else:
                    anchor=rng.choice(rr)['stops'][0][0]
                    remove=set(sorted(range(len(rr)),key=lambda i:0 if rr[i]['stops'][0][0]==anchor else P.geo[anchor,rr[i]['stops'][0][0]][0])[:k])
                fixed=[r for i,r in enumerate(rr) if i not in remove]
                rows=ctor.build(rng,mode='random',fixed=fixed,temperature=1.5)
            else:
                rows=ctor.build(rng,mode='aco' if method=='aco' else 'random',pheromone=pheromone,temperature=1.5)
            if rows is None:
                failed_constructions+=1
                if method=='greedy':
                    break
                continue
            signature=tuple(sorted(r['route']['id'] for r in rows))
            if question=='Q3' and signature in seen:
                if method=='greedy':break
                continue
            seen.add(signature)
            budget=min(deadline-time.perf_counter(),20. if attempts==1 else 12.)
            sol=decode(rows,budget)
            improved=retain(sol)
            if sol:
                if current is None or score(sol,objective)<score(current,objective):
                    current=sol
                elif method=='alns':
                    delta=score(sol,objective)[0]-score(current,objective)[0]
                    scale=(100. if objective=='time' else 1.)*max(.01,1-(time.perf_counter()-began)/seconds)
                    if rng.random()<math.exp(-max(0,delta)/scale):
                        current=sol;anneal_accepted+=1
                if method=='aco':
                    for rid in list(pheromone):
                        pheromone[rid]=max(.05,pheromone[rid]*.9)
                    for row in (best or sol)['transport']:
                        rid=row['route']['id'];pheromone[rid]=min(20,pheromone.get(rid,1.)+1.)
                if method=='alns':
                    rewards[operator]+=8. if improved else 1.
            if method=='alns' and attempts%25==0:
                for j in range(3):
                    weights[j]=.8*weights[j]+.2*(rewards[j]/max(1,used[j])+.1)
                rewards=[0.,0.,0.];used=[0,0,0]
            if method=='greedy':
                break
    search_wall=time.perf_counter()-began
    record=dict(question=question,objective=objective,method=method,seed=seed,budget_s=seconds,
                common_time_hint=common_time_hint,
                search_wall_s=search_wall,first_feasible_observed_s=first,attempts=attempts,
                decoder_calls=decoder_calls,decoder_evidence=decoder_status,failed_constructions=failed_constructions,
                alns_operator_weights=weights,alns_anneal_accepted=anneal_accepted,
                trace=trace,status='NO_VALIDATED_SOLUTION',metrics=None,validation=None)
    if best:
        audit=check(best['transport'],data=inputs())
        station=station_audit(P,best['transport'])
        if question=='Q3':
            radio_audit=check_q3(output/'best_solution.json',save=True)
        else:
            radio_audit=None
        assert audit['summary']['valid'],audit['errors']
        assert not station['late_boxes'] and not station['hard_violations'],station
        if radio_audit:
            assert radio_audit['summary']['valid'],radio_audit['errors']
        C,E=(score(best,'time'))
        record.update(status='VALIDATED_FEASIBLE',metrics=dict(completion_s=C,energy_kwh=E,
            transport_sorties=len(best['transport']),relay_sorties=len(best['relay']),
            **station),validation=dict(transport=audit,station=station,radio=radio_audit))
    record['total_wall_s']=time.perf_counter()-began
    dump(output/'run.json',record)
    print('FINISH',question,objective,method,record['status'],record['metrics'],flush=True)
    return record


def run(args):
    base=EVIDENCE/args.name;base.mkdir(exist_ok=False)
    dump(base/'protocol.json',dict(seconds=args.seconds,seeds=[args.seed],questions=['Q2','Q3'],
        objectives=['time','energy'],methods=['greedy','aco','alns','cp_sat'],
        workers=1,completion_cap=None,zero_station_lateness=True,
        q3_metaheuristics='route-group search with shared CP scheduling decoder; not pure ACO/ALNS',
        historical_reference='external historical results; unknown/nonmatched total search budget; never supplied as warm start'))
    records=[]
    for question in ['Q2','Q3']:
        for objective in ['time','energy']:
            for method in ['greedy','aco','alns','cp_sat']:
                row=run_one(question,objective,method,args.seconds,args.seed,base/f'{question}_{objective}_{method}')
                records.append(row);dump(base/'results.json',records)
    table(base/'results.csv',[{k:r[k] for k in ['question','objective','method','seed','status','budget_s','search_wall_s','total_wall_s']}| (r['metrics'] or {}) for r in records])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','run','one']);p.add_argument('--seconds',type=float,default=180)
    p.add_argument('--seed',type=int,default=42);p.add_argument('--name',default='main_180s_seed42')
    p.add_argument('--question',default='Q2');p.add_argument('--objective',default='time');p.add_argument('--method',default='greedy')
    p.add_argument('--common-time-hint',action='store_true')
    args=p.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='run':run(args)
    else:run_one(args.question,args.objective,args.method,args.seconds,args.seed,EVIDENCE/args.name,args.common_time_hint)
