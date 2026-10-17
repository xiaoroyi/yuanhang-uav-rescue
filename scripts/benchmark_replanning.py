"""Same-budget repair/full comparison on real compact inputs, retaining complete evidence."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from shared.contracts import content_hash,validate_outcome
from solver.adapters.contest import compact_scenario
from solver.public_api import solve,replan


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--seconds',type=float,default=15)
    args=parser.parse_args()
    report={'budget_per_method_s':args.seconds,'notes':['Both methods run in one Python process after computing the original plan; terrain caches are warm. Timings exclude HTTP/subprocess startup.','Relaxed variant intentionally removes all deadlines to test stability where time slack exists; original variant preserves every original deadline.'],'cases':[]}
    for variant in ['original_deadlines','relaxed_deadlines']:
        scene=compact_scenario()
        if variant=='relaxed_deadlines':
            for d in scene['demands']:d.update(expected_deadline_s=None,hard_deadline_s=None)
        snap={'schema_version':scene['schema_version'],'snapshot_id':'SNAP-BENCH-BASE','scenario_id':scene['scenario_id'],'scenario_state_version':1,'content_hash':content_hash(scene),'created_at':scene['start_time'],'scenario':scene}
        options={'schema_version':scene['schema_version'],'plan_id':'PLAN-BENCH-BASE','snapshot_id':snap['snapshot_id'],'objective':'time','mode':'quick','time_limit_s':args.seconds,'seed':42,'parent_plan_id':None,'event_id':None,'requested_model_scope':['cargo_unique','capacity','inventory','aircraft','battery','time_window','energy','terrain'],'allow_partial_service':False}
        baseline=solve(snap,options);assert baseline['plan'],baseline
        for uid in ['U01','U05','U07']:
            future=copy.deepcopy(snap);s=future['scenario']
            next(d for d in s['drones'] if d['drone_id']==uid)['status']='unavailable';s['state_version']=2
            future.update(snapshot_id='SNAP-BENCH-'+uid,scenario_state_version=2,content_hash=content_hash(s))
            opts={**options,'snapshot_id':future['snapshot_id'],'mode':'replan','parent_plan_id':baseline['plan']['plan_id'],'event_id':'EVT-BENCH-'+uid}
            event={'event_id':opts['event_id'],'event_type':'drone.unavailable','effective_time_s':0,'payload':{'drone_id':uid}}
            old={r['sortie_id'] for r in baseline['plan']['sorties']}
            results={}
            for mode in ['repair','full']:
                o={**opts,'plan_id':'PLAN-BENCH-'+uid+'-'+mode.upper()}
                outcome=replan(future,baseline['plan'],event,o) if mode=='repair' else solve(future,o)
                validate_outcome(outcome,future)
                ids={r['sortie_id'] for r in outcome['plan']['sorties']} if outcome['plan'] else set()
                results[mode]={'status':outcome['solver_status'],'runtime_s':outcome['runtime_s'],'first_feasible_s':outcome['first_feasible_s'],'preserved_count':len(old&ids),'removed_count':len(old-ids),'added_count':len(ids-old),'outcome':outcome}
            report['cases'].append({'variant':variant,'failed_drone_id':uid,'before_snapshot':snap,'after_snapshot':future,'before_plan':baseline['plan'],'results':results})
            print(variant,uid,[(mode,record['status'],round(record['runtime_s'],3),record['preserved_count']) for mode,record in results.items()],flush=True)
    out=ROOT/'evidence/solver/replan-comparison.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0


if __name__=='__main__':raise SystemExit(main())
