"""Q3 communication reduction derived only from route geometry, inside each run.

The restricted relay-site set is selected afresh from candidate coverage masks.
Adjacent atoms whose allowed relay sets are equal are conservatively coalesced.
This requires a single sortie to cover a coalesced interval and can exclude
mid-interval relay handovers; it cannot admit an uncovered time interval. Neither
operation reads a complete solution, schedule, paper result, or shared incumbent.
Every produced solution still needs the unchanged independent Q3 validator.
"""
from pathlib import Path
import itertools
import math
import time
import warnings
import numpy as np
from scipy.optimize import milp, Bounds, LinearConstraint
import joint_v4
import master_v4
from legacy_routes import Physics,charge
from support import OUT as DEFAULT_OUT, dump

OUT = DEFAULT_OUT


def intersect(a,b):
    pieces=sorted((max(x,z),min(y,w)) for x,y in a for z,w in b if max(x,z)<=min(y,w))
    merged=[]
    for lo,hi in pieces:
        if merged and lo<=merged[-1][1]+1:merged[-1]=(merged[-1][0],max(merged[-1][1],hi))
        else:merged.append((lo,hi))
    return merged


def make_relay(site,start,finish,slot):
    e=site['fly_energy']+1.1*(finish-start-site['arrival_offset'])/3600
    r=dict(sortie=f'R-{slot+1:03}',slot=slot,site=site,start=start,
        arrival=start+site['arrival_offset'],link_complete=start+site['ready_offset'],
        service_end=finish,energy=e,SOC=1-e/3.2,charge=charge(1-e/3.2,1800))
    r['return']=finish+site['back'];r['component_ready']=r['return']+r['charge'];r['aircraft_ready']=r['return']+300
    return r


def trim_unused_relay_time(sol, atoms):
    """Shrink each generated relay interval to actual selected-route coverage.

    Every new resource interval is a subset of its own original interval, with
    lower energy/charge time, so shrinking cannot add resource conflicts.
    """
    needs=[[] for _ in sol['relay']]
    for row in sol['transport']:
        for atom in atoms[row['route']['id']]:
            lo=row['start']+atom['a'];hi=row['start']+atom['b']
            choices=[j for j,r in enumerate(sol['relay']) if r['site']['id'] in atom['sites']
                and r['link_complete']<=lo+1e-7 and r['service_end']>=hi-1e-7]
            assert choices,(row['route']['id'],lo,hi)
            def extension(j):
                old=needs[j]
                return max([hi]+[v[1] for v in old])-min([lo]+[v[0] for v in old])
            j=min(choices,key=extension);needs[j].append((lo,hi))
    relay=[]
    for j,(r,intervals) in enumerate(zip(sol['relay'],needs)):
        if not intervals:continue
        lo=min(a for a,b in intervals);hi=max(b for a,b in intervals)
        start=max(r['start'],math.floor((lo-r['site']['ready_offset'])*10+1e-7)/10)
        end=min(r['service_end'],math.ceil(hi*10-1e-7)/10)
        relay.append(make_relay(r['site'],start,end,j))
    sol['relay']=relay
    return sol


