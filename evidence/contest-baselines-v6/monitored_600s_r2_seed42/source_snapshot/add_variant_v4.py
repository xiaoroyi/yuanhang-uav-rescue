"""Add independently prepared compact transportation candidates to the public pool."""
import time
from pattern_v4 import V4
from benchmark_v2 import load
from support import inputs,dump
from legacy_routes import Physics
from legacy_radio import Radio
from legacy_atoms import build_route

def main():
    began=time.perf_counter();P=Physics();ss=load(V4/'sites.json');atoms=load(V4/'atoms.json');pool={r['id']:r for r in load(V4/'pool_q2.json')}
    radio=Radio(inputs());new=load(V4/'transport_candidate_union_compact.json')
    for r in new:
        pool[r['id']]=r
        if r['id'] not in atoms:
            aa,_=build_route(r,P,radio,ss,max_block=120)
            if all(a['sites'] for a in aa):atoms[r['id']]=aa
    dump(V4/'pool_q2.json',list(pool.values()));dump(V4/'pool_q3.json',[r for r in pool.values() if r['id'] in atoms]);dump(V4/'atoms.json',atoms)
    dump(V4/'preparation/compact_addition.json',dict(wall_s=time.perf_counter()-began,added_route_inputs=len(new),total_routes=len(pool),sites=len(ss)))
    print('VARIANT ROUTES READY',len(pool),len(ss),flush=True)

if __name__=='__main__':main()
