"""Cheap feasibility screening of the unchanged public pool under a short horizon."""
import argparse
import json
import time
import numpy as np
from scipy.optimize import linprog
from benchmark_v2 import load,V1
from support import PROJECT,dump
from legacy_routes import Physics
import master_v2

def main():
    p=argparse.ArgumentParser();p.add_argument('--cap',type=float,default=6000);p.add_argument('--seconds',type=float,default=30);a=p.parse_args()
    out=PROJECT/'evidence/contest-baselines-v3';out.mkdir(exist_ok=True,parents=True)
    P=Physics();pool=load(V1/'pool_q2.json');box=list(P.boxes);n=len(pool)
    cover=np.asarray([[int(b in r['boxes']) for r in pool]+[0] for b in box],float)
    work=np.asarray([[r['duration'] if r['model']==g else 0 for r in pool]+[-P.data['M'][g]] for g in P.models])
    objective=np.r_[np.zeros(n),1.]
    lp=linprog(objective,A_eq=cover,b_eq=np.ones(len(box)),A_ub=work,b_ub=np.zeros(len(work)),bounds=[(0,1)]*n+[(0,None)],method='highs')
    result=dict(cap_s=a.cap,pool_size=n,lp_status=int(lp.status),necessary_min_completion_lower_bound_s=float(lp.fun) if lp.success else None)
    began=time.perf_counter()
    cp=master_v2.solve(P,{r['id']:r for r in pool},seconds=a.seconds,seed=42,workers=1,objectives=('C',),fixed_D=0,
        max_C=a.cap,delivery_mode='batch',evidence_path=out/'probe_q2_cp.json',deadline_monotonic=began+a.seconds)
    result.update(cp_evidence=cp['evidence'],cp_selected=len(cp['selected'] or []),cp_wall_s=time.perf_counter()-began)
    if cp['selected']:
        rows=master_v2.decode(P,cp,retime=True)
        dump(out/'probe_q2_solution.json',dict(transport=rows,relay=[],resources=[2,6]))
    dump(out/'probe.json',result);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
