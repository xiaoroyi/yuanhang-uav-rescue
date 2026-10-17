"""Frozen-schedule exact partitioning; Decimal events, Fraction objectives."""
from audit_q4 import *
from fractions import Fraction as F
from itertools import combinations,product
from collections import Counter
import heapq,time,math,copy
D=Decimal
H=['U_A','U_B','U_C','BAT_A','BAT_B','BAT_C','U_R','COMP_R']

class DSU:
    def __init__(self,values):self.p={x:x for x in values}
    def root(self,x):
        while x!=self.p[x]:self.p[x]=self.p[self.p[x]];x=self.p[x]
        return x
    def merge(self,values):
        values=list(values)
        for x in values[1:]:self.p[self.root(x)]=self.root(values[0])
    def groups(self):
        out=defaultdict(list)
        for x in self.p:out[self.root(x)].append(x)
        return sorted(sorted(v) for v in out.values())

def components(sol,ints,pts):
    dest={r['sortie']:sorted(s for s,_ in r['route']['stops']) for r in sol['transport']};V=sorted({s for vv in dest.values() for s in vv});ds=DSU(V)
    edges=[dict(kind='transport',id=t,services=sorted(set(v)),records=[]) for t,v in dest.items()]
    for e in edges:ds.merge(e['services'])
    transport_count=len(ds.groups());clients=defaultdict(set);refs=defaultdict(list)
    for kind,items in [('interval',ints),('event',pts)]:
        for n,r in enumerate(items):
            if r['source']=='G01':continue
            clients[r['source']].add(r['sortie']);refs[r['source']].append(f'{kind}:{n+1}')
    for r in sol['relay']:
        j=r['sortie'];assert clients[j],('orphan relay needs explicit policy',j)
        e=dict(kind='relay',id=j,services=sorted({s for t in clients[j] for s in dest[t]}),transports=sorted(clients[j]),records=refs[j]);edges.append(e);ds.merge(e['services'])
    groups=ds.groups();membership={s:n for n,g in enumerate(groups) for s in g}
    atoms=[dict(id=f'C{n+1}',services=g,transport=[t for t,v in dest.items() if membership[v[0]]==n],relay=[e['id'] for e in edges if e['kind']=='relay' and membership[e['services'][0]]==n]) for n,g in enumerate(groups)]
    # Independent bipartite graph flood fill.
    graph=defaultdict(set)
    for e in edges:
        node=e['kind']+':'+e['id']
        for s in e['services']:graph[s].add(node);graph[node].add(s)
    unseen=set(graph);bfs=[]
    while unseen:
        seen=set();todo=[next(iter(unseen))]
        while todo:
            x=todo.pop()
            if x in seen:continue
            seen.add(x);todo.extend(graph[x]-seen)
        unseen-=seen;bfs.append(sorted(x for x in seen if x in V))
    assert sorted(bfs)==groups
    strict=DSU(V)
    for e in edges:strict.merge(e['services'])
    identities=defaultdict(set)
    rd={e['id']:e['services'] for e in edges if e['kind']=='relay'}
    for kind,key in [('transport','aircraft'),('transport','battery'),('relay','aircraft'),('relay','component')]:
        for r in sol[kind]:identities[(kind,key,r[key])].update(dest[r['sortie']] if kind=='transport' else rd[r['sortie']])
    identity_edges=[]
    for key,ss in identities.items():strict.merge(ss);identity_edges.append(dict(identity=key,services=sorted(ss)))
    result=dict(atoms=atoms,edges=edges,transport_only_components=transport_count,bfs_matches=True,strict_original_identity_components=strict.groups(),identity_edges=identity_edges)
    return result

def charge(E,use,T):
    soc=1-E/use
    return D(T)*(D('.65')*(D('.9')-soc)/D('.9')+D('.35')) if soc<D('.9') else D(T)*D('.35')*(1-soc)/D('.1')

def intervals(sol,data):
    out=[];mismatch=[]
    for r in sol['transport']:
        g=r['route']['model'];e=D(str(r['route']['energy']));use=D(str(data['models'][g]['Euse']));ch=charge(e,use,data['Tfull'][g]);ready=r['return']+ch
        mismatch.append(abs(ready-r['battery_ready']));assert mismatch[-1]<D('0.000002')
        for h,end,ident in [('U_'+g,r['return'],r['aircraft']),('BAT_'+g,r['battery_ready'],r['battery'])]:out.append(dict(task=r['sortie'],resource=h,start=r['start'],end=end,original_id=ident,kind='transport'))
    for r in sol['relay']:
        ch=charge(r['energy'],D(str(data['relay']['Euse'])),data['relay']['Tfull']);mismatch.append(abs(r['return']+ch-r['component_ready']));assert mismatch[-1]<D('0.000002')
        assert abs(r['return']+D(str(data['relay']['turn']))-r['aircraft_ready'])<D('0.000002')
        for h,key,ident in [('U_R','aircraft_ready',r['aircraft']),('COMP_R','component_ready',r['component'])]:out.append(dict(task=r['sortie'],resource=h,start=r['start'],end=r[key],original_id=ident,kind='relay'))
    return out,max(mismatch)

