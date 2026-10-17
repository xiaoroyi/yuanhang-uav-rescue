"""Independent event reconstruction. No candidate evaluator, scheduler or decoder imports."""
import env
from env import OUT
from prepare import load
from data_io import dump,table
from collections import Counter,defaultdict
import math,json

def peak(intervals):
    # Collapse only floating arithmetic noise at the stated microsecond tolerance.
    events=sorted([(round(s,6),1) for s,e in intervals]+[(round(e,6),-1) for s,e in intervals])
    n=ans=0
    for _,delta in events:n+=delta;ans=max(ans,n)
    return ans

def check(rows,save=None,M=None,K=None,energy_scale=1.,flight_scale=1.,horizontal_scale=1.,rho=.2,subset=None,data=None,compare_reported=True):
    data=data or load();boxes={b['id']:b for b in data['boxes']};M=M or data['M'];K=K or data['K']
    errors=[];warnings=[];seen=[];deliveries=[];legs=[];stops=[];sorties=[];air=defaultdict(list);bat=defaultdict(list)
    geo={tuple(sorted((r['start'],r['end']))):r for r in json.loads((OUT/'terrain_evidence_all.json').read_text(encoding='utf-8'))['legs']}
    def require(condition,code,detail):
        if not condition:errors.append(dict(code=code,detail=detail))
    def close(a,b,code,detail):require(abs(a-b)<=2e-6,code,dict(detail=detail,expected=a,reported=b))
    for row in rows:
        r=row['route'];typ=r['model'];m=data['models'][typ];rid=row['sortie'];uid=row['aircraft'];bid=row['battery'];S=row['start']
        require(S>=-1e-9,'negative_start',rid)
        validids=set(k for k,v in data['aircraft'].items() if v==typ)
        if M[typ]>data['M'][typ]:validids.update(f'{typ}-EXTRA-{i}' for i in range(1,M[typ]-data['M'][typ]+1))
        require(uid in validids,'aircraft_id',rid)
        require(bid in {f'{typ}-BAT-{j:02d}' for j in range(1,K[typ]+1)},'battery_type_or_id',rid)
        ids=[b for _,bs in r['stops'] for b in bs];seen.extend(ids)
        require(bool(ids) and len(ids)==len(set(ids)),'route_duplicate_or_empty',rid)
        if any(b not in boxes for b in ids):errors.append(dict(code='unknown_box',detail=rid));continue
        q=sum(boxes[b]['weight'] for b in ids);volume=sum(boxes[b]['volume_L'] for b in ids);initial=q
        require(q<=m['Q'],'over_mass',rid);require(volume<=m['volume_L'],'over_volume',rid)
        prep=m['prep']+m['load']*len(ids);takeoff=S+prep;t=takeoff;energy=0.;flight=0.;handover=0.;a='O01'
        for j,(dest,bs) in enumerate(list(r['stops'])+[('O01',[]) ]):
            require(a!=dest,'zero_leg',rid)
            if a==dest:continue
            g=geo[tuple(sorted((a,dest)))];H=g['cruise_m'];d=g['distance_m']
            za=data['nodes'][a]['z']+(30 if a!='O01' else 0);zb=data['nodes'][dest]['z']+(30 if dest!='O01' else 0)
            climb=H-za;desc=H-zb;require(min(climb,desc)>=0,'negative_climb',rid)
            t0=t;tup=flight_scale*climb/m['up'];th=flight_scale*d/m['speed'];td=flight_scale*desc/m['down']
            L=m['L0']-(m['L0']-m['LF'])*math.pow(q/m['Q'],1.5)
            eh=energy_scale*horizontal_scale*m['Euse']*d/L;eu=energy_scale*(m['m0']+q)*9.81*climb/(m['eta']*3600000)
            energy+=eh+eu;flight+=tup+th+td;t+=tup+th+td
            legs.append(dict(sortie=rid,leg_index=j+1,origin=a,destination=dest,payload_kg=q,cruise_m=H,distance_m=d,climb_start=t0,cruise_start=t0+tup,descent_start=t0+tup+th,leg_end=t,horizontal_kwh=eh,climb_kwh=eu,SOC_end=1-energy/m['Euse']))
            if dest!='O01':
                require(bool(bs),'empty_visit',rid)
                require(all(boxes[b]['service']==dest for b in bs),'wrong_destination',rid)
                order=row['orders'][j] if j<len(row['orders']) else []
                require(Counter(order)==Counter(bs),'invalid_box_order',rid)
                arrival=t;base=t+m['handover'];handover+=m['handover']+m['handover_box']*len(bs)
                for k,b in enumerate(order,1):
                    if b not in boxes:continue
                    box=boxes[b];C=base+k*m['handover_box'];hard=box['hard_due'];late=max(0,C-box['expected_s'])
                    require(hard is None or C<=hard+1e-6,'hard_deadline',dict(box=b,complete=C,due=hard))
                    deliveries.append(dict(box= b,sortie=rid,service=dest,visit_index=j+1,local_rank=k,category=box['category'],weight_kg=box['weight'],volume_L=box['volume_L'],first=box['first'],priority=box['priority'],hard_due=hard,expected_s=box['expected_s'],arrival=arrival,base_handover_end=base,complete=C,hard_slack=None if hard is None else hard-C,tardiness=late,weighted_tardiness=box['priority']*late))
                t=base+m['handover_box']*len(bs);stops.append(dict(sortie=rid,visit=j+1,service=dest,arrival=arrival,base_end=base,departure=t,boxes=order))
                q-=sum(boxes[b]['weight'] for b in bs)
            a=dest
        require(q==0,'nonempty_return',rid)
        soc=1-energy/m['Euse'];require(soc>=rho-1e-10,'energy_reserve',dict(sortie=rid,soc=soc))
        full=data['Tfull'][typ]
        charging=full*(.65*(.9-soc)/.9+.35) if soc<.9 else full*.35*(1-soc)/.1
        ready=t+charging
        if compare_reported:
            close(t,row['return'],'return_time',rid);close(ready,row['battery_ready'],'battery_ready',rid)
            close(energy,r['energy'],'energy_value',rid);close(t-S,r['duration'],'duration_value',rid)
        air[uid].append((S,t,rid,typ));bat[bid].append((S,ready,rid,typ,t,soc,charging))
        sorties.append(dict(sortie=rid,route_id=r['id'],model=typ,aircraft=uid,battery=bid,boxes=ids,stops=r['stops'],mass_kg=initial,volume_L=volume,start=S,takeoff=takeoff,return_s=t,prep_s=prep,pure_flight_s=flight,handover_s=handover,energy_kwh=energy,SOC=soc,charge_duration=charging,battery_ready=ready))
    wanted=set(subset or boxes)
    require(Counter(seen)==Counter({b:1 for b in wanted}),'coverage',dict(missing=sorted(wanted-set(seen)),duplicates=[b for b,n in Counter(seen).items() if n>1],extra=sorted(set(seen)-wanted)))
    for name,groups in [('aircraft',air),('battery',bat)]:
        for ident,events in groups.items():
            ordered=sorted(events)
            for prev,nxt in zip(ordered,ordered[1:]):require(prev[1]<=nxt[0]+1e-6,name+'_overlap',dict(id=ident,previous=prev[2],next=nxt[2],available=prev[1],start=nxt[0]))
    up={g:peak([(r['start'],r['return_s']) for r in sorties if r['model']==g]) for g in data['models']}
    bp={g:peak([(r['start'],r['battery_ready']) for r in sorties if r['model']==g]) for g in data['models']}
    for g in data['models']:require(up[g]<=M[g],'aircraft_capacity',g);require(bp[g]<=K[g],'battery_capacity',g)
    hard=[d for d in deliveries if d['hard_due'] is not None];nonmed=[d for d in deliveries if d['category']!='MED']
    summary=dict(valid=not errors,errors=len(errors),boxes=len(seen),unique_boxes=len(set(seen)),mass_kg=sum(boxes[b]['weight'] for b in seen),volume_L=sum(boxes[b]['volume_L'] for b in seen),D=sum(d['weighted_tardiness'] for d in deliveries),Cmax=max((r['return_s'] for r in sorties),default=0),E=sum(r['energy_kwh'] for r in sorties),N=len(rows),by_model=dict(Counter(r['model'] for r in sorties)),min_SOC=min((r['SOC'] for r in sorties),default=1),min_hard_slack=min((r['hard_slack'] for r in hard),default=None),hard_boxes=len(hard),hard_violations=sum(d['hard_slack']< -1e-6 for d in hard),on_time_rate=sum(d['tardiness']<=1e-6 for d in deliveries)/max(1,len(deliveries)),nonmedical_on_time_rate=sum(d['tardiness']<=1e-6 for d in nonmed)/max(1,len(nonmed)),weighted_mean_delivery=sum(d['priority']*d['complete'] for d in deliveries)/max(1,sum(d['priority'] for d in deliveries)),aircraft_peak=up,battery_peak=bp,multi_stop_sorties=sum(len(r['stops'])>1 for r in sorties),max_stops=max((len(r['stops']) for r in sorties),default=0))
    result=dict(summary=summary,errors=errors,warnings=warnings)
    if save:
        save.mkdir(exist_ok=True,parents=True);dump(save/'validation.json',result);dump(save/'solution.json',rows)
        for name,values in [('sorties',sorties),('deliveries',deliveries),('leg_events',legs),('stop_events',stops)]:table(save/f'{name}.csv',values)
        table(save/'aircraft_timeline.csv',[dict(aircraft=k,start=e[0],end=e[1],sortie=e[2],model=e[3]) for k,es in air.items() for e in sorted(es)])
        batteryrows=[]
        for k,es in bat.items():
            for i,e in enumerate(sorted(es)):
                ss=sorted(es);nxt=ss[i+1][0] if i+1<len(ss) else None
                batteryrows.append(dict(battery=k,model=e[3],sortie=e[2],reservation=e[0],return_s=e[4],SOC_start=1,SOC_return=e[5],charging_start=e[4],charging_end=e[1],next_use=nxt,full_wait=None if nxt is None else nxt-e[1]))
        table(save/'battery_timeline.csv',batteryrows)
    return result

if __name__=='__main__':
    import sys
    from pathlib import Path
    p=Path(sys.argv[1]);res=check(json.loads(p.read_text(encoding='utf-8')));print(json.dumps(res,ensure_ascii=False,indent=2));sys.exit(not res['summary']['valid'])
