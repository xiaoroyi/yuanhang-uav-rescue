"""Independent radio candidates and a validated common Q3 feasible initial."""
import argparse
import copy
import itertools
import math
import time
import numpy as np
from pattern_v4 import V4
from benchmark_v2 import load,validate_solution,solution_metrics,digest
from support import PROJECT,inputs,dump,FORWARD,INVERSE
from legacy_routes import Physics
from legacy_radio import Radio
from legacy_sites import relay_metrics
from legacy_atoms import build_route
import joint_v4

def sites():
    d=inputs();radio=Radio(d);xy=np.array([n['xy'] for n in d['nodes'].values()]);lo=xy.min(axis=0)-500;hi=xy.max(axis=0)+500
    points=[tuple(n['xy']) for n in d['nodes'].values()];spacing=2000
    for x in np.arange(lo[0],hi[0],spacing):
        for y in np.arange(lo[1],hi[1],spacing):
            points.append((x+spacing/2,y+spacing/2))
            ll,tt=INVERSE.transform([x,x+spacing],[y,y+spacing]);cols=np.clip(((np.array(ll)-d['lon'][0])/radio.dx+.5).astype(int),0,d['dem'].shape[1]-1);rs=np.clip(((d['lat'][0]-np.array(tt))/radio.dy+.5).astype(int),0,d['dem'].shape[0]-1)
            r0,r1=min(rs),max(rs)+1;c0,c1=min(cols),max(cols)+1
            rr,cc=np.unravel_index(np.argmax(d['dem'][r0:r1,c0:c1]),(r1-r0,c1-c0));points.append(tuple(FORWARD.transform(d['lon'][c0+cc],d['lat'][r0+rr])))
    targets={s:np.array(n['xy']+[n['z']+30]) for s,n in d['nodes'].items() if s!='O01'};accepted=[]
    for i,(x,y) in enumerate(dict.fromkeys(points)):
        lon,lat=INVERSE.transform(x,y);r0=int(round((d['lat'][0]-lat)/radio.dy));c0=int(round((lon-d['lon'][0])/radio.dx))
        if not (0<=r0<d['dem'].shape[0] and 0<=c0<d['dem'].shape[1]):continue
        for agl in [150,300]:
            p=[x,y,float(d['dem'][r0,c0])+agl]
            if not radio.point(d['gateway'],p,'backhaul')['valid']:continue
            cover=[s for s,t in targets.items() if radio.point(p,t,'access')['valid']]
            if cover:accepted.append(dict(lon=lon,lat=lat,agl=agl,cover=cover,dist=math.hypot(x-d['gateway'][0],y-d['gateway'][1])))
    accepted.sort(key=lambda s:(-len(s['cover']),s['dist'],s['agl']));chosen=[];patterns={}
    for s in accepted:
        key=tuple(s['cover']);patterns[key]=patterns.get(key,0)+1
        if patterns[key]<=2:chosen.append(s)
    for name in targets:chosen.extend([s for s in accepted if name in s['cover']][:3])
    chosen.extend(accepted[:12]);unique={(s['lon'],s['lat'],s['agl']):s for s in chosen};out=[]
    for s in unique.values():
        m=relay_metrics(d,s['lon'],s['lat'],s['agl'])
        if m and m['max_service']>0:m.update(id=f'V4-{len(out)+1:03}',cover=s['cover']);out.append(m)
    dump(V4/'sites.json',out);dump(V4/'preparation/site_generation.json',dict(grid_m=spacing,agl=[150,300],points=len(points),accepted=len(accepted),selected=len(out),no_historical_sites_used=True))
    print('SITES',len(out),flush=True);return out

