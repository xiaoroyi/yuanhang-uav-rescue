"""Targeted verifier tests and final checks; no application service is modified."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from support import EVIDENCE, inputs, dump, PROJECT
from legacy_validate import check
from benchmark import station_audit
from legacy_routes import Physics

def negative_tests():
    rows=json.loads((EVIDENCE/'pilot_q2_greedy/best_solution.json').read_text(encoding='utf-8'))['transport']
    P=Physics()
    assert check(rows,data=inputs())['summary']['valid']
    tests=[]
    duplicate=copy.deepcopy(rows)+[copy.deepcopy(rows[0])]
    report=check(duplicate,data=inputs())
    assert not report['summary']['valid'] and any(e['code']=='coverage' for e in report['errors'])
    tests.append(dict(name='duplicate cargo and overlapping resources rejected',passed=True))
    energy=copy.deepcopy(rows)
    energy[0]['route']['energy']+=.1
    report=check(energy,data=inputs())
    assert not report['summary']['valid'] and any(e['code']=='energy_value' for e in report['errors'])
    tests.append(dict(name='reported energy recomputed independently',passed=True))
    changed=copy.deepcopy(rows)
    for r in changed:
        r['start']+=20000;r['return']+=20000;r['battery_ready']+=20000
    report=check(changed,data=inputs())
    assert not report['summary']['valid'] and any(e['code']=='hard_deadline' for e in report['errors'])
    assert station_audit(P,changed)['hard_violations']>0
    tests.append(dict(name='hard deadlines and station lateness rejected',passed=True))
    absent=copy.deepcopy(rows[1:])
    report=check(absent,data=inputs())
    assert not report['summary']['valid'] and any(e['code']=='coverage' for e in report['errors'])
    tests.append(dict(name='missing cargo rejected',passed=True))
    dump(EVIDENCE/'verifier_tests.json',tests)
    print('Verifier negative cases',len(tests),'passed')

def final_checks(name):
    base=EVIDENCE/name
    records=json.loads((base/'results.json').read_text(encoding='utf-8'))
    expected={(q,o,m) for q in ['Q2','Q3'] for o in ['time','energy'] for m in ['greedy','aco','alns','cp_sat']}
    assert {(r['question'],r['objective'],r['method']) for r in records}==expected
    P=Physics();checks=[]
    for r in records:
        folder=base/f"{r['question']}_{r['objective']}_{r['method']}"
        assert r['seed']==42 and r['budget_s']==180
        if r['metrics'] is None:
            checks.append(dict(run=folder.name,status=r['status'],metrics=None))
            continue
        sol=json.loads((folder/'best_solution.json').read_text(encoding='utf-8'))
        transport=check(sol['transport'],data=inputs())
        station=station_audit(P,sol['transport'])
        assert transport['summary']['valid']
        assert station['boxes']==station['unique_boxes']==80 and station['late_boxes']==station['hard_violations']==0
        C=max(v['return'] for v in sol['transport']+sol['relay'])
        E=sum(v['route']['energy'] for v in sol['transport'])+sum(v['energy'] for v in sol['relay'])
        assert abs(C-r['metrics']['completion_s'])<1e-7 and abs(E-r['metrics']['energy_kwh'])<1e-7
        assert r['metrics']['minimum_hard_slack_s']>=-1e-6
        if r['question']=='Q3':
            radio=r['validation']['radio']['summary']
            assert radio['valid'] and radio['gap_seconds']==radio['unknown_intervals']==radio['hard_violations']==0
            assert abs(C-radio['C_joint'])<1e-7 and abs(E-radio['E_total'])<1e-7
        checks.append(dict(run=folder.name,status='passed',completion_s=C,energy_kwh=E,
                           solution_sha256=hashlib.sha256((folder/'best_solution.json').read_bytes()).hexdigest()))
    dump(base/'final_checks.json',dict(expected_runs=16,actual_runs=len(records),all_checks_passed=True,runs=checks))
    print('Final experiment integrity',len(records),'runs verified')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--final',action='store_true');p.add_argument('--name',default='main_180s_seed42')
    a=p.parse_args()
    if a.final:final_checks(a.name)
    else:negative_tests()
