"""Independent cargo-pattern feasibility preparation, not a paper-answer replay.

Cargo labels with equal site/mass/volume/effective zero-late deadline are
exchangeable only inside this common preprocessor. Materialization restores all
original IDs and independently validates them. All methods receive its outputs.
"""
import argparse
from collections import Counter,defaultdict
import itertools
import math
import random
import time
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from scipy.sparse import csc_matrix
from benchmark import due,route_latest,station_audit
from benchmark_v2 import load,digest,validate_solution,solution_metrics,V1
from legacy_routes import Physics
from support import PROJECT,dump
import master_v2

V4=PROJECT/'evidence/contest-baselines-v4'

def schedule(P,routes,cap,seconds=1.):
    """Bounded depth-first list scheduling with explicit aircraft/battery IDs."""
    until=time.perf_counter()+seconds;result=[]
    for g in P.models:
        jobs=[r for r in routes if r['model']==g];ids=sorted(k for k,v in P.data['aircraft'].items() if v==g)
        latest=[min(route_latest(P,r),cap-r['duration']) for r in jobs];memo=set()
        def visit(mask,ua,ba,rows):
            if not mask:return rows
            if time.perf_counter()>=until:return None
            key=(mask,tuple(sorted(round(t,5) for t in ua)),tuple(sorted(round(t,5) for t in ba)))
            if key in memo:return None
            memo.add(key);u=min(range(len(ua)),key=ua.__getitem__);b=min(range(len(ba)),key=ba.__getitem__);start=max(ua[u],ba[b])
            opts=[i for i in range(len(jobs)) if mask>>i&1]
            if any(start>latest[i]+1e-7 for i in opts):return None
            if sum(jobs[i]['duration'] for i in opts)>sum(max(0,cap-t) for t in ua)+1e-7:return None
            for i in sorted(opts,key=lambda i:(latest[i],-jobs[i]['duration'])):
                r=jobs[i];us=ua.copy();bs=ba.copy();ret=start+r['duration'];ready=ret+r['charge'];us[u]=ret;bs[b]=ready
                row=dict(route=r,start=start,orders=[list(x) for _,x in r['stops']],sortie='INIT',aircraft=ids[u],battery=f'{g}-BAT-{b+1:02}',battery_ready=ready)
                row['return']=ret
                found=visit(mask^(1<<i),us,bs,rows+[row])
                if found is not None:return found
            return None
        found=visit((1<<len(jobs))-1,[0.]*len(ids),[0.]*P.data['K'][g],[])
        if found is None:return None
        result.extend(found)
    for i,r in enumerate(sorted(result,key=lambda r:(r['start'],r['route']['id'])),1):r['sortie']=f'INIT-{i:03}'
    return result

def classes(P):
    groups=defaultdict(list)
    for b in sorted(P.boxes):
        x=P.boxes[b];groups[(x['service'],x['weight'],x['volume_L'],due(P,b))].append(b)
    groups=sorted(groups.items());members=[bs for key,bs in groups]
    index={b:i for i,bs in enumerate(members) for b in bs}
    return members,index

def signature(r,index):
    return (r['model'],tuple((s,tuple(sorted(Counter(index[b] for b in bs).items()))) for s,bs in r['stops']))

def materialize(P,routes,members,index):
    available=[list(bs) for bs in members];out=[]
    for r in routes:
        stops=[]
        for site,bs in r['stops']:
            restored=[]
            for b in bs:
                k=index[b];assert available[k];restored.append(available[k].pop(0))
            stops.append((site,restored))
        rr=P.evaluate(r['model'],stops);assert rr is not None
        assert abs(rr['energy']-r['energy'])<1e-9 and abs(rr['duration']-r['duration'])<1e-7
        out.append(rr)
    assert not any(available)
    return out

def generate():
    P=Physics();members,index=classes(P);by=defaultdict(list)
    for i,bs in enumerate(members):by[P.boxes[bs[0]]['service']].append(i)
    pool={}
    def emit(g,stops):
        r=P.evaluate(g,stops)
        if r and route_latest(P,r)>=0:pool[signature(r,index)]=r
    # Complete count patterns at each site: no random holes between equivalent IDs.
    for site,ks in by.items():
        for counts in itertools.product(*(range(len(members[k])+1) for k in ks)):
            bs=[b for k,n in zip(ks,counts) for b in members[k][:n]]
            if bs:
                for g in P.models:emit(g,[(site,bs)])
    single=list(pool.values());print('SINGLE PATTERNS',len(single),flush=True)
    # All pairs plus local triple single-box visits; no historical candidates used.
    for a,b in itertools.combinations(range(len(members)),2):
        sa=P.boxes[members[a][0]]['service'];sb=P.boxes[members[b][0]]['service']
        if sa==sb:continue
        for g in ['A','B','C']:
            emit(g,[(sa,members[a][:1]),(sb,members[b][:1])]);emit(g,[(sb,members[b][:1]),(sa,members[a][:1])])
    for a,b,c in itertools.combinations(range(len(members)),3):
        ks=[a,b,c];ss=[P.boxes[members[k][0]]['service'] for k in ks]
        if len(set(ss))!=3:continue
        # Only local triples, chosen geometrically rather than by the paper plan.
        if max(P.geo[x,y][0] for x,y in itertools.combinations(ss,2))>5000:continue
        for perm in itertools.permutations(ks):
            stops=[(P.boxes[members[k][0]]['service'],members[k][:1]) for k in perm]
            for g in ['A','B']:emit(g,stops)
    # Insert one box from a nearby other site into each feasible single-site batch.
    for r in single:
        site=r['stops'][0][0];near=sorted((s for s in by if s!=site),key=lambda s:P.geo[site,s][0])[:4]
        for s in near:
            for k in by[s]:
                extra=(s,members[k][:1]);emit(r['model'],r['stops']+[extra]);emit(r['model'],[extra]+r['stops'])
    routes=list(pool.values());dump(V4/'patterns.json',routes)
    dump(V4/'classes.json',dict(members=members,box_class=index,equivalence='site,mass,volume,min(expected,hard); valid only with D_station=0'))
    print('ALL PATTERNS',len(routes),flush=True)
    return routes,members,index

