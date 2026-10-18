import bootstrap
import itertools
import math
from functools import lru_cache
from collections import Counter
from flight_physics import D, metrics
from data_io import CATEGORIES

def enumerate_patterns(data,geometries,eta_scale=1):
    patterns=[]; rejected=[]
    for s,counts in data['counts'].items():
        for a in itertools.product(*(range(n+1) for n in counts)):
            if not any(a): continue
            mass=sum(a[k]*data['attributes'][c][0] for k,c in enumerate(CATEGORIES))
            volume=sum(a[k]*data['attributes'][c][1] for k,c in enumerate(CATEGORIES))
            for g,m in data['models'].items():
                identity=dict(service=s,model=g,counts=a,mass_kg=mass,volume_L=volume,box_count=sum(a))
                if mass>m['Q'] or volume>m['volume_L']:
                    rejected.append(dict(identity,reason='mass' if mass>m['Q'] else 'volume'))
                    continue
                patterns.append(dict(identity,id=f'{s}-{g}-'+''.join(map(str,a)),**metrics(m,geometries[s],mass,sum(a),eta_scale)))
    return patterns,rejected

def local_dp(counts,patterns,order):
    @lru_cache(None)
    def solve(r):
        if not any(r): return ((D(0),D(0),D(0)),())
        best=None
        for p in patterns:
            if any(a>b for a,b in zip(p['counts'],r)): continue
            prev=solve(tuple(b-a for a,b in zip(p['counts'],r)))
            if prev is None: continue
            v=(prev[0][0]+1,prev[0][1]+p['E'],prev[0][2]+p['T'])
            key=tuple(v[i] for i in order)
            if best is None or key<tuple(best[0][i] for i in order):
                best=(v,prev[1]+(p,))
        return best
    return solve(tuple(counts))

def solve_all(data,patterns,rho=D('.2'),order=(0,1,2),only_model=None):
    chosen=[]
    for s in data['services']:
        feasible=[p for p in patterns if p['service']==s and p['SOC']>=D(rho) and (only_model is None or p['model']==only_model)]
        local=local_dp(data['counts'][s],feasible,order)
        if local is None: return None
        chosen.extend(local[1])
    return chosen

def summary(chosen):
    if chosen is None: return dict(feasible=False,N=None,E_kwh=None,T_s=None)
    return dict(feasible=True,N=len(chosen),E_kwh=float(sum((p['E'] for p in chosen),D(0))),T_s=float(sum((p['T'] for p in chosen),D(0))),A=sum(p['model']=='A' for p in chosen),B=sum(p['model']=='B' for p in chosen),C=sum(p['model']=='C' for p in chosen),min_SOC=float(min(p['SOC'] for p in chosen)))

def assign_boxes(data,chosen):
    queues={(s,c):sorted((b for b in data['boxes'] if b['service']==s and b['category']==c),key=lambda b:(not b['first'],b['id'])) for s in data['services'] for c in CATEGORIES}
    rows=[]
    for i,p in enumerate(chosen,1):
        ids=[]
        for c,n in zip(CATEGORIES,p['counts']):
            ids.extend(queues[p['service'],c].pop(0)['id'] for _ in range(n))
        row={k:float(v) if hasattr(v,'as_tuple') else v for k,v in p.items()}
        row.update(batch=f'Q1-{i:03d}',boxes=ids)
        rows.append(row)
    assert all(not q for q in queues.values())
    return rows

def baselines(data,patterns,rho=D('.2')):
    lookup={}
    for p in patterns:
        if p['SOC']>=rho:
            key=(p['service'],p['counts'])
            if key not in lookup or (p['E'],p['T'])<(lookup[key]['E'],lookup[key]['T']): lookup[key]=p
    single=[]; greedy=[]
    for s in data['services']:
        boxes=[b for b in data['boxes'] if b['service']==s]
        # Descending maximum normalized loading difficulty; deterministic IDs break ties.
        boxes.sort(key=lambda b:(-max(b['weight']/max(m['Q'] for m in data['models'].values()),b['volume_L']/max(m['volume_L'] for m in data['models'].values())),-b['weight'],-b['volume_L'],b['id']))
        bins=[]
        for b in boxes:
            a=tuple(int(c==b['category']) for c in CATEGORIES)
            single.append(lookup[(s,a)])
            candidates=[]
            for idx,old in enumerate(bins):
                new=tuple(x+y for x,y in zip(old['counts'],a))
                if (s,new) in lookup:
                    p=lookup[s,new]
                    candidates.append((p['E']-old['E'],p['T']-old['T'],idx,p))
            if candidates:
                _,_,idx,p=min(candidates,key=lambda x:x[:3]); bins[idx]=p
            else: bins.append(lookup[s,a])
        # Exhaust deterministic legal pair merging until no merge is possible.
        while True:
            options=[]
            for i,j in itertools.combinations(range(len(bins)),2):
                a=tuple(x+y for x,y in zip(bins[i]['counts'],bins[j]['counts']))
                if (s,a) in lookup:
                    p=lookup[s,a]; options.append((p['E']-bins[i]['E']-bins[j]['E'],i,j,p))
            if not options: break
            _,i,j,p=min(options,key=lambda x:x[:3]); bins[i]=p; bins.pop(j)
        greedy.extend(bins)
    return single,greedy

def bitmask_check(data,geometries,rho=D('.2')):
    """Box identity subset DP; no count-pattern library is read."""
    results=[]
    for s in data['services']:
        boxes=[b for b in data['boxes'] if b['service']==s]
        if len(boxes)>8: continue
        subsets={}
        for mask in range(1,1<<len(boxes)):
            bs=[b for j,b in enumerate(boxes) if mask>>j&1]
            w=sum(b['weight'] for b in bs); v=sum(b['volume_L'] for b in bs)
            options=[]
            for m in data['models'].values():
                if w<=m['Q'] and v<=m['volume_L']:
                    z=metrics(m,geometries[s],w,len(bs))
                    if z['SOC']>=rho: options.append((D(1),z['E'],z['T']))
            if options: subsets[mask]=min(options)
        @lru_cache(None)
        def dp(mask):
            if mask==0: return (D(0),D(0),D(0))
            best=None; sub=mask; first=mask&-mask
            while sub:
                if sub&first and sub in subsets:
                    prev=dp(mask^sub)
                    if prev is not None:
                        v=tuple(a+b for a,b in zip(prev,subsets[sub]))
                        if best is None or v<best: best=v
                sub=(sub-1)&mask
            return best
        value=dp((1<<len(boxes))-1)
        results.append(dict(service=s,N=int(value[0]),E_kwh=float(value[1]),T_s=float(value[2])))
    return results
