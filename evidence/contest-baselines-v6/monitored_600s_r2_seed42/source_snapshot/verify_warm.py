"""Recheck the supplementary solutions without any new optimization."""
import hashlib
import json
from pathlib import Path
from support import EVIDENCE, inputs, dump
from legacy_validate import check
from legacy_routes import Physics
from benchmark import station_audit

def main():
    base=EVIDENCE/'cp_energy_warm_180s'
    results=json.loads((base/'results.json').read_text(encoding='utf-8'))
    assert {r['question'] for r in results}=={'Q2','Q3'}
    evidence=[]
    for r in results:
        assert r['common_time_hint'] and r['budget_s']==180 and r['seed']==42
        assert r['metrics'] and r['status']=='VALIDATED_FEASIBLE'
        p=base/f"{r['question']}_energy_cp_sat/best_solution.json"
        sol=json.loads(p.read_text(encoding='utf-8'))
        assert check(sol['transport'],data=inputs())['summary']['valid']
        station=station_audit(Physics(),sol['transport'])
        assert station['boxes']==station['unique_boxes']==80 and not station['hard_violations'] and not station['late_boxes']
        C=max(x['return'] for x in sol['transport']+sol['relay'])
        E=sum(x['route']['energy'] for x in sol['transport'])+sum(x['energy'] for x in sol['relay'])
        assert abs(C-r['metrics']['completion_s'])<1e-7 and abs(E-r['metrics']['energy_kwh'])<1e-7
        if r['question']=='Q3':
            a=r['validation']['radio']['summary']
            assert a['valid'] and a['gap_seconds']==a['unknown_intervals']==0
        evidence.append(dict(question=r['question'],status='passed',solution_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    dump(base/'final_checks.json',dict(all_checks_passed=True,runs=evidence))
    print('Supplement integrity: 2 runs passed')

if __name__=='__main__':main()
