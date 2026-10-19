"""Check saved checkpoint evidence and immutable search sources, without rerunning search."""
import csv
import math
from pathlib import Path
from benchmark_v2 import V2,V1,load,digest,key,solution_metrics
from support import PROJECT,dump

BASE=V2/'main_600s_seed42'

def main():
    protocol=load(BASE/'protocol.json');completion=load(BASE/'completion.json')
    assert completion['complete'] and completion['completed_runs']==16
    records=load(BASE/'results.json')
    expected={(q,o,m) for q in ['Q2','Q3'] for o in ['time','energy'] for m in ['greedy','aco','alns','cp_sat']}
    assert {(r['question'],r['objective'],r['method']) for r in records}==expected
    for name,h in protocol['source_sha256'].items():
        assert digest(BASE/'source_snapshot'/name)==h
        assert digest(Path(__file__).with_name(name))==h,('search source changed',name)
    for name,h in protocol['frozen_candidate_files'].items():assert digest(V1/name)==h
    for source in load(V2/'solver_sources.json'):
        assert digest(PROJECT/source['source'])==source['source_sha256']
        assert digest(PROJECT/source['destination'])==source['destination_sha256']
    initial=protocol['common_initial_manifest']
    assert initial['no_paper_results_used'] and initial['excluded_from_per_method_search_budget']
    checks=[]
    for r in records:
        label=f"{r['question']}_{r['objective']}_{r['method']}";folder=BASE/label
        assert load(folder/'run.json')==r
        assert r['budget_s']==600 and r['seed']==42 and r['status']=='COMPLETED'
        assert r['search_wall_s']>=599.5 or r['method']=='cp_sat'
        assert r['initial_sha256']==digest(V2/'common_initial'/f"{r['question']}_{r['objective']}.json")
        assert [c['checkpoint_s'] for c in r['checkpoints']]==[180.,600.]
        solutions=[]
        for cp in r['checkpoints']:
            stem=f"checkpoint_{cp['checkpoint_s']:g}s";path=folder/f'{stem}_solution.json'
            sol=load(path);audit=load(folder/cp['validation_file']);m=cp['metrics']
            assert cp['status']=='VALIDATED_FEASIBLE' and audit['status']=='passed'
            assert digest(path)==cp['solution_sha256']==audit['solution_sha256']
            for field,value in solution_metrics(sol).items():assert math.isclose(m[field],value,rel_tol=0,abs_tol=1e-8)
            assert m['boxes']==m['unique_boxes']==80
            assert m['late_boxes']==m['hard_violations']==0 and m['minimum_hard_slack_s']>=-1e-6
            assert audit['transport']['summary']['valid'] and audit['station']['late_boxes']==0
            if r['question']=='Q3':
                radio=audit['radio']['summary']
                assert radio['valid'] and radio['gap_seconds']==radio['unknown_intervals']==radio['hard_violations']==0
                assert abs(radio['C_joint']-m['completion_s'])<1e-7
                assert abs(radio['E_total']-m['energy_kwh'])<1e-7
            eligible=[t for t in r['trace'] if t['found_s']<=cp['checkpoint_s']]
            assert eligible and abs(eligible[-1]['found_s']-cp['best_found_s'])<1e-8
            assert abs(eligible[-1]['completion_s']-m['completion_s'])<1e-8
            assert abs(eligible[-1]['energy_kwh']-m['energy_kwh'])<1e-8
            solutions.append(sol)
        assert key(solutions[1],r['objective'])<=key(solutions[0],r['objective'])
        for field in ['completion_s','energy_kwh']:
            assert abs(solution_metrics(load(folder/'best_solution.json'))[field]-r['checkpoints'][-1]['metrics'][field])<1e-8
        checks.append(dict(run=label,checkpoints_passed=2,initial_shared=True,
            objective_nonworsening=True,changed_after_180s=digest(folder/'checkpoint_180s_solution.json')!=digest(folder/'checkpoint_600s_solution.json'),
            final_is_initial=cp['solution_sha256']==r['initial_sha256']))
    rows=list(csv.DictReader((BASE/'results.csv').open(encoding='utf-8-sig')))
    assert len(rows)==32
    for row in rows:
        r=next(x for x in records if all(x[k]==row[k] for k in ['question','objective','method']))
        c=next(x for x in r['checkpoints'] if x['checkpoint_s']==float(row['checkpoint_s']))
        for k in ['completion_s','energy_kwh']:assert abs(float(row[k])-c['metrics'][k])<1e-8
    result=dict(all_checks_passed=True,configurations=16,validated_checkpoints=32,source_fingerprints_passed=True,
        candidate_fingerprints_passed=True,shared_initials_passed=True,checkpoint_timestamps_passed=True,
        objective_nonworsening_passed=True,independent_validation_files_passed=True,runs=checks)
    dump(BASE/'final_checks.json',result)
    print('16 configurations / 32 checkpoints / saved physical-radio audits / immutable fingerprints: passed')

if __name__=='__main__':main()
