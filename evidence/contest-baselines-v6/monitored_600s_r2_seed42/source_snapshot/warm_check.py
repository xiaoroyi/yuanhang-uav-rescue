"""Supplement two cold-start CP energy failures; same 180 s, neutral time hint."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from support import EVIDENCE, PROJECT, dump

def main():
    base=EVIDENCE/'cp_energy_warm_180s'
    base.mkdir(exist_ok=False)
    start=time.perf_counter()
    dump(base/'protocol.json',dict(reason='Both cold-start CP energy runs were UNKNOWN; add a neutral greedy time-feasible incumbent, not paper results',
        budget_per_run_s=180,seed=42,workers=1,concurrent_processes=2,
        source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}))
    def invoke(q):
        args=[sys.executable,'-u',str(Path(__file__).with_name('benchmark.py')),'one','--question',q,
              '--objective','energy','--method','cp_sat','--seconds','180','--seed','42',
              '--name',f'cp_energy_warm_180s/{q}_energy_cp_sat','--common-time-hint']
        with (base/f'{q}.txt').open('w',encoding='utf-8') as f:
            subprocess.run(args,cwd=PROJECT,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=360,
                env={**os.environ,'PYTHONIOENCODING':'utf-8','OMP_NUM_THREADS':'1','OPENBLAS_NUM_THREADS':'1','MKL_NUM_THREADS':'1'})
        return json.loads((base/f'{q}_energy_cp_sat/run.json').read_text(encoding='utf-8'))
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(invoke,['Q2','Q3']))
    dump(base/'results.json',results)
    dump(base/'completion.json',dict(complete=True,wall_s=time.perf_counter()-start,sum_search_wall_s=sum(r['search_wall_s'] for r in results)))
    print([(r['question'],r['status'],r['metrics']) for r in results])

if __name__=='__main__':main()
