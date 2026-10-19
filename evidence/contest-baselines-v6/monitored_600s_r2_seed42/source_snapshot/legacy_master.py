import math,time,json,threading
from pathlib import Path
from collections import defaultdict
from ortools.sat.python import cp_model as cp

def ceil_tick(x,q):return int(math.ceil(x/q-1e-9))

def grid_route(r,P,q):
    m=P.models[r['model']];t=ceil_tick(r['prep'],q);arr=[]
    for i,fly in enumerate(r['flights']):
        t+=ceil_tick(fly,q)
        if i<len(r['stops']):arr.append(t);t+=ceil_tick(m['handover']+m['handover_box']*len(r['stops'][i][1]),q)
    return dict(duration=t,arrivals=arr,charge=ceil_tick(r['charge'],q))

def solve(P,pool,seconds=60,seed=0,q=.1,warm=None,M=None,K=None,objectives=('D','C','E','N'),fixed_D=None,max_C=None,explicit=False,workers=2,box_ids=None,incumbent_C_bound=False,stage_seconds=None,edd_order=False,fixed_starts=None,delivery_mode='sequential',max_E=None,evidence_path=None,deadline_monotonic=None,max_N=None,required_route_ids=None,stop_file=None):
    began=time.perf_counter();routes=list(pool.values());M=M or P.data['M'];K=K or P.data['K'];box_ids=box_ids or list(P.boxes)
    grid=[grid_route(r,P,q) for r in routes]
    required_route_ids=set(required_route_ids or ())
    assert required_route_ids <= set(r['id'] for r in routes)
    horizon=len(box_ids)*max(v['duration']+v['charge'] for v in grid)
    if max_C is not None:horizon=min(horizon,int(max_C/q+1e-7))
    model=cp.CpModel();xs=[];ss=[];ends=[];ranks=[];intervalU=defaultdict(list);intervalB=defaultdict(list);cover=defaultdict(list)
    Cbox={b:model.new_int_var(0,horizon,'C_'+b) for b in box_ids}
    for b in box_ids:
        due=P.boxes[b]['hard_due']
        if due is not None:model.add(Cbox[b]<=int(due/q+1e-7))
    entityU=defaultdict(list);entityB=defaultdict(list)
    for i,(r,gr) in enumerate(zip(routes,grid)):
        typ=r['model'];m=P.models[typ];x=model.new_bool_var(f'x{i}');s=model.new_int_var(0,horizon,f's{i}');end=model.new_int_var(0,horizon,f'e{i}')
        if r['id'] in required_route_ids:model.add(x==1)
        if fixed_starts and r['id'] in fixed_starts:
            model.add(x==1);model.add(s==ceil_tick(fixed_starts[r['id']],q))
        eb=model.new_int_var(0,horizon+gr['charge'],f'b{i}')
        model.add(s==0).only_enforce_if(x.Not());model.add(end==0).only_enforce_if(x.Not());model.add(eb==0).only_enforce_if(x.Not())
        iu=model.new_optional_interval_var(s,gr['duration'],end,x,f'iu{i}');ib=model.new_optional_interval_var(s,gr['duration']+gr['charge'],eb,x,f'ib{i}')
        intervalU[typ].append(iu);intervalB[typ].append(ib)
        if explicit:
            for prefix,count,duration,finish,store in [('u',M[typ],gr['duration'],end,entityU),('b',K[typ],gr['duration']+gr['charge'],eb,entityB)]:
                assignment=[]
                for k in range(count):
                    v=model.new_bool_var(f'{prefix}{i}_{k}');assignment.append(v)
                    store[typ,k].append(model.new_optional_interval_var(s,duration,finish,v,f'{prefix}iv{i}_{k}'))
                model.add(sum(assignment)==x)
        rr={}
        for j,(_,bs) in enumerate(r['stops']):
            # At D=0 each box has an effective hard due date. Equal processing
            # times within a stop imply EDD is feasibility-preserving by exchange.
            # Order changes neither route duration, energy nor return time.
            edd=sorted(bs,key=lambda b:(min(P.boxes[b]['expected_s'],P.boxes[b]['hard_due'] or float('inf')),b))
            for b in bs:
                if fixed_D==0 or edd_order:
                    rk=edd.index(b)+1;k=model.new_int_var(rk,rk,f'k{i}_{b}')
                else:
                    k=model.new_int_var(1,len(bs),f'k{i}_{b}')
                    model.add(k==1).only_enforce_if(x.Not())
                rr[b]=k
                delivery_rank=len(bs) if delivery_mode=='batch' else k
                model.add(Cbox[b]==s+gr['arrivals'][j]+ceil_tick(m['handover'],q)+ceil_tick(m['handover_box'],q)*delivery_rank).only_enforce_if(x)
                cover[b].append(x)
            for aidx,a in enumerate(bs if fixed_D!=0 and not edd_order else []):
                for b in bs[aidx+1:]:
                    model.add(rr[a]!=rr[b]).only_enforce_if(x)
                    # Order true deadline/priority equivalents to break harmless label symmetry.
                    aa=P.boxes[a];bb=P.boxes[b]
                    if (aa['hard_due'],aa['expected_s'],aa['priority'])==(bb['hard_due'],bb['expected_s'],bb['priority']):model.add(rr[a]<rr[b]).only_enforce_if(x)
        xs.append(x);ss.append(s);ends.append(end);ranks.append(rr)
    for b in box_ids:model.add(sum(cover[b])==1)
    if explicit:
        for intervals in list(entityU.values())+list(entityB.values()):model.add_no_overlap(intervals)
    else:
        for g in P.models:
            model.add_cumulative(intervalU[g],[1]*len(intervalU[g]),M[g]);model.add_cumulative(intervalB[g],[1]*len(intervalB[g]),K[g])
    cm=model.new_int_var(0,horizon,'Cmax');model.add_max_equality(cm,ends)
    for g in P.models:model.add(sum(gr['duration']*x for r,gr,x in zip(routes,grid,xs) if r['model']==g)<=M[g]*cm)
    tard=[]
    for b in box_ids:
        late=model.new_int_var(0,horizon,'late'+b);model.add_max_equality(late,[0,Cbox[b]-int(P.boxes[b]['expected_s']/q+1e-7)])
        assert int(P.boxes[b]['priority'])==P.boxes[b]['priority'];tard.append(int(P.boxes[b]['priority'])*late)
    expr={'D':sum(tard),'C':cm,'E':sum(round(r['energy']*1e6)*x for r,x in zip(routes,xs)),'N':sum(xs)}
    if 'H' in objectives:
        hard=[b for b in box_ids if P.boxes[b]['hard_due'] is not None]
        slack=model.new_int_var(-horizon,max(int(P.boxes[b]['hard_due']/q) for b in hard),'min_hard_slack')
        model.add_min_equality(slack,[int(P.boxes[b]['hard_due']/q)-Cbox[b] for b in hard]);expr['H']=-slack
    if fixed_D is not None:model.add(expr['D']<=round(fixed_D/q))
    if max_C is not None:model.add(cm<=int(max_C/q+1e-7))
    if max_N is not None:model.add(expr['N']<=int(max_N))
    # Conservative micro-kWh cap: summing ceilings cannot admit an actual
    # floating-precision energy sum above the requested physical cap.
    if max_E is not None:model.add(sum(int(math.ceil(r['energy']*1e6-1e-9))*x for r,x in zip(routes,xs))<=int(math.floor(max_E*1e6+1e-9)))
    warmids={v['route']['id']:v for v in warm} if warm else {}
    if warmids:
        for i,r in enumerate(routes):model.add_hint(xs[i],int(r['id'] in warmids))
        # Rebuild a conservative-grid feasible incumbent from its actual resource
        # sequences, rather than hinting rounded continuous starts independently.
        if all('aircraft' in v and 'battery' in v and 'orders' in v for v in warmids.values()) and set(warmids)<=set(r['id'] for r in routes) and all(len({v['aircraft'] for v in warmids.values() if v['route']['model']==g})<=M[g] and len({v['battery'] for v in warmids.values() if v['route']['model']==g})<=K[g] for g in P.models):
            lookup={r['id']:i for i,r in enumerate(routes)};ready_u={};ready_b={};cs={};warmtime={};warmmax=0
            for v in sorted(warmids.values(),key=lambda v:(v['start'],v['route']['id'])):
                i=lookup[v['route']['id']];gr=grid[i];g=routes[i]['model'];m=P.models[g]
                start=max(ready_u.get(v['aircraft'],0),ready_b.get(v['battery'],0));end=start+gr['duration']
                ready_u[v['aircraft']]=end;ready_b[v['battery']]=end+gr['charge'];warmtime[i]=start;warmmax=max(warmmax,end)
                model.add_hint(ss[i],start);model.add_hint(ends[i],end)
                for j,order in enumerate(v['orders']):
                    for k,b in enumerate(order,1):
                        model.add_hint(ranks[i][b],k);cs[b]=start+gr['arrivals'][j]+ceil_tick(m['handover'],q)+ceil_tick(m['handover_box'],q)*(len(order) if delivery_mode=='batch' else k)
            if set(cs)==set(box_ids):
                for b,c in cs.items():model.add_hint(Cbox[b],c)
                # A hint never changes objective preference. In particular a
                # zero-late high-energy hint cannot impose D=0 under max_E.
                if fixed_D == 0 and all(c<=int(P.boxes[b]['expected_s']/q+1e-7) and (P.boxes[b]['hard_due'] is None or c<=int(P.boxes[b]['hard_due']/q+1e-7)) for b,c in cs.items()) and (max_E is None or sum(math.ceil(v['route']['energy']*1e6-1e-9) for v in warmids.values())<=math.floor(max_E*1e6+1e-9)) and (max_C is None or warmmax<=int(max_C/q+1e-7)):
                    model.add(expr['D']==0);fixed_D=0
                    if incumbent_C_bound:model.add(cm<=warmmax)
                    model.add_hint(cm,warmmax)
    invalid=model.validate()
    assert not invalid,invalid
    evidence=[];chosen=None;last_values=None;progress=[]
    class Callback(cp.CpSolverSolutionCallback):
        def __init__(self,obj):super().__init__();self.obj=obj
        def on_solution_callback(self):
            progress.append(dict(stage=self.obj,time_s=self.wall_time,objective=self.objective_value,bound=self.best_objective_bound))
            if self.obj=='D' and self.objective_value==0:self.stop_search()
    for stage in objectives:
        if (stop_file and Path(stop_file).exists()) or (deadline_monotonic is not None and time.perf_counter()>=deadline_monotonic):break
        if stage=='D' and fixed_D==0:continue
        model.minimize(expr[stage]);solver=cp.CpSolver();solver.parameters.max_time_in_seconds=seconds
        if stage_seconds and stage in stage_seconds:solver.parameters.max_time_in_seconds=stage_seconds[stage]
        if deadline_monotonic is not None:
            solver.parameters.max_time_in_seconds=min(solver.parameters.max_time_in_seconds,max(0.05,deadline_monotonic-time.perf_counter()))
        solver.parameters.num_search_workers=workers;solver.parameters.random_seed=seed
        done=threading.Event()
        def interrupt_on_stop():
            while not done.wait(.5):
                if (stop_file and Path(stop_file).exists()) or (deadline_monotonic is not None and time.perf_counter()>=deadline_monotonic):
                    solver.stop_search();return
        watcher=threading.Thread(target=interrupt_on_stop,daemon=True);watcher.start()
        try:status=solver.solve(model,Callback(stage))
        finally:done.set();watcher.join(timeout=1)
        label=solver.status_name(status)
        valid=status in (cp.OPTIMAL,cp.FEASIBLE)
        row=dict(stage=stage,status=label,objective=solver.objective_value if valid else None,best_bound=solver.best_objective_bound,wall_time=solver.wall_time,branches=solver.num_branches,conflicts=solver.num_conflicts,pool_size=len(routes),q=q,seed=seed,workers=workers)
        evidence.append(row);print('SOLVE',stage,label,row['objective'],row['best_bound'],round(row['wall_time'],2),'pool',len(routes),flush=True)
        if not valid:
            if evidence_path:
                Path(evidence_path).write_text(json.dumps(dict(evidence=evidence,progress=progress,selected=chosen,grid_objectives=last_values),ensure_ascii=False,indent=2),encoding='utf-8')
            break
        value=solver.value(expr[stage]);model.add(expr[stage]<=value)
        chosen=[]
        for i,r in enumerate(routes):
            if solver.value(xs[i]):
                orders=[sorted(bs,key=lambda b:solver.value(ranks[i][b])) for _,bs in r['stops']]
                chosen.append(dict(route=r,start=solver.value(ss[i])*q,orders=orders,grid_duration=grid[i]['duration']*q,grid_charge=grid[i]['charge']*q))
        last_values={k:solver.value(v)*(q if k in ('D','C','H') else 1e-6 if k=='E' else 1) for k,v in expr.items()}
        if evidence_path:
            Path(evidence_path).write_text(json.dumps(dict(evidence=evidence,progress=progress,selected=chosen,grid_objectives=last_values),ensure_ascii=False,indent=2),encoding='utf-8')
            Path(evidence_path).with_name('stage_'+stage+'_solution.json').write_text(json.dumps(dict(selected=chosen,grid_objectives=last_values,evidence=row),ensure_ascii=False,indent=2),encoding='utf-8')
        model.clear_hints()
        for i in range(len(model.proto.variables)):
            v=model.get_int_var_from_proto_index(i);model.add_hint(v,solver.value(v))
    return dict(selected=chosen,evidence=evidence,grid_objectives=last_values,progress=progress,seconds=time.perf_counter()-began,time_quantum=q,candidate_pool_complete=False,D_zero_incumbent_certificate=fixed_D==0,incumbent_C_bound=incumbent_C_bound,delivery_mode=delivery_mode,max_energy_kwh=max_E,scope='restricted route pool and conservative integer time grid')

