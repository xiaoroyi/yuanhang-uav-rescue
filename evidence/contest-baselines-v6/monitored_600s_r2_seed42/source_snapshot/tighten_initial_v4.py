"""Remove unused relay hovering without changing any transportation schedule."""
import copy
import math
import time
from pattern_v4 import V4
from benchmark_v2 import load,validate_solution,solution_metrics
from support import dump
from legacy_routes import charge,Physics
import joint_v4

def main():
    begin=time.perf_counter();wide=V4/'preparation/common_q3_wide_windows.json';original=load(wide if wide.exists() else V4/'common_q3.json');atoms=load(V4/'atoms.json');sol=copy.deepcopy(original)
    assigned=[[] for r in sol['relay']]
    for row in sol['transport']:
        for atom in atoms[row['route']['id']]:
            a=row['start']+atom['a'];b=row['start']+atom['b']
            options=[i for i,r in enumerate(sol['relay']) if r['site']['id'] in atom['sites'] and r['link_complete']<=a+1e-7 and r['service_end']>=b-1e-7]
            assert options,'Initial atom has no complete single-relay witness'
            k=min(options,key=lambda i:sol['relay'][i]['service_end']);assigned[k].append((a,b))
    out=[]
    for r,iv in zip(sol['relay'],assigned):
        if not iv:continue
        site=r['site'];st=max(r['start'],(math.floor(min(a for a,b in iv)*10+1e-7)-math.ceil(site['ready_offset']*10-1e-7))/10)
        finish=min(r['service_end'],math.ceil(max(b for a,b in iv)*10-1e-7)/10)
        e=site['fly_energy']+1.1*(finish-st-site['arrival_offset'])/3600;ch=charge(1-e/3.2,1800)
        updated=dict(r,start=st,arrival=st+site['arrival_offset'],link_complete=st+site['ready_offset'],service_end=finish,
            energy=e,SOC=1-e/3.2,charge=ch,component_ready=finish+site['back']+ch,aircraft_ready=finish+site['back']+300)
        updated['return']=finish+site['back'];out.append(updated)
        assert updated['start']>=r['start'] and updated['return']<=r['return']+1e-7 and updated['component_ready']<=r['component_ready']+1e-7
    out.sort(key=lambda r:(r['start'],r['slot']))
    for i,r in enumerate(out):r['slot']=i
    sol['relay']=out;joint_v4.color(sol,Physics())
    if not wide.exists():dump(wide,original)
    dump(V4/'common_q3.json',sol);metrics,_=validate_solution('Q3',V4/'common_q3.json',V4/'common_q3_validation.json')
    assert metrics['completion_s']<=5939.9+1e-6
    dump(V4/'preparation/tightening.json',dict(before=solution_metrics(original),after=metrics,wall_s=time.perf_counter()-begin,
        rule='Assign each public coverage atom to an existing complete witness; only shrink occupied intervals; independently revalidate continuous communication.'))
    print('INITIAL TIGHTENED',metrics,flush=True)

if __name__=='__main__':main()
