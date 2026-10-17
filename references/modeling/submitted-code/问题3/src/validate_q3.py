"""Reconstruct transport from raw inputs; relay physics and full-time coverage audit."""
from setup_q3 import *
from communication import Radio,phases
from routes import Physics
from validate import check,peak
from sites import relay_metrics
import math,csv,time
from collections import defaultdict

def state(prof,u,endpoint=False):
    if endpoint and any(abs(u-v)<1e-10 for v in prof['events']):return False
    return any(lo-1e-12<=u<=hi+1e-12 and ok for lo,hi,ok in prof['pieces'])

def independent_ray(engine,a,p):
    """GEOS line/pixel intersection, independent of lambda-polygon clipping."""
    import shapely
    a=np.array(a);p=np.array(p);v=p-a;vs,hs=engine.cells(a,p,p)
    line=shapely.LineString([a[:2],p[:2]]) if np.linalg.norm(v[:2])>1e-10 else shapely.Point(a[:2])
    polys=shapely.polygons(vs)
    if engine.pad:polys=shapely.buffer(polys,engine.pad,join_style='mitre')
    hits=shapely.intersects(polys,line);ids=np.flatnonzero(hits)
    for k in ids:
        cut=shapely.intersection(polys[k],line);xy=shapely.get_coordinates(cut)
        if np.dot(v[:2],v[:2])<1e-20:z=min(a[2],p[2])
        else:
            u=(xy-a[:2])@v[:2]/np.dot(v[:2],v[:2]);z=float(np.min(a[2]+u*v[2]))
        if z<=hs[k]+1e-7:return True
    return False