def main(seconds):
    beg=time.perf_counter();P=Physics();ss=load(V4/'sites.json') if (V4/'sites.json').exists() else sites()
    sol=load(V4/'common_q2.json');chosen=[r['route'] for r in sol['transport']]
    pool={r['id']:r for r in load(V4/'transport_candidate_union.json')}
    pool.update({r['id']:r for r in chosen})
    # Concrete box label closure: all same-model swaps/relocations between the
    # independently constructed routes, keeping both complements in the pool.
    for r,t in itertools.combinations(chosen,2):
        for b in r['boxes']:
            left=[(s,[x for x in bs if x!=b]) for s,bs in r['stops']];dest=P.boxes[b]['service']
            right=[(s,list(bs)+([b] if s==dest else [])) for s,bs in t['stops']]
            if dest not in [s for s,_ in t['stops']]:right.append((dest,[b]))
            for g in [r['model'],t['model']]:
                for stops in [left,right]:
                    rr=P.evaluate(g,stops)
                    if rr and min(P.boxes[b]['expected_s']-rr['arrivals'][j]-P.models[g]['handover']-P.models[g]['handover_box']*len(bs) for j,(_,bs) in enumerate(rr['stops']) for b in bs)>=0:pool[rr['id']]=rr
    # Keep a moderate public concrete pool for full joint CP. All independently
    # built common-route columns and MILP candidates survive this deterministic cap.
    required={r['id'] for r in chosen}|{r['id'] for r in load(V4/'transport_candidate_union.json')}
    extras=sorted((r for r in pool.values() if r['id'] not in required),key=lambda r:(r['energy']/len(r['boxes'])**.8,r['duration'],r['id']))[:600]
    pool={r['id']:r for r in list(pool.values()) if r['id'] in required};pool.update({r['id']:r for r in extras})
    dump(V4/'pool_q2.json',list(pool.values()));radio=Radio(inputs());atoms={};q3=[]
    atom_path=V4/'atoms.json';old=load(atom_path) if atom_path.exists() else {}
    for i,r in enumerate(pool.values()):
        aa=old.get(r['id'])
        if aa is None:aa,_=build_route(r,P,radio,ss,max_block=120)
        if all(a['sites'] for a in aa):atoms[r['id']]=aa;q3.append(r)
        if i%50==0:print('ATOMS',i,len(pool),round(time.perf_counter()-beg,1),flush=True);dump(atom_path,atoms)
    dump(atom_path,atoms);dump(V4/'pool_q3.json',q3)
    assert all(r['id'] in atoms for r in chosen)
    joint_v4.OUT=V4/'preparation/joint';observed=[]
    def observe(s,info):
        observed.append(dict(**info,**solution_metrics(s)))
        dump(V4/'common_q3.json',s)
    initial_seconds=min(40,seconds)
    found=joint_v4.solve(name='fixed_independent_transport',fixed=True,fixed_transport=sol['transport'],pool=chosen,
        atoms=atoms,sites_override=ss,slots=6,seconds=initial_seconds,objectives=('E',),max_C=5939.9,zero_late=True,workers=4,
        stop_on_first=True,deadline=time.monotonic()+initial_seconds,incumbent_callback=observe)
    if found is None:
        left=seconds-(time.perf_counter()-beg)
        if left>1:
            found=joint_v4.solve(name='reschedule_independent_groups',pool=chosen,atoms=atoms,sites_override=ss,
                slots=6,seconds=left,objectives=('C',),max_C=5939.9,zero_late=True,workers=4,stop_on_first=True,
                warm=dict(transport=sol['transport'],relay=[]),deadline=time.monotonic()+left,incumbent_callback=observe)
    assert found is not None,'Q3 feasibility gate failed; do not run matrix'
    dump(V4/'common_q3.json',found);metrics,_=validate_solution('Q3',V4/'common_q3.json',V4/'common_q3_validation.json')
    assert metrics['completion_s']<=5939.9+1e-6
    dump(V4/'preparation/joint_summary.json',dict(wall_s=time.perf_counter()-beg,metrics=metrics,observed=observed,
        no_paper_results_used=True,slots=6,scope='6 computational relay slots, separate from 2 aircraft and 6 component stock. No energy or transport count target caps.'))
    print('COMMON Q3 VALIDATED',metrics,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=240);a=p.parse_args();main(a.seconds)