def decode(P,result,M=None,K=None,retime=True):
    M=M or P.data['M'];K=K or P.data['K'];selected=sorted(result['selected'],key=lambda x:(x['start'],x['route']['id']))
    usedU={g:[0.]*M[g] for g in P.models};usedB={g:[0.]*K[g] for g in P.models}
    idsU={g:sorted(k for k,v in P.data['aircraft'].items() if v==g) for g in P.models}
    for g in P.models:
        idsU[g]=(idsU[g]+[f'{g}-EXTRA-{i}' for i in range(1,M[g]+1)])[:M[g]]
    previousU={};previousB={};rows=[]
    for v in selected:
        r=v['route'];g=r['model'];s=v['start']
        u=next(i for i,t in enumerate(usedU[g]) if t<=s+1e-7);b=next(i for i,t in enumerate(usedB[g]) if t<=s+1e-7)
        usedU[g][u]=s+v['grid_duration'];usedB[g][b]=s+v['grid_duration']+v['grid_charge']
        uid=idsU[g][u];bid=f'{g}-BAT-{b+1:02d}';preu=previousU.get(uid);preb=previousB.get(bid)
        if retime:s=max(0,preu['return'] if preu else 0,preb['battery_ready'] if preb else 0)
        row=dict(sortie=f'Q2-{len(rows)+1:03d}',route=r,aircraft=uid,battery=bid,start=s,return_=s+r['duration'],battery_ready=s+r['duration']+r['charge'],orders=v['orders'],grid_start=v['start'])
        row['return']=row.pop('return_');rows.append(row);previousU[uid]=row;previousB[bid]=row
    return rows