def run(path,margin=8,obstacle=10,save=True):
    path=Path(path);sol=json.loads(path.read_text(encoding='utf-8'));directory=path.parent;data=inputs();P=Physics();engine=Radio(data,margin=margin,obstacle=obstacle);beg=time.time()
    transport=check(sol['transport'],data=data,save=directory/'transport_validation' if save else None);errors=list(transport['errors']);relays=[];timelines=[];cross=[]
    def req(ok,code,detail):
        if not ok:errors.append(dict(code=code,detail=detail))
    for r in sol['relay']:
        site=r['site'];m=relay_metrics(data,site['lon'],site['lat'],site['agl']);p=np.array([m['x'],m['y'],m['z']]);back=engine.point(data['gateway'],p,'backhaul')
        req(0<site['agl']<=300,'height',r['sortie']);req(back['valid'],'backhaul',dict(sortie=r['sortie'],**back));req(r['start']>=0,'negative_start',r['sortie'])
        link=r['start']+180+m['out']+30;end=r['service_end'];ret=end+m['back'];e=m['fly_energy']+1.1*(end-r['start']-180-m['out'])/3600;soc=1-e/3.2
        ch=1800*(.65*(.9-soc)/.9+.35) if soc<.9 else 1800*.35*(1-soc)/.1
        req(end>=link-1e-8,'relay_before_link',r['sortie']);req(e<=2.56+1e-9,'relay_energy',r['sortie'])
        for actual,key in [(r['start']+180+m['out'],'arrival'),(link,'link_complete'),(ret,'return'),(e,'energy'),(soc,'SOC'),(ch,'charge'),(ret+ch,'component_ready'),(ret+300,'aircraft_ready')]:req(abs(actual-r[key])<2e-6,'relay_value_'+key,r['sortie'])
        for key in ('x','y','z','ground','cruise','out','back','fly_energy'):
            req(abs(site[key]-m[key])<2e-6,'relay_site_'+key,r['sortie'])
        req(r['aircraft'] in [f'R{i+1:02d}' for i in range(sol['resources'][0])],'relay_id',r['sortie']);req(r['component'] in [f'R-COMP-{i+1:02d}' for i in range(sol['resources'][1])],'component_id',r['sortie'])
        relays.append(dict(**r,xyz=p.tolist(),backhaul_margin=back['margin']))
        for group,identity,last in [('relay',r['aircraft'],ret+300),('component',r['component'],ret+ch)]:timelines.append(dict(resource=group,id=identity,sortie=r['sortie'],start=r['start'],end=last))
        independent=independent_ray(engine,data['gateway'],p);cross.append(dict(kind='backhaul',sortie=r['sortie'],same=independent==back['blocked']));req(cross[-1]['same'],'independent_geometry',cross[-1])
    for typ,stock in [('relay',sol['resources'][0]),('component',sol['resources'][1])]:
        group=[r for r in timelines if r['resource']==typ];req(peak([(r['start'],r['end']) for r in group])<=stock,typ+'_capacity',stock)
        for ident in set(r['id'] for r in group):
            events=sorted((r['start'],r['end']) for r in group if r['id']==ident)
            req(all(b<=c+1e-6 for (a,b),(c,d) in zip(events,events[1:])),typ+'_overlap',ident)
    intervals=[];points=[];fails=[];margin_rows=[]
    for row in sol['transport']:
        for p in phases(row['route'],P):
            start=row['start']+p['a'];end=row['start']+p['b'];dt=end-start
            direct=engine.profile(data['gateway'],p['p0'],p['p1'],'direct');links={'G01':direct};active={};fixed={'G01':data['gateway']}
            cuts={0.,1.}
            for relay in relays:
                if relay['backhaul_margin'] < -1e-8:continue
                if relay['service_end']<start or relay['link_complete']>end:continue
                rid=relay['sortie'];links[rid]=engine.profile(relay['xyz'],p['p0'],p['p1'],'access');fixed[rid]=relay['xyz'];active[rid]=(relay['link_complete'],relay['service_end'])
                for t in active[rid]:
                    if start<t<end:cuts.add((t-start)/dt)
            for prof in links.values():
                for lo,hi,_ in prof['pieces']:cuts.update((lo,hi))
                cuts.update(prof['events'])
            cuts=sorted(cuts)
            def source(u,at_point=False):
                if state(direct,u,at_point):return 'G01'
                t=start+dt*u
                for rid in active:
                    if active[rid][0]-1e-8<=t<=active[rid][1]+1e-8 and state(links[rid],u,at_point):return rid
                return None
            for lo,hi in zip(cuts,cuts[1:]):
                mid=(lo+hi)/2;rid=source(mid);ta=start+dt*lo;tb=start+dt*hi
                if rid is None:fails.append(dict(sortie=row['sortie'],phase=p['phase'],start=ta,end=tb));continue
                prof=links[rid];kind='direct' if rid=='G01' else 'access';x0=np.array(p['p0'])+lo*(np.array(p['p1'])-p['p0']);x1=np.array(p['p0'])+hi*(np.array(p['p1'])-p['p0']);anchor=np.array(fixed[rid]);dmax=max(np.linalg.norm(x0-anchor),np.linalg.norm(x1-anchor));blocked=any(a<=mid<=b for a,b in prof['blocked'])
                if prof['radius_certified'] and not prof['blocked']:blocked=True # worst-case bound valid regardless of actual terrain
                worst=engine.limits[kind]-(engine.base+20*math.log10(max(dmax,1e-9))+engine.obstacle*blocked)
                req(worst>=-1e-6,'interval_budget',dict(sortie=row['sortie'],margin=worst))
                intervals.append(dict(sortie=row['sortie'],phase=p['phase'],stage=p['type'],start=ta,end=tb,source=rid,state='direct' if rid=='G01' else 'relay',min_margin_bound_db=worst,endpoint_rule='open interval; all event points checked separately'))
                margin_rows.append((worst,anchor.tolist(),((x0+x1)/2).tolist(),kind))
            for u in cuts:
                rid=source(u,True);req(rid is not None,'isolated_uncovered_point',dict(sortie=row['sortie'],phase=p['phase'],time=start+dt*u))
                points.append(dict(sortie=row['sortie'],phase=p['phase'],time=start+dt*u,source=rid))
    req(not fails,'communication_gaps',fails[:8])
    for _,anchor,p,kind in sorted(margin_rows,key=lambda v:v[0])[:60]:
        primary=bool(engine.blocked(anchor,p,p));secondary=independent_ray(engine,anchor,p);cross.append(dict(kind=kind,same=primary==secondary));req(primary==secondary,'independent_ray',dict(anchor=anchor,point=p))
    st=transport['summary'];summary=dict(valid=not errors,errors=len(errors),D=st['D'],C_joint=max([r['return'] for r in sol['transport']]+[r['return'] for r in sol['relay']]),C_transport=max(r['return'] for r in sol['transport']),C_relay=max((r['return'] for r in sol['relay']),default=0),E_transport=st['E'],E_relay=sum(r['energy'] for r in relays),E_total=st['E']+sum(r['energy'] for r in relays),N_transport=len(sol['transport']),N_relay=len(relays),hard_violations=st['hard_violations'],min_hard_slack=st['min_hard_slack'],min_transport_SOC=st['min_SOC'],min_relay_SOC=min((r['SOC'] for r in relays),default=1),certified_open_intervals=len(intervals),certified_event_points=len(points),gap_seconds=sum(r['end']-r['start'] for r in fails),unknown_intervals=0,min_active_margin_bound=min((r['min_margin_bound_db'] for r in intervals),default=0),direct_customer_seconds=sum(r['end']-r['start'] for r in intervals if r['source']=='G01'),relay_customer_seconds=sum(r['end']-r['start'] for r in intervals if r['source']!='G01'),independent_ray_checks=len(cross),elapsed=time.time()-beg,geometry_scope='frozen original-height projected convex quadrilaterals + 2 mm footprint buffer; finite precision, full temporal intervals, independent GEOS ray checks')
    report=dict(summary=summary,errors=errors,geometry_cross_checks=cross)
    if save:
        dump(directory/'validation_q3.json',report);dump(directory/'solution_summary.json',summary);table(directory/'communication_intervals_q3.csv',intervals);table(directory/'communication_event_points_q3.csv',points);table(directory/'relay_trips_q3.csv',[{k:v for k,v in r.items() if k not in ('site','xyz')}|r['site'] for r in relays]);table(directory/'relay_resource_timeline.csv',timelines)
    print(json.dumps(summary,ensure_ascii=False),flush=True)
    return report

if __name__=='__main__':run(sys.argv[1])