def prepare(seconds=180,route_penalty=0.,suffix=''):
    V4.mkdir(exist_ok=True,parents=True);beg=time.perf_counter();P=Physics()
    if (V4/'patterns.json').exists():
        pool=load(V4/'patterns.json');c=load(V4/'classes.json');members,index=c['members'],c['box_class']
    else:pool,members,index=generate()
    n=len(pool);groups=list(P.models);counts=np.array([len(bs) for bs in members],float)
    cover=np.zeros((len(members),n))
    for i,r in enumerate(pool):
        for b in r['boxes']:cover[index[b],i]+=1
    work=np.array([[r['duration']/P.data['M'][g] if r['model']==g else 0 for r in pool] for g in groups])
    # Minimize a balanced necessary makespan proxy, then schedule exact resources.
    A=np.block([[cover,np.zeros((len(members),1))],[work,-np.ones((len(groups),1))]])
    lo=np.r_[counts,[-np.inf]*len(groups)];hi=np.r_[counts,np.zeros(len(groups))]
    # Each job must start by L. At least min(p,max(0,T-L)) of its
    # aircraft/battery occupation lies before T in EVERY feasible schedule.
    latest=[min(route_latest(P,r),5939.9-r['duration']) for r in pool]
    for g in groups:
        for T in [1800,2400,3000,3600,4200,4800,5400,5939.9]:
            for field,stock in [('duration',P.data['M'][g]),('battery',P.data['K'][g])]:
                coef=[min(r['duration']+(r['charge'] if field=='battery' else 0),max(0,T-latest[i])) if r['model']==g else 0 for i,r in enumerate(pool)]
                A=np.vstack([A,np.r_[coef,0]]);lo=np.r_[lo,-np.inf];hi=np.r_[hi,T*stock]
    constraints=LinearConstraint(csc_matrix(A),lo,hi)
    upper=np.array([min(int(counts[k]//cover[k,i]) for k in np.flatnonzero(cover[:,i])) for i in range(n)]+[5939.9])
    rng=np.random.default_rng(42);records=[];best=None;all_selected={};attempt=0
    while time.perf_counter()-beg<seconds:
        attempt+=1
        obj=np.r_[np.array([r['energy'] for r in pool])*(.4+rng.random(n)*.3)+route_penalty,1.]
        res=milp(obj,integrality=np.r_[np.ones(n),0],bounds=Bounds(np.zeros(n+1),upper),constraints=constraints,
            options={'time_limit':min(8,seconds-(time.perf_counter()-beg)),'mip_rel_gap':.015})
        if res.x is None:records.append(dict(attempt=attempt,mip_status=int(res.status),selected=0));continue
        rr=[r for i,r in enumerate(pool) for _ in range(round(res.x[i]))]
        chosen=materialize(P,rr,members,index)
        for r in chosen:all_selected[r['id']]=r
        left=seconds-(time.perf_counter()-beg)
        if left<.2:break
        out=V4/'preparation'/f'energetic{suffix}_{attempt:03}';out.mkdir(exist_ok=True,parents=True)
        dump(out/'chosen.json',chosen)
        direct=schedule(P,chosen,5939.9,seconds=min(2,left))
        if direct is not None:
            result=dict(selected=[],evidence=[dict(status='CONSTRUCTED',wall_time=0)])
            rows=direct
        else:
            result=master_v2.solve(P,{r['id']:r for r in chosen},seconds=min(8,left),workers=4,seed=42+attempt,
            objectives=('C',),fixed_D=0,max_C=5939.9,delivery_mode='batch',evidence_path=out/'cp.json',deadline_monotonic=time.perf_counter()+min(10,left))
        rec=dict(attempt=attempt,mip_status=int(res.status),selected=len(chosen),proxy_completion_s=float(res.x[-1]),cp=result['evidence'])
        records.append(rec);print('PREP',rec,flush=True)
        dump(V4/f'preparation/transport_search{suffix}.json',dict(attempts=records,wall_s=time.perf_counter()-beg,no_paper_results_used=True,feasible=best is not None,route_penalty=route_penalty))
        if direct is not None or result['selected']:
            if direct is None:rows=master_v2.decode(P,result,retime=False)
            sol=dict(transport=rows,relay=[],resources=[2,6]);metric=solution_metrics(sol)
            if best is None or metric['completion_s']<solution_metrics(best)['completion_s']:
                best=sol;dump(V4/f'common_q2{suffix}.json',sol)
                validate_solution('Q2',V4/f'common_q2{suffix}.json',V4/f'common_q2{suffix}_validation.json')
                print('FEASIBLE COMMON TRANSPORT',metric,flush=True)
            break
    dump(V4/f'preparation/transport_search{suffix}.json',dict(attempts=records,wall_s=time.perf_counter()-beg,
        no_paper_results_used=True,feasible=best is not None,route_penalty=route_penalty))
    dump(V4/f'transport_candidate_union{suffix}.json',list(all_selected.values()))
    if best is None:raise RuntimeError('No independent cap-feasible transportation initial; do not run formal matrix.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=180);p.add_argument('--route-penalty',type=float,default=0);p.add_argument('--suffix',default='');a=p.parse_args();prepare(a.seconds,a.route_penalty,a.suffix)
