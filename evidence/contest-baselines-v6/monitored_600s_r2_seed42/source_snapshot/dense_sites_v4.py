"""Generic 900m terrain site scout; retain prior sites and recompute coverage."""
import time
from pattern_v4 import V4
from benchmark_v2 import load
from support import dump
from legacy_routes import Physics
from legacy_radio import Radio
from legacy_atoms import build_route
from support import inputs
import legacy_sites

def main():
    beg=time.perf_counter();old=load(V4/'sites.json');legacy_sites.OUT=V4/'preparation/dense_site_scout';legacy_sites.OUT.mkdir(exist_ok=True,parents=True)
    legacy_sites.build(spacing=900);new=load(legacy_sites.OUT/'relay_sites.json');ss=old.copy();coords={(s['lon'],s['lat'],s['agl']) for s in ss}
    for s in new:
        if (s['lon'],s['lat'],s['agl']) in coords:continue
        s['id']=f'DENSE-{len(ss)+1:03}';ss.append(s)
    dump(V4/'preparation/coarse_sites.json',old);dump(V4/'sites.json',ss)
    P=Physics();radio=Radio(inputs());pool=load(V4/'pool_q2.json');atoms={};q3=[]
    for i,r in enumerate(pool):
        aa,_=build_route(r,P,radio,ss,max_block=120)
        if all(a['sites'] for a in aa):atoms[r['id']]=aa;q3.append(r)
        if i%50==0:print('DENSE ATOMS',i,len(pool),round(time.perf_counter()-beg,1),flush=True)
    dump(V4/'atoms.json',atoms);dump(V4/'pool_q3.json',q3);dump(V4/'preparation/dense_summary.json',dict(old_sites=len(old),sites=len(ss),q3_routes=len(q3),wall_s=time.perf_counter()-beg))

if __name__=='__main__':main()
