"""Method-owned route construction inside independently generated radio windows.

Only the continuous cover relaxation and heuristic backtracking choose routes.
The CP decoder receives an exact disjoint cover with EVERY route mandatory;
its task is exclusively aircraft/battery timing within the supplied windows.
No supplied complete transport or relay solution is accepted or read here.
"""
import time
import numpy as np

from construction_v6 import Constructor
import master_v4


class WindowConstructor(Constructor):
    def __init__(self, P, pool, cap, allowed_start_intervals, quantum=.1,
                 schedule_seconds=2., seed=42):
        self.quantum=quantum
        self.allowed_start_intervals={rid:[(int(lo),int(hi)) for lo,hi in intervals if lo<=hi]
            for rid,intervals in allowed_start_intervals.items()}
        candidates=[r for r in pool if self.allowed_start_intervals.get(r['id'])]
        super().__init__(P,candidates,cap)
        self.schedule_seconds=schedule_seconds
        self.seed=seed
        self.last_schedule_evidence=[]
        self.infeasible_covers=set()
        # These are necessary bounds in this particular radio-window family,
        # not additional claims about the unrestricted original problem.
        self.latest=[min(old,max(hi for lo,hi in self.allowed_start_intervals[r['id']])*quantum)
            for old,r in zip(self.latest,self.pool)]
        self.by=[[] for _ in self.boxes]
        for i,r in enumerate(self.pool):
            if self.latest[i]>=-1e-7:
                for b in r['boxes']:self.by[self.bi[b]].append(i)
        if self.cuts:
            updated=[]
            for g in self.groups:
                for T in sorted(set([1800.,2400.,3000.,3600.,4200.,4800.,5400.,cap])):
                    if T>cap:continue
                    for battery in [False,True]:
                        stock=P.data['K' if battery else 'M'][g]
                        coeff=[min(r['duration']+(r['charge'] if battery else 0),max(0.,T-self.latest[i]))
                            if r['model']==g else 0. for i,r in enumerate(self.pool)]
                        updated.append((T*stock,coeff))
            self.cuts=updated
            self.cut_matrix=np.array([coeff for _,coeff in self.cuts])

    def cover(self,rng,deadline,mode='greedy',objective='energy',pheromone=None,
              fixed=(),max_nodes=25000,excluded=()):
        if any(r['id'] not in self.rid for r in fixed):
            self.stats['fixed_routes_outside_window']+=1
            return None
        return super().cover(rng,deadline,mode,objective,pheromone,fixed,max_nodes,excluded)

    def schedule(self,routes,deadline,max_nodes=100000):
        """Solve fixed-group timing, with no discrete route selection freedom."""
        del max_nodes
        self.stats['window_schedule_calls']+=1
        if time.perf_counter()>=deadline-.02 or not routes:return None
        ids=[r['id'] for r in routes]
        self.last_proposal_route_ids=list(ids)
        assert len(ids)==len(set(ids))
        boxes=[b for r in routes for b in r['boxes']]
        assert len(boxes)==len(set(boxes))==len(self.boxes)
        assert set(boxes)==set(self.boxes)
        seconds=min(self.schedule_seconds,deadline-time.perf_counter())
        result=master_v4.solve(self.P,{r['id']:r for r in routes},seconds=seconds,
            seed=self.seed+self.stats['window_schedule_calls'],q=self.quantum,workers=1,
            objectives=('C',),fixed_D=0,max_C=self.cap,delivery_mode='batch',warm=None,
            required_route_ids=ids,allowed_start_intervals=self.allowed_start_intervals,
            stop_on_first=True,deadline_monotonic=deadline)
        self.last_schedule_evidence=result['evidence']
        if not result['selected']:
            status=result['evidence'][-1]['status'] if result['evidence'] else 'DEADLINE'
            self.stats['window_schedule_'+status]+=1
            self.stats['schedule_failures']+=1
            # A proof applies only to this fixed route set in THIS template.
            # UNKNOWN/deadline cases do not justify excluding any cover.
            if status=='INFEASIBLE':
                signature=tuple(sorted(self.rid[rid] for rid in ids))
                if signature not in self.infeasible_covers:
                    self.infeasible_covers.add(signature)
                    selected=set(signature)
                    self.cuts.append((len(signature)-1.,[1. if i in selected else 0.
                        for i in range(len(self.pool))]))
                    self.cut_matrix=np.array([coeff for _,coeff in self.cuts])
                    self.stats['proven_infeasible_cover_nogoods']+=1
            return None
        assert {v['route']['id'] for v in result['selected']}==set(ids)
        self.stats['scheduled_covers']+=1
        return master_v4.decode(self.P,result,retime=False)

    def build(self,rng,deadline,mode='greedy',objective='energy',pheromone=None,
              fixed=(),cover_seconds=1.,schedule_seconds=2.):
        selected=self.cover(rng,min(deadline,time.perf_counter()+cover_seconds),
            mode,objective,pheromone,fixed)
        if selected is None:return None
        return self.schedule(selected,min(deadline,time.perf_counter()+schedule_seconds))