def sweep(items):
    events=[]
    for i,r in enumerate(items):
        assert r['end']>r['start'];events.extend([(r['start'],1,i),(r['end'],-1,i)])
    active=set();best=set();when=None
    for t,sign,i in sorted(events):
        if sign<0:active.remove(i)
        else:active.add(i)
        if len(active)>len(best):best=active.copy();when=t
    return dict(count=len(best),time=when,tasks=sorted(items[i]['task'] for i in best),intervals=[items[i] for i in sorted(best)])

def color(items):
    heap=[];n=0;assigned=[]
    for r in sorted(items,key=lambda x:(x['start'],x['end'],x['task'])):
        if heap and heap[0][0]<=r['start']:_,idx=heapq.heappop(heap)
        else:n+=1;idx=n
        heapq.heappush(heap,(r['end'],idx));assigned.append(dict(**r,color=idx))
    for idx in range(1,n+1):
        seq=sorted((r['start'],r['end']) for r in assigned if r['color']==idx)
        assert all(b<=c for (a,b),(c,d) in zip(seq,seq[1:]))
    return n,assigned

def rgs(n,k):
    if n==0:return
    def rec(a):
        if len(a)==n:
            if max(a)+1==k:yield a
            return
        for v in range(min(k-1,max(a)+1)+1):yield from rec(a+[v])
    yield from rec([0])

def metrics(groups,stock,scale=None,work='W'):
    scale=scale or stock;N=[sum(g['N'][i] for g in groups) for i in range(8)];gap=[max(0,n-i) for n,i in zip(N,stock)];W=[F(g[work]) for g in groups];tot=sum(W)
    cv=len(W)*sum(w*w for w in W)/(tot*tot)-1
    return dict(N=N,gap=gap,Jgap=sum((F(d,i) for d,i in zip(gap,scale)),F(0)),Jsize=sum((F(n,i) for n,i in zip(N,scale)),F(0)),CV2=cv,max_deviation=max(abs(len(W)*w/tot-1) for w in W),W=W)

def precompute(atoms,iv,sol,data):
    ts={r['sortie']:r for r in sol['transport']};rs={r['sortie']:r for r in sol['relay']};subsets={};horizon=max(r['end'] for r in iv)
    for mask in range(1,1<<len(atoms)):
        group=[a for i,a in enumerate(atoms) if mask>>i&1];tids={t for a in group for t in a['transport']};rids={t for a in group for t in a['relay']};ids=tids|rids
        witnesses={h:sweep([r for r in iv if r['task'] in ids and r['resource']==h]) for h in H};assign=[]
        for h in H:
            count,colored=color([r for r in iv if r['task'] in ids and r['resource']==h]);assert count==witnesses[h]['count'];assign.extend(colored)
        wt=sum((ts[t]['return']-ts[t]['start'] for t in tids),D(0));wr=sum((rs[t]['return']-rs[t]['start'] for t in rids),D(0));boxes=[b for t in tids for b in ts[t]['route']['boxes']]
        N=[witnesses[h]['count'] for h in H];busy=[sum((r['end']-r['start'] for r in iv if r['task'] in ids and r['resource']==h),D(0)) for h in H]
        subsets[mask]=dict(mask=mask,atoms=[a['id'] for a in group],services=sorted(s for a in group for s in a['services']),transport=sorted(tids),relay=sorted(rids),N=N,W=wt+wr,Wtransport=wt,Wturn=wt+wr+len(rids)*D(str(data['relay']['turn'])),Wrelay=wr,boxes=len(boxes),mass=sum(ts[t]['route']['mass'] for t in tids),volume_L=sum(ts[t]['route']['volume'] for t in tids),energy=sum((ts[t]['route']['energy'] for t in tids),D(0))+sum((rs[t]['energy'] for t in rids),D(0)),busy=busy,utilization=[float(b/(n*horizon)) if n else None for n,b in zip(N,busy)],witnesses=witnesses,assignment=assign)
    return subsets,horizon