def iter_templates(pool, atoms, sites, deadline, seed=42, max_C=None, reduce=True):
    """Yield physical windows/domains without selecting a transport route set.

    Domains are inclusive integer 0.1s ticks. Consumers must also enforce all
    transport resource and deadline constraints. The initial site reduction and
    every generated window are part of the caller's own search time budget.
    """
    if reduce:
        sites,atoms,reduction=reduce_coverage(pool,atoms,sites,seed,
            seconds=min(2,max(.05,deadline-time.monotonic())))
    else:
        reduction=None
    all_boxes={b for route in pool for b in route['boxes']}
    # A time-minimization call has no imposed completion cap. These horizons are
    # search templates, expanded when no solution exists; they are not constraints
    # of the original problem and a successful solution may later be improved.
    horizons=[max_C] if max_C is not None else [6500.,7500.,9000.,12000.]
    orders=list(itertools.permutations(sites,3)) if len(sites)>=3 else list(itertools.product(sites,repeat=3))
    rng=np.random.default_rng(seed);rng.shuffle(orders)
    for horizon in horizons:
        for end_first in [1500.,1800.,1200.,2100.,2400.,900.,2700.,3000.]:
            for order in orders:
                if time.monotonic()>=deadline-.05:return
                first=make_relay(order[0],0.,end_first,0)
                last_start=math.ceil(first['aircraft_ready']*10-1e-7)/10
                rr=[first,
                    make_relay(order[1],0.,math.floor((horizon-order[1]['back'])*10+1e-7)/10,1),
                    make_relay(order[2],last_start,math.floor((horizon-order[2]['back'])*10+1e-7)/10,2)]
                if any(r['service_end']<r['link_complete'] or not 0<r['energy']<=2.56 for r in rr):continue
                domains={}
                for route in pool:
                    intervals=[(0,math.floor((horizon-route['duration'])*10+1e-7))]
                    for atom in atoms[route['id']]:
                        candidates=[]
                        for relay in rr:
                            if relay['site']['id'] not in atom['sites']:continue
                            lo=math.ceil(relay['link_complete']*10-1e-7)-math.floor(atom['a']*10+1e-7)
                            hi=math.floor(relay['service_end']*10+1e-7)-math.ceil(atom['b']*10-1e-7)
                            if lo<=hi:candidates.append((lo,hi))
                        intervals=intersect(intervals,candidates)
                        if not intervals:break
                    if intervals:domains[route['id']]=intervals
                possible=[r for r in pool if r['id'] in domains]
                if {b for r in possible for b in r['boxes']}!=all_boxes:continue
                yield dict(pool=possible,allowed_start_intervals=domains,relay=rr,
                    horizon=horizon,sites=[s['id'] for s in order],end_first=end_first,
                    coverage_reduction=reduction)


def template_solve(name, pool, atoms, sites, deadline, seed=42, max_C=None,
                   objectives=('C',), workers=1, incumbent_callback=None, template_seconds=5.):
    """Solve route choice/scheduling only inside independent relay templates."""
    P=Physics();directory=Path(OUT)/name;directory.mkdir(parents=True,exist_ok=True)
    records=[]
    for attempt,template in enumerate(iter_templates(pool,atoms,sites,deadline,seed,max_C,reduce=False),1):
        budget=min(template_seconds,max(.05,deadline-time.monotonic()))
        result=master_v4.solve(P,{r['id']:r for r in template['pool']},seconds=budget,
            seed=seed+attempt,workers=workers,objectives=objectives,fixed_D=0,max_C=template['horizon'],
            delivery_mode='batch',warm=None,allowed_start_intervals=template['allowed_start_intervals'],
            stop_on_first=True,evidence_path=directory/f'template_{attempt:04}.json',
            deadline_monotonic=time.perf_counter()+budget)
        records.append(dict(attempt=attempt,sites=template['sites'],end_first=template['end_first'],
            horizon=template['horizon'],possible_routes=len(template['pool']),evidence=result['evidence']))
        dump(directory/'template_progress.json',dict(records=records))
        if not result['selected']:continue
        sol=dict(transport=master_v4.decode(P,result,retime=False),relay=template['relay'],resources=[2,6],
            search_scope='Independently generated three-relay time-window template',supplied_initial_solution=False)
        trim_unused_relay_time(sol,atoms)
        joint_v4.color(sol,P);dump(directory/'solution_q3.json',sol)
        if incumbent_callback is not None:
            incumbent_callback(sol,dict(found_perf=time.perf_counter(),stage='template_first_feasible',
                objective=None,bound=None))
        return sol
    return None


