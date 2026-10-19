from support import *
from legacy_routes import Physics,charge
from legacy_master import ceil_tick
from ortools.sat.python import cp_model as cp
from collections import defaultdict
import math,time,copy,threading

def solve(name='joint_fixed_routes',fixed=False,seconds=100,slots=8,seed=0,site_ids=None,pool=None,atoms=None,resources=(2,6),max_C=None,objectives=('D','C','E','N'),slot_sites=None,zero_late=False,warm=None,max_E=None,max_N=None,workers=2,forbidden_routes=(),forbidden_slots=(),fix_route_ids=None,sites_override=None,complete_warm=False,presolve=True,max_transport=None,deadline=None,stop_path=None,incumbent_callback=None):
    data=inputs();P=Physics();q=.1;H=240000 if max_C is None else math.ceil(max_C/q)+1;beg=time.time();directory=OUT/name;directory.mkdir(exist_ok=True,parents=True)
    seedrows=[] # No historical solution is supplied to any baseline.
    routes=pool if pool is not None else [r['route'] for r in seedrows];atoms=atoms if atoms is not None else json.loads((OUT/'coverage_atoms.json').read_text(encoding='utf-8'))
    allsites=sites_override if sites_override is not None else json.loads((OUT/'relay_sites.json').read_text(encoding='utf-8'));sites=[s for s in allsites if site_ids is None or s['id'] in site_ids];sindex={s['id']:i+1 for i,s in enumerate(sites)}
    model=cp.CpModel();uiv=defaultdict(list);biv=defaultdict(list);cover=defaultdict(list);xs=[];starts=[];ends=[];ranks=[]
    cb={b:model.new_int_var(0,H,'cb'+b) for b in P.boxes}
    if not fixed:
        for b in P.boxes:
            if P.boxes[b]['hard_due'] is not None:model.add(cb[b]<=int(P.boxes[b]['hard_due']/q))
    for i,r in enumerate(routes):
        x=model.new_bool_var('x'+str(i));s=model.new_int_var(0,H,'s'+str(i));e=model.new_int_var(0,H,'e'+str(i));rr={};g=r['model'];m=P.models[g]
        if r['id'] in forbidden_routes:model.add(x==0)
        if fix_route_ids is not None:model.add(x==int(r['id'] in fix_route_ids))
        if fixed:
            model.add(x==1);model.add(s==int(seedrows[i]['start']/q));model.add(e==ceil_tick(seedrows[i]['return'],q))
        else:
            model.add(s==0).only_enforce_if(x.Not());model.add(e==0).only_enforce_if(x.Not())
            if max_C is not None:model.add(s<=math.floor((max_C-r['duration'])/q)).only_enforce_if(x)
            dur=ceil_tick(r['duration'],q);endb=model.new_int_var(0,H+100000,'eb'+str(i))
            uiv[g].append(model.new_optional_interval_var(s,dur,e,x,'u'+str(i)))
            biv[g].append(model.new_optional_interval_var(s,ceil_tick(r['duration']+r['charge'],q),endb,x,'b'+str(i)))
            for j,(_,bs) in enumerate(r['stops']):
                # Under zero_late, identical handling times make EDD safe:
                # each deadline is min(expected,hard), all jobs are released
                # at the same arrival, and route length/energy is unchanged.
                edd=sorted(bs,key=lambda b:(min(P.boxes[b]['expected_s'],P.boxes[b]['hard_due'] if P.boxes[b]['hard_due'] is not None else float('inf')),b))
                for b in bs:
                    kk=edd.index(b)+1
                    rr[b]=model.new_int_var(kk,kk,'k'+str(i)+b);cover[b].append(x)
                    model.add(cb[b]==s+ceil_tick(r['arrivals'][j]+m['handover']+m['handover_box']*len(bs),q)).only_enforce_if(x)
                model.add_all_different([rr[b] for b in bs])
        xs.append(x);starts.append(s);ends.append(e);ranks.append(rr)
    if not fixed:
        for b in P.boxes:model.add(sum(cover[b])==1)
        for g in P.models:
            model.add_cumulative(uiv[g],[1]*len(uiv[g]),P.data['M'][g]);model.add_cumulative(biv[g],[1]*len(biv[g]),P.data['K'][g])
    # Variable-length relay slots. 9 micro-kWh units preserve 275/9 per .1 s.
    ys=[];locs=[];Y=[];B=[];F=[];R=[];ER=[];CH=[];riv=[];hiv=[]
    ready=[0]+[ceil_tick(s['ready_offset'],q) for s in sites];backs=[0]+[ceil_tick(s['back'],q) for s in sites]
    alpha=[0]+[math.ceil(9e6*(s['fly_energy']-1.1*s['arrival_offset']/3600)) for s in sites]
    for j in range(slots):
        y=model.new_bool_var('y'+str(j));loc=model.new_int_var(0,len(sites),'loc'+str(j));st=model.new_int_var(0,H,'Y'+str(j));b=model.new_int_var(0,H,'B'+str(j));f=model.new_int_var(0,H,'F'+str(j));ret=model.new_int_var(0,H,'R'+str(j))
        if j in forbidden_slots:model.add(y==0)
        model.add(loc>=1).only_enforce_if(y);model.add(loc==0).only_enforce_if(y.Not())
        if slot_sites is not None:model.add(loc==sindex[slot_sites[j]]).only_enforce_if(y)
        for v in (st,b,f,ret):model.add(v==0).only_enforce_if(y.Not())
        dt=model.new_int_var(0,max(ready),'dt'+str(j));bk=model.new_int_var(0,max(backs),'bk'+str(j));aa=model.new_int_var(min(alpha),max(alpha),'alpha'+str(j))
        model.add_element(loc,ready,dt);model.add_element(loc,backs,bk);model.add_element(loc,alpha,aa)
        model.add(b==st+dt);model.add(f>=b);model.add(ret==f+bk)
        energy9=model.new_int_var(0,23040000,'energy9'+str(j));energy=model.new_int_var(0,2560000,'er'+str(j))
        model.add(energy9==aa+275*(f-st));model.add_division_equality(energy,energy9+8,9)
        high=model.new_bool_var('high'+str(j));model.add(energy>=320001).only_enforce_if(high);model.add(energy<=320000).only_enforce_if(high.Not())
        chi=model.new_int_var(0,15400,'chi'+str(j));lowcharge=model.new_int_var(0,50400,'lowcharge'+str(j));highcharge=model.new_int_var(0,20000,'highcharge'+str(j))
        model.add_division_equality(lowcharge,63*energy+3199,3200);model.add_division_equality(highcharge,13*energy+3199,3200)
        model.add(chi==lowcharge).only_enforce_if(high.Not());model.add(chi==5000+highcharge).only_enforce_if(high)
        eu=model.new_int_var(0,H+3000,'eru'+str(j));eh=model.new_int_var(0,H+15400,'erh'+str(j));su=model.new_int_var(0,H+3000,'szu'+str(j));sh=model.new_int_var(0,H+15400,'szh'+str(j))
        model.add(eu==ret+3000*y);model.add(eh==ret+chi);model.add(su==eu-st);model.add(sh==eh-st)
        riv.append(model.new_optional_interval_var(st,su,eu,y,'ri'+str(j)));hiv.append(model.new_optional_interval_var(st,sh,eh,y,'hi'+str(j)))
        if j:model.add(y<=ys[-1]);model.add(st>=Y[-1]).only_enforce_if(y)
        ys.append(y);locs.append(loc);Y.append(st);B.append(b);F.append(f);R.append(ret);ER.append(energy);CH.append(chi)
    model.add_cumulative(riv,[1]*slots,resources[0]);model.add_cumulative(hiv,[1]*slots,resources[1])
    assigns=[];use=[[] for _ in ys];allowed_cache={}
    for i,r in enumerate(routes):
        for c,atom in enumerate(atoms[r['id']]):
            allowed=[sindex[k] for k in atom['sites'] if k in sindex];zz=[]
            if not allowed:model.add(xs[i]==0);continue
            for j in range(slots):
                z=model.new_bool_var(f'z{i}_{c}_{j}');zz.append(z);use[j].append(z)
                model.add(z<=ys[j])
                signature=(j,tuple(sorted(allowed)))
                if signature not in allowed_cache:
                    ok=model.new_bool_var('loc_allowed_'+str(len(allowed_cache)))
                    model.add_allowed_assignments([locs[j]],[[k] for k in allowed]).only_enforce_if(ok)
                    allowed_cache[signature]=ok
                model.add(z<=allowed_cache[signature])
                lo=math.floor(((seedrows[i]['start'] if fixed else 0)+atom['a'])/q+1e-9);hi=ceil_tick((seedrows[i]['start'] if fixed else 0)+atom['b'],q)
                model.add(B[j]<=(0 if fixed else starts[i])+lo).only_enforce_if(z);model.add(F[j]>=(0 if fixed else starts[i])+hi).only_enforce_if(z)
            model.add(sum(zz)==xs[i]);assigns.append((i,c,zz))
    for j in range(slots):model.add(sum(use[j])>=ys[j])
    C=model.new_int_var(0,H,'Cjoint');model.add_max_equality(C,ends+R)
    if max_C is not None:model.add(C<=int(max_C/q))
    tard=[]
    if not fixed:
        for b in P.boxes:
            v=model.new_int_var(0,H,'late'+b);model.add_max_equality(v,[0,cb[b]-int(P.boxes[b]['expected_s']/q)]);tard.append(int(P.boxes[b]['priority'])*v)
    expr={'D':sum(tard),'C':C,'E':sum(math.ceil(r['energy']*1e6-1e-9)*x for r,x in zip(routes,xs))+sum(ER),'N':sum(xs)+sum(ys)}
    if zero_late:model.add(expr['D']==0)
    if max_E is not None:model.add(expr['E']<=math.floor(max_E*1e6+1e-9))
    if max_N is not None:model.add(expr['N']<=max_N)
    if max_transport is not None:model.add(sum(xs)<=max_transport)
    if 'H' in objectives:
        slack=model.new_int_var(-H,H,'hard_slack')
        model.add_min_equality(slack,[int(P.boxes[b]['hard_due']/q)-cb[b] for b in P.boxes if P.boxes[b]['hard_due'] is not None]);expr['H']=-slack
    if warm is not None:
        wr={r['route']['id']:r for r in warm['transport']}
        for i,r in enumerate(routes):
            model.add_hint(xs[i],int(r['id'] in wr))
            if r['id'] in wr:
                v=wr[r['id']];model.add_hint(starts[i],round(v['start']/q))
                for order in v['orders']:
                    for k,b in enumerate(order,1):model.add_hint(ranks[i][b],k)
        for j in range(slots):
            v=next((r for r in warm['relay'] if r['slot']==j),None);model.add_hint(ys[j],int(v is not None))
            if v is not None and v['site']['id'] in sindex:
                model.add_hint(locs[j],sindex[v['site']['id']]);model.add_hint(Y[j],round(v['start']/q));model.add_hint(F[j],round(v['service_end']/q))
    assert not model.validate(),model.validate()
    if complete_warm and warm is not None:
        # Find every auxiliary value for an already known solution without
        # restricting the optimization model; hints remain hints, never bounds.
        hint_model=model.clone();hint_model.clear_hints()
        for i,r in enumerate(routes):
            hint_model.add(xs[i]==int(r['id'] in wr))
            if r['id'] in wr:
                v=wr[r['id']];hint_model.add(starts[i]==round(v['start']/q))
                for order in v['orders']:
                    for k,b in enumerate(order,1):hint_model.add(ranks[i][b]==k)
        for j in range(slots):
            v=next((r for r in warm['relay'] if r['slot']==j),None)
            hint_model.add(ys[j]==int(v is not None))
            if v is not None:
                hint_model.add(locs[j]==sindex[v['site']['id']]);hint_model.add(Y[j]==round(v['start']/q));hint_model.add(F[j]==round(v['service_end']/q))
        hs=cp.CpSolver();hs.parameters.num_search_workers=1;hs.parameters.max_time_in_seconds=min(12,max(.1,deadline-time.monotonic())) if deadline is not None else 12
        hstatus=hs.solve(hint_model)
        dump(directory/'warm_completion.json',dict(status=hs.status_name(hstatus),seconds=hs.wall_time,scope='auxiliary feasibility only, fixes removed from optimization model'))
        if hstatus in (cp.FEASIBLE,cp.OPTIMAL):
            model.clear_hints()
            for i in range(len(model.proto.variables)):
                v=model.get_int_var_from_proto_index(i);model.add_hint(v,hs.value(v))
    def extract_incumbent(reader):
        coverage=[]
        trans=[]
        for i,r in enumerate(routes):
            if not reader.value(xs[i]):continue
            if fixed:tr=copy.deepcopy(seedrows[i])
            else:
                st=reader.value(starts[i])*q
                tr=dict(route=r,start=st,return_=st+r['duration'],battery_ready=st+r['duration']+r['charge'],orders=[sorted(bs,key=lambda b:reader.value(ranks[i][b])) for _,bs in r['stops']],grid_start=st)
                tr['return']=tr.pop('return_')
            tr['sortie']=f'Q3T-{len(trans)+1:03d}';trans.append(tr)
        rel=[]
        for j in range(slots):
            if not reader.value(ys[j]):continue
            site=sites[reader.value(locs[j])-1];st=reader.value(Y[j])*q;finish=reader.value(F[j])*q;readytrue=st+site['ready_offset'];e=site['fly_energy']+1.1*(finish-st-site['arrival_offset'])/3600;ret=finish+site['back'];ch=charge(1-e/3.2,1800)
            rel.append(dict(sortie=f'Q3R-{j+1:03d}',slot=j,site=site,start=st,arrival=st+site['arrival_offset'],link_complete=readytrue,grid_ready=reader.value(B[j])*q,service_end=finish,return_=ret,energy=e,SOC=1-e/3.2,charge=ch,component_ready=ret+ch,aircraft_ready=ret+300))
            rel[-1]['return']=rel[-1].pop('return_')
        best=dict(transport=trans,relay=rel,assignment=coverage,grid_metrics={k:reader.value(v)*(q if k in ('D','C','H') else 1e-6 if k=='E' else 1) for k,v in expr.items()},scope='finite routes/sites/coverage atoms; conservative .1s resource envelopes',fixed_q2=fixed,resources=resources,elapsed=time.time()-beg)
        color(best,P)
        return best
    evidence=[];best=None;progress=[]
    class CB(cp.CpSolverSolutionCallback):
        def __init__(self,stage):super().__init__();self.stage=stage
        def on_solution_callback(self):
            progress.append(dict(stage=self.stage,elapsed_solver_s=self.wall_time,objective=self.objective_value,best_bound=self.best_objective_bound))
            if incumbent_callback is not None:
                observed_at=time.perf_counter()
                incumbent_callback(extract_incumbent(self),dict(found_perf=observed_at,stage=self.stage,objective=self.objective_value,bound=self.best_objective_bound))
            if self.stage=='D' and self.objective_value==0:self.stop_search()
    for stage in objectives:
        if fixed and stage=='D':continue
        if (stop_path is not None and Path(stop_path).exists()) or (deadline is not None and time.monotonic()>=deadline):break
        remaining=seconds if deadline is None else min(seconds,max(.1,deadline-time.monotonic()))
        model.minimize(expr[stage]);solver=cp.CpSolver();solver.parameters.num_search_workers=workers;solver.parameters.random_seed=seed;solver.parameters.max_time_in_seconds=remaining
        solver.parameters.cp_model_presolve=presolve
        finished=threading.Event()
        def watch():
            while not finished.wait(.5):
                if (stop_path is not None and Path(stop_path).exists()) or (deadline is not None and time.monotonic()>=deadline):solver.stop_search();break
        watcher=threading.Thread(target=watch,daemon=True);watcher.start()
        try:status=solver.solve(model,CB(stage))
        finally:finished.set();watcher.join(timeout=1)
        ok=status in (cp.FEASIBLE,cp.OPTIMAL)
        ev=dict(stage=stage,status=solver.status_name(status),objective=solver.objective_value if ok else None,bound=solver.best_objective_bound,seconds=solver.wall_time,branches=solver.num_branches,seed=seed,workers=workers);evidence.append(ev);print(name,ev,flush=True)
        dump(directory/'solver_evidence.json',evidence)
        table(directory/'search_progress.csv',progress)
        if not ok:break
        trans=[]
        for i,r in enumerate(routes):
            if not solver.value(xs[i]):continue
            if fixed:tr=copy.deepcopy(seedrows[i])
            else:
                st=solver.value(starts[i])*q
                tr=dict(route=r,start=st,return_=st+r['duration'],battery_ready=st+r['duration']+r['charge'],orders=[sorted(bs,key=lambda b:solver.value(ranks[i][b])) for _,bs in r['stops']],grid_start=st)
                tr['return']=tr.pop('return_')
            tr['sortie']=f'Q3T-{len(trans)+1:03d}';trans.append(tr)
        rel=[]
        for j in range(slots):
            if not solver.value(ys[j]):continue
            site=sites[solver.value(locs[j])-1];st=solver.value(Y[j])*q;finish=solver.value(F[j])*q;readytrue=st+site['ready_offset'];e=site['fly_energy']+1.1*(finish-st-site['arrival_offset'])/3600;ret=finish+site['back'];ch=charge(1-e/3.2,1800)
            rel.append(dict(sortie=f'Q3R-{j+1:03d}',slot=j,site=site,start=st,arrival=st+site['arrival_offset'],link_complete=readytrue,grid_ready=solver.value(B[j])*q,service_end=finish,return_=ret,energy=e,SOC=1-e/3.2,charge=ch,component_ready=ret+ch,aircraft_ready=ret+300))
            rel[-1]['return']=rel[-1].pop('return_')
        coverage=[dict(route=routes[i]['id'],atom=c,slot=next(j for j,z in enumerate(zs) if solver.value(z))) for i,c,zs in assigns if solver.value(xs[i])]
        best=dict(transport=trans,relay=rel,assignment=coverage,grid_metrics={k:solver.value(v)*(q if k in ('D','C','H') else 1e-6 if k=='E' else 1) for k,v in expr.items()},scope='finite routes/sites/coverage atoms; conservative .1s resource envelopes',fixed_q2=fixed,resources=resources,elapsed=time.time()-beg)
        color(best,P);dump(directory/'solution_q3.json',best)
        dump(directory/'activation_evidence.json',dict(routes=[dict(id=r['id'],selected=bool(solver.value(xs[i])),start=solver.value(starts[i]),end=solver.value(ends[i])) for i,r in enumerate(routes)],relay_slots=[dict(slot=j,enabled=bool(solver.value(ys[j])),location=solver.value(locs[j]),start=solver.value(Y[j]),link=solver.value(B[j]),finish=solver.value(F[j]),return_tick=solver.value(R[j]),energy_micro_kwh=solver.value(ER[j]),charge_ticks=solver.value(CH[j])) for j in range(slots)]))
        model.add(expr[stage]<=solver.value(expr[stage]));model.clear_hints()
        for i in range(len(model.proto.variables)):
            v=model.get_int_var_from_proto_index(i);model.add_hint(v,solver.value(v))
    return best

def color(sol,P):
    for g in P.models:
        group=[r for r in sol['transport'] if r['route']['model']==g]
        for field,end,ids in [('aircraft','return',sorted(k for k,v in P.data['aircraft'].items() if v==g)),('battery','battery_ready',[f'{g}-BAT-{i+1:02d}' for i in range(P.data['K'][g])])]:
            available={k:0. for k in ids}
            for r in sorted(group,key=lambda r:r['start']):
                id=next(k for k,t in available.items() if t<=r['start']+1e-7);r[field]=id;available[id]=r[end]
    for field,end,n,prefix in [('aircraft','aircraft_ready',sol['resources'][0],'R'),('component','component_ready',sol['resources'][1],'R-COMP-')]:
        available={f'{prefix}{i+1:02d}':0. for i in range(n)}
        for r in sorted(sol['relay'],key=lambda r:r['start']):
            id=next(k for k,t in available.items() if t<=r['start']+1e-7);r[field]=id;available[id]=r[end]