def enumerate_all(subsets,n,stock):
    out=[]
    for k in (2,3):
        for seq in rgs(n,k):
            masks=[sum(1<<i for i,v in enumerate(seq) if v==g) for g in range(k)];groups=[subsets[a] for a in masks];m=metrics(groups,stock);out.append(dict(id=f'K{k}-{sum(r["K"]==k for r in out)+1:02d}',K=k,masks=masks,partition='/'.join('+'.join(g['atoms']) for g in groups),**m))
    for p in out:
        peers=[q for q in out if q['K']==p['K'] and q['id']!=p['id']];v=p['N']+[p['CV2']]
        p['pareto']=not any(all(a<=b for a,b in zip(q['N']+[q['CV2']],v)) and any(a<b for a,b in zip(q['N']+[q['CV2']],v)) for q in peers)
    return out

def key(p,mode='resource'):
    return (p['Jgap'],p['Jsize'],p['CV2'],p['partition']) if mode=='resource' else (p['CV2'],p['Jgap'],p['Jsize'],p['partition'])

def milp_verify(subsets,n,stock,parts):
    import numpy as np
    from scipy.optimize import milp,Bounds,LinearConstraint
    masks=sorted(subsets);m=len(masks);nv=m+8;lcm=math.lcm(*stock);logs=[]
    for k in (2,3):
        A=[];lo=[];hi=[]
        for a in range(n):A.append([int(mask>>a&1) for mask in masks]+[0]*8);lo.append(1);hi.append(1)
        A.append([1]*m+[0]*8);lo.append(k);hi.append(k)
        for h in range(8):A.append([subsets[mask]['N'][h] for mask in masks]+[-int(j==h) for j in range(8)]);lo.append(-np.inf);hi.append(stock[h])
        objs=[];objs.append([0]*m+[lcm//i for i in stock]);objs.append([sum(subsets[a]['N'][h]*lcm//stock[h] for h in range(8)) for a in masks]+[0]*8)
        # Total work is fixed; scale W² to hours² for stable LP coefficients.
        objs.append([float(subsets[a]['W']/3600)**2 for a in masks]+[0]*8)
        for stage,c in enumerate(objs):
            result=milp(np.array(c),integrality=np.ones(nv),bounds=Bounds([0]*nv,[1]*m+[np.inf]*8),constraints=LinearConstraint(np.array(A,float),np.array(lo),np.array(hi)),options={'mip_rel_gap':0})
            assert result.success,result.message
            selected=[a for j,a in enumerate(masks) if result.x[j]>.5];v=metrics([subsets[a] for a in selected],stock)
            optimum=min((key(p)[:stage+1] for p in parts if p['K']==k))
            assert key(v|{'partition':''})[:stage+1]==optimum,(stage,v,optimum)
            logs.append(dict(K=k,stage=stage+1,status=result.message,objective=float(result.fun),dual_bound=float(result.mip_dual_bound),gap=float(result.mip_gap),selected=selected,exact_enumeration_agrees=True))
            if stage<2:A.append(c);lo.append(round(result.fun));hi.append(round(result.fun))
    return logs

def ownership(groups,ints,pts):
    taskgroup={t:i+1 for i,g in enumerate(groups) for t in g['transport']+g['relay']};out=[]
    for kind,items in [('interval',ints),('event',pts)]:
        for n,r in enumerate(items):
            source=r['source'];t=r['sortie'];assert t in taskgroup
            assert source=='G01' or (source in taskgroup and taskgroup[source]==taskgroup[t]),r
            out.append(dict(record=f'{kind}:{n+1}',transport=t,phase=r['phase'],start=r.get('start',r.get('time')),end=r.get('end',r.get('time')),left_closed=kind=='event',right_closed=kind=='event',source=source,transport_group=taskgroup[t],relay_group=taskgroup.get(source),certificate_file='communication_certificates.jsonl' if kind=='interval' else 'communication_event_points_q3.csv'))
    return out

def main():
    beg=time.time();sol=read(Q3/'solution_q3.json');ints=rows(Q3/'communication_intervals_q3.csv');pts=rows(Q3/'communication_event_points_q3.csv');data=inputs()
    # Relay stock extracted from actual ID rows and energy-component table, independently of setup defaults.
    from openpyxl import load_workbook
    raw=next((PROJECT.parent/'D题').rglob('中继无人机数据.xlsx'));wb=load_workbook(raw,data_only=True);rr=list(wb['数据'].values);wb.close()
    relay_ids=sorted({r[0] for r in rr if isinstance(r[0],str) and r[0].startswith('R0')});assert relay_ids
    krelay=next(r[1] for r in rr if r[0]=='R' and r[1:3]==(6,1800))
    stock=[data['M'][g] for g in 'ABC']+[data['K'][g] for g in 'ABC']+[len(relay_ids),krelay]
    comp=components(sol,ints,pts);atoms=comp['atoms'];iv,charge_error=intervals(sol,data);subsets,horizon=precompute(atoms,iv,sol,data);parts=enumerate_all(subsets,len(atoms),stock)
    pool=subsets[(1<<len(atoms))-1];assert len(parts)>0
    dump(OUT/'components_q4.json',comp);table(OUT/'resource_intervals_q4.csv',iv);dump(OUT/'group_subsets_q4.json',subsets);table(OUT/'all_partitions_q4.csv',parts);table(OUT/'pareto_q4.csv',[p for p in parts if p['pareto']]);milp=milp_verify(subsets,len(atoms),stock,parts)
    assignments=[];coverage=[];decomp=[];work=[];witness=[];solutions={}
    for k in (2,3):
        chosen=min((p for p in parts if p['K']==k),key=key);balanced=min((p for p in parts if p['K']==k),key=lambda p:key(p,'balance'));groups=[subsets[a] for a in chosen['masks']]
        for gno,g in enumerate(groups,1):
            work.append(dict(K=k,group=gno,**{x:g[x] for x in ('services','W','Wtransport','Wrelay','Wturn','boxes','mass','volume_L','energy','N','busy','utilization')}))
            for h in H:witness.append(dict(K=k,group=gno,resource=h,**g['witnesses'][h]))
        for hi,h in enumerate(H):
            allocated=0
            for gno,g in enumerate(groups,1):
                mapping={color:allocated+color for color in range(1,g['N'][hi]+1)};allocated+=g['N'][hi]
                for r in g['assignment']:
                    if r['resource']!=h:continue
                    ordinal=mapping[r['color']];extra=ordinal>stock[hi];global_id=f'{h}-'+('ADD-' if extra else 'STOCK-')+f'{ordinal-stock[hi] if extra else ordinal:02d}'
                    assignments.append(dict(K=k,group=gno,**r,new_id=global_id,group_local_id=f'K{k}-G{gno}-{h}-{r["color"]:02d}',needs_addition=extra))
            decomp.append(dict(K=k,resource=h,stock=stock[hi],pooled=pool['N'][hi],partition_total=chosen['N'][hi],additional_vs_pool=chosen['N'][hi]-pool['N'][hi],deficit=chosen['gap'][hi],unallocated_stock=max(0,stock[hi]-chosen['N'][hi]),busy_seconds=pool['busy'][hi],horizon=horizon,utilization=float(pool['busy'][hi]/(chosen['N'][hi]*horizon))))
        coverage.extend(dict(K=k,**r) for r in ownership(groups,ints,pts))
        solutions[k]=dict(selected=chosen,balanced=balanced,groups=[{x:v for x,v in g.items() if x not in ('assignment','witnesses')} for g in groups],status='补足指定资源后可按原时序独立执行',Q3_task_hash=sha(Q3/'solution_q3.json'))
        dump(OUT/f'solution_k{k}.json',solutions[k])
    table(OUT/'group_resource_assignment.csv',assignments);table(OUT/'coverage_ownership_q4.csv',coverage);table(OUT/'deficit_decomposition.csv',decomp);table(OUT/'group_workload.csv',work);dump(OUT/'resource_peak_witnesses.json',witness)
    # Every legal partition inherits physical fields and actual ownership, not only the selected two.
    for p in parts:ownership([subsets[a] for a in p['masks']],ints,pts)
    allboxes=[b for r in sol['transport'] for b in r['route']['boxes']];assert len(allboxes)==len(set(allboxes))==80
    assert pool['mass']==758 and pool['volume_L']==2011
    summary=dict(atoms=len(atoms),partitions={k:sum(p['K']==k for p in parts) for k in (2,3)},stock=stock,pooled=pool['N'],pooled_W=pool['W'],horizon=horizon,max_charge_recompute_error=charge_error,strict_identity_components=len(comp['strict_original_identity_components']),any_partition_within_inventory={k:any(not any(p['gap']) for p in parts if p['K']==k) for k in (2,3)},milp=milp,source_task_hash=sha(Q3/'solution_q3.json'),elapsed_seconds=time.time()-beg,resource_order=H)
    dump(OUT/'run_summary.json',summary);print(json.dumps({'summary':summary,'solutions':{k:{a:v for a,v in x.items() if a!='groups'} for k,x in solutions.items()}},ensure_ascii=False,default=default),flush=True)
    return sol,comp,iv,subsets,parts,stock

if __name__=='__main__':main()
