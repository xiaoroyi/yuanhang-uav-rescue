from communication import Radio,phases,profile_bad_intervals
from setup_q3 import *
from terrain import route_points,supercover_segment
import math,time

def relay_metrics(data,lon,lat,agl):
    r=data['relay'];nr,nc=data['dem'].shape
    c=int(math.floor((lon-data['lon'][0])/(data['lon'][1]-data['lon'][0])+.5));row=int(math.floor((data['lat'][0]-lat)/(data['lat'][0]-data['lat'][1])+.5))
    if not (0<=row<nr and 0<=c<nc):return None
    ground=float(data['dem'][row,c]);z=ground+agl;x,y=FORWARD.transform(lon,lat);o=data['nodes']['O01'];dist=math.hypot(x-o['xy'][0],y-o['xy'][1])
    _,pts,_=route_points(data,o,dict(lon=lon,lat=lat),10.)
    cells=set()
    for a,b in zip(pts,pts[1:]):cells.update(supercover_segment(a,b))
    H=max(z,o['z'],max(float(data['dem'][rr,cc]) for rr,cc in cells)+50)
    out=(H-o['z'])/r['up']+dist/r['speed']+(H-z)/r['down'];back=(H-z)/r['up']+dist/r['speed']+(H-o['z'])/r['down']
    fly=r['cruise_power']*2*dist/r['speed']/3600+r['mass']*9.81*(2*H-o['z']-z)/(r['eta']*3600000)
    maxservice=((1-r['rho_percent']/100)*r['Euse']-fly)*3600/(r['hover']+r['radio'])-r['link']
    return dict(lon=lon,lat=lat,x=x,y=y,z=z,ground=ground,agl=agl,distance=dist,cruise=H,out=out,back=back,fly_energy=fly,max_service=maxservice,ready_offset=r['prep']+out+r['link'],arrival_offset=r['prep']+out)

def build(spacing=900):
    d=inputs();radio=Radio(d);nodes=d['nodes'];xy=np.array([n['xy'] for n in nodes.values()]);lo=xy.min(axis=0)-1000;hi=xy.max(axis=0)+1000
    points=[tuple(n['xy']) for n in nodes.values()]
    # Include a local high-ground representative in each grid tile, and tile centre.
    X,Y=radio.X,radio.Y
    for x in np.arange(lo[0],hi[0],spacing):
        for y in np.arange(lo[1],hi[1],spacing):
            points.append((x+spacing/2,y+spacing/2))
            ll,tt=INVERSE.transform([x,x+spacing],[y,y+spacing]);cols=np.clip(((np.array(ll)-d['lon'][0])/radio.dx+.5).astype(int),0,d['dem'].shape[1]-1);rs=np.clip(((d['lat'][0]-np.array(tt))/radio.dy+.5).astype(int),0,d['dem'].shape[0]-1)
            r0,r1=min(rs),max(rs)+1;c0,c1=min(cols),max(cols)+1
            rr,cc=np.unravel_index(np.argmax(d['dem'][r0:r1,c0:c1]),(r1-r0,c1-c0));points.append(tuple(FORWARD.transform(d['lon'][c0+cc],d['lat'][r0+rr])))
    targets=[np.array(n['xy']+[n['z']+30]) for k,n in nodes.items() if k!='O01'];names=[k for k in nodes if k!='O01'];candidates=[];beg=time.time()
    for i,(x,y) in enumerate(points):
        lon,lat=INVERSE.transform(x,y);r0=int(round((d['lat'][0]-lat)/radio.dy));c0=int(round((lon-d['lon'][0])/radio.dx))
        if not (0<=r0<d['dem'].shape[0] and 0<=c0<d['dem'].shape[1]):continue
        for h in (150,300):
            z=float(d['dem'][r0,c0])+h;p=np.array([x,y,z]);back=radio.point(d['gateway'],p,'backhaul')
            if not back['valid']:continue
            cover=[]
            for name,t in zip(names,targets):
                if np.linalg.norm(p-t)>radio.radii['access'][1]:continue
                if radio.profile(p,t,t,'access')['pieces'][0][2]:cover.append(name)
            if not cover:continue
            candidates.append(dict(lon=lon,lat=lat,agl=h,cover=cover,score=len(cover),distance=float(np.linalg.norm(p-d['gateway']))))
        if i%100==0:print('site scout',i,len(points),'accepted',len(candidates),'s',round(time.time()-beg),flush=True)
    candidates.sort(key=lambda v:(-v['score'],v['distance']))
    selected=[];seen=set()
    # Retain best alternatives for every unique coverage pattern and every service.
    for c in candidates:
        key=tuple(c['cover'])
        if key not in seen:seen.add(key);selected.append(c)
    selected=selected[:60]
    for s in names:
        selected+= [c for c in candidates if s in c['cover']][:3]
    selected+=candidates[:12]
    unique={tuple(c[k] for k in ('lon','lat','agl')):c for c in selected};out=[]
    for c in unique.values():
        m=relay_metrics(d,c['lon'],c['lat'],c['agl'])
        if m and m['max_service']>0:
            m.update(id=f'P{len(out)+1:03d}',cover=c['cover']);out.append(m)
    dump(OUT/'site_scout.json',dict(grid_m=spacing,total_points=len(points),accepted=len(candidates),elapsed=time.time()-beg,coverage_patterns=len(seen)))
    dump(OUT/'relay_sites.json',out);table(OUT/'relay_sites.csv',out)
    print('active',len(out),'best',[(v['id'],v['cover']) for v in out[:10]],flush=True)

if __name__=='__main__':build()
