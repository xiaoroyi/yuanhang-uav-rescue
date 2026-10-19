"""Add incumbent observation hooks to isolated CP models; math is unchanged."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).parent
ROOT=HERE.parents[1]
EVIDENCE=ROOT/'evidence/contest-baselines-v2'

def main():
    EVIDENCE.mkdir(exist_ok=True,parents=True)
    master=(HERE/'legacy_master.py').read_text(encoding='utf-8')
    old='required_route_ids=None,stop_file=None):'
    assert old in master
    master=master.replace(old,'required_route_ids=None,stop_file=None,incumbent_callback=None):',1)
    anchor="            if self.obj=='D' and self.objective_value==0:self.stop_search()"
    assert anchor in master
    observe="""            if incumbent_callback is not None:
                observed_at=time.perf_counter()
                selected=[]
                for i,r in enumerate(routes):
                    if self.value(xs[i]):
                        orders=[sorted(bs,key=lambda b:self.value(ranks[i][b])) for _,bs in r['stops']]
                        selected.append(dict(route=r,start=self.value(ss[i])*q,orders=orders,grid_duration=grid[i]['duration']*q,grid_charge=grid[i]['charge']*q))
                incumbent_callback(dict(selected=selected),dict(found_perf=observed_at,stage=self.obj,objective=self.objective_value,bound=self.best_objective_bound))
"""
    master=master.replace(anchor,observe+anchor,1)
    (HERE/'master_v2.py').write_text(master,encoding='utf-8')
    joint=(HERE/'legacy_joint.py').read_text(encoding='utf-8')
    old='stop_path=None):'
    assert old in joint
    joint=joint.replace(old,'stop_path=None,incumbent_callback=None):',1)
    start=joint.index('        trans=[]\n',joint.index('    for stage in objectives:'))
    stop=joint.index("        color(best,P);dump(directory/'solution_q3.json',best)",start)
    extract=joint[start:stop].replace('solver.value','reader.value')
    extract='\n'.join(line for line in extract.splitlines() if not line.strip().startswith('coverage=['))
    helper='    def extract_incumbent(reader):\n        coverage=[]\n'+extract+'\n        color(best,P)\n        return best\n'
    anchor='    evidence=[];best=None;progress=[]\n'
    assert anchor in joint
    joint=joint.replace(anchor,helper+anchor,1)
    anchor="            if self.stage=='D' and self.objective_value==0:self.stop_search()"
    assert anchor in joint
    observe="""            if incumbent_callback is not None:
                observed_at=time.perf_counter()
                incumbent_callback(extract_incumbent(self),dict(found_perf=observed_at,stage=self.stage,objective=self.objective_value,bound=self.best_objective_bound))
"""
    joint=joint.replace(anchor,observe+anchor,1)
    (HERE/'joint_v2.py').write_text(joint,encoding='utf-8')
    rows=[]
    for old,new in [('legacy_master.py','master_v2.py'),('legacy_joint.py','joint_v2.py')]:
        rows.append(dict(source=f'scripts/contest_baselines/{old}',source_sha256=hashlib.sha256((HERE/old).read_bytes()).hexdigest(),
            destination=f'scripts/contest_baselines/{new}',destination_sha256=hashlib.sha256((HERE/new).read_bytes()).hexdigest(),
            change='Add optional feasible-incumbent callback and Q3 extraction helper. Constraints/objectives/rounding unchanged.'))
    (EVIDENCE/'solver_sources.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