def reduce_coverage(pool, atoms, sites, seed=42, seconds=2.0):
    began = time.perf_counter()
    signatures = sorted({tuple(sorted(a['sites'])) for r in pool for a in atoms[r['id']]})
    if not signatures:
        return sites[:1], {r['id']: [] for r in pool}, dict(original_atoms=0, reduced_atoms=0)
    ids = [s['id'] for s in sites]
    masks = [set(k) for k in signatures]
    matrix = np.array([[int(sid in k) for sid in ids] for k in masks], dtype=float)
    if np.any(matrix.sum(axis=1) == 0):
        raise ValueError('A route contains a communication atom with no candidate relay site')
    # Set cover is an independent physical candidate selection, not a transport
    # schedule or an imported initial solution. All time is charged to this call.
    rng = np.random.default_rng(seed)
    cost = np.array([1.0+s['back']/100000.0 for s in sites]) + rng.random(len(sites))*.0001
    # SciPy forwards this supported HiGHS option but warns because its public
    # MILP option whitelist omits it. Keep this MILP and the constructor's LPs
    # at one thread from their first call to avoid global scheduler conflicts
    # and oversubscription when independent configurations run concurrently.
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore',
            message=r"Unrecognized options detected: \{'threads'\}\. These will be passed to HiGHS verbatim\.",
            category=RuntimeWarning)
        result = milp(cost, integrality=np.ones(len(sites)), bounds=Bounds(0,1),
            constraints=LinearConstraint(matrix, 1, np.inf),
            options={'time_limit': max(.05, seconds), 'mip_rel_gap': .001, 'threads':1})
    if result.x is not None:
        selected = [s for i,s in enumerate(sites) if result.x[i]>.5]
    else:
        todo = set(range(len(masks))); selected = []
        while todo:
            s = max((s for s in sites if s not in selected),
                key=lambda s: sum(s['id'] in masks[i] for i in todo)/(1+s['back']/100000))
            selected.append(s); todo = {i for i in todo if s['id'] not in masks[i]}
    selected_ids = {s['id'] for s in selected}
    reduced = {}
    for r in pool:
        rows = []
        for a in atoms[r['id']]:
            allowed = sorted(selected_ids.intersection(a['sites']))
            assert allowed, r['id']
            if rows and rows[-1]['sites']==allowed and a['a']<=rows[-1]['b']+1e-8:
                rows[-1]['b'] = max(rows[-1]['b'], a['b'])
            else:
                rows.append(dict(a=a['a'], b=a['b'], sites=allowed))
        reduced[r['id']] = rows
    info = dict(original_sites=len(sites), restricted_sites=len(selected),
        selected_site_ids=sorted(selected_ids), original_atoms=sum(len(atoms[r['id']]) for r in pool),
        reduced_atoms=sum(map(len,reduced.values())), reduction_wall_s=time.perf_counter()-began,
        highs_threads=1,
        source='Independent set cover of physical route coverage masks; conservative adjacent merging under restricted sites',
        no_supplied_solution=True, candidate_restriction=True,
        conservative_atom_restriction='One relay sortie per merged interval; mid-interval handovers may be excluded')
    return selected, reduced, info


def solve(name='joint_v6', seconds=100, pool=None, atoms=None, sites_override=None,
          deadline=None, seed=42, **kwargs):
    began = time.monotonic()
    deadline = min(deadline, began+seconds) if deadline is not None else began+seconds
    if kwargs.get('warm') is not None or kwargs.get('fixed_transport') is not None:
        raise ValueError('v6 searches must not receive a supplied complete solution')
    selected, reduced, info = reduce_coverage(pool, atoms, sites_override, seed=seed,
        seconds=min(2,max(.05,deadline-time.monotonic())))
    directory = Path(OUT)/name
    dump(directory/'coverage_reduction.json', info)
    print('Q3_COVERAGE_REDUCTION', name, info, flush=True)
    joint_v4.OUT = Path(OUT)
    remaining = deadline-time.monotonic()
    if remaining <= .05:
        return None
    return joint_v4.solve(name=name, seconds=remaining, pool=pool, atoms=reduced,
        sites_override=selected, deadline=deadline, seed=seed, **kwargs)
