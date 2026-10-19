"""Continuous swept-line occlusion in a frozen projected-pixel terrain model."""
from support import *
import math,hashlib
from numba import njit

@njit(cache=True)
def clip(poly,n,A,B,C):
    out=np.empty((16,2));k=0
    for i in range(n):
        j=(i+1)%n;x,y=poly[i];xx,yy=poly[j];f=A*x+B*y+C;g=A*xx+B*yy+C
        if f<=1e-10:out[k,0]=x;out[k,1]=y;k+=1
        if (f<0 and g>0) or (f>0 and g<0):
            t=f/(f-g);out[k,0]=x+t*(xx-x);out[k,1]=y+t*(yy-y);k+=1
    return out,k

@njit(cache=True)
def blocked_kernel(a,p0,p1,verts,heights,pad):
    result=np.empty((len(heights),2));nres=0;v0=p0-a;v1=p1-a
    for k in range(len(heights)):
        if heights[k]+1e-7<min(a[2],p0[2],p1[2]):continue
        poly=np.empty((16,2));poly[0]=[0.,0.];poly[1]=[1.,0.];poly[2]=[0.,1.];n=3
        for e in range(4):
            x,y=verts[k,e];xx,yy=verts[k,(e+1)%4];dx=xx-x;dy=yy-y
            A=dx*v0[1]-dy*v0[0];B=dx*v1[1]-dy*v1[0];C=dx*(a[1]-y)-dy*(a[0]-x)-pad*math.hypot(dx,dy)
            poly,n=clip(poly,n,A,B,C)
            if n==0:break
        if n==0:continue
        poly,n=clip(poly,n,v0[2],v1[2],a[2]-heights[k]-1e-7)
        if n==0:continue
        low=1.;high=0.;haszero=False
        for j in range(n):
            den=poly[j,0]+poly[j,1]
            if den>1e-12:
                u=poly[j,1]/den;low=min(low,u);high=max(high,u)
            else:haszero=True
        if haszero and a[2]<=heights[k]+1e-7:
            low=0.;high=1.
        if high>=low:
            result[nres,0]=max(0.,low);result[nres,1]=min(1.,high);nres+=1
    return result[:nres]

def merge(iv,tol=1e-11):
    ans=[]
    for a,b in sorted(iv,key=lambda v:(v[0],v[1])):
        a=max(0.,float(a));b=min(1.,float(b))
        if b<a:continue
        if ans and a<=ans[-1][1]+tol:ans[-1][1]=max(ans[-1][1],b)
        else:ans.append([a,b])
    return ans

class Radio:
    def __init__(self,data,margin=8,obstacle=10,pad=.002):
        self.data=data;self.margin=margin;self.obstacle=obstacle;self.pad=pad;self.cache={}
        self.base=32.45+20*math.log10(data['radio']['frequency'])-60
        self.limits={k:data['radio'][k]['limit']-(margin-8) for k in ('direct','access','backhaul')}
        self.radii={k:(10**((v-self.base-obstacle)/20),10**((v-self.base)/20)) for k,v in self.limits.items()}
        lon=data['lon'];lat=data['lat'];dx=lon[1]-lon[0];dy=lat[0]-lat[1]
        le=np.r_[lon-dx/2,lon[-1]+dx/2];la=np.r_[lat+dy/2,lat[-1]-dy/2]
        file=CACHE/'pixel_corners.npz'
        if file.exists():
            z=np.load(file);self.X=z['X'];self.Y=z['Y']
        else:
            lo,lt=np.meshgrid(le,la);self.X,self.Y=FORWARD.transform(lo,lt);np.savez_compressed(file,X=self.X,Y=self.Y)
        self.dem=data['dem'];self.dx=dx;self.dy=dy
    def cells(self,a,p0,p1):
        pts=np.array([a,p0,p1]);xmin,ymin=pts[:,:2].min(axis=0);xmax,ymax=pts[:,:2].max(axis=0)
        lo,lt=INVERSE.transform([xmin,xmin,xmax,xmax],[ymin,ymax,ymin,ymax])
        c0=max(0,int(math.floor((min(lo)-self.data['lon'][0])/self.dx+.5))-2);c1=min(self.dem.shape[1],int(math.ceil((max(lo)-self.data['lon'][0])/self.dx+.5))+2)
        r0=max(0,int(math.floor((self.data['lat'][0]-max(lt))/self.dy+.5))-2);r1=min(self.dem.shape[0],int(math.ceil((self.data['lat'][0]-min(lt))/self.dy+.5))+2)
        hs=self.dem[r0:r1,c0:c1];rs,cs=np.where(hs>=pts[:,2].min()-1e-7);rs+=r0;cs+=c0
        verts=np.stack([np.stack([self.X[rs,cs],self.Y[rs,cs]],axis=1),np.stack([self.X[rs,cs+1],self.Y[rs,cs+1]],axis=1),np.stack([self.X[rs+1,cs+1],self.Y[rs+1,cs+1]],axis=1),np.stack([self.X[rs+1,cs],self.Y[rs+1,cs]],axis=1)],axis=1)
        return verts,np.asarray(self.dem[rs,cs],dtype=float)
    def blocked(self,a,p0,p1):
        vs,hs=self.cells(a,p0,p1)
        return merge(blocked_kernel(np.array(a,dtype=float),np.array(p0,dtype=float),np.array(p1,dtype=float),vs,hs,self.pad))
    def profile(self,a,p0,p1,kind):
        a=np.asarray(a,float);p0=np.asarray(p0,float);p1=np.asarray(p1,float)
        key=tuple(a)+tuple(p0)+tuple(p1)+(kind,)
        if key in self.cache:return self.cache[key]
        rb,rc=self.radii[kind];v=p1-p0;w=p0-a;A=np.dot(v,v);B=2*np.dot(w,v);C=np.dot(w,w)
        dmax=max(np.linalg.norm(w),np.linalg.norm(p1-a))
        if dmax<=rb:return {'pieces':[[0.,1.,True]],'events':[],'blocked':[],'radius_certified':True}
        u=np.clip(-B/(2*A),0,1) if A>1e-18 else 0;dmin=np.linalg.norm(w+u*v)
        if dmin>rc:return {'pieces':[[0.,1.,False]],'events':[0.,1.],'blocked':[],'radius_certified':True}
        obs=self.blocked(a,p0,p1);cuts=[0.,1.]
        for lo,hi in obs:cuts.extend([lo,hi])
        for r in (rb,rc):
            if A>1e-18:
                dis=B*B-4*A*(C-r*r)
                if dis>=0:
                    for x in [(-B-math.sqrt(dis))/(2*A),(-B+math.sqrt(dis))/(2*A)]:
                        if 0<x<1:cuts.append(float(x))
        cuts=sorted(set(cuts))
        def valid(u):
            dist=np.linalg.norm(w+u*v);blocked=any(lo-1e-11<=u<=hi+1e-11 for lo,hi in obs)
            return bool(dist<=rb+1e-8 or (not blocked and dist<=rc+1e-8))
        pieces=[[lo,hi,valid((lo+hi)/2)] for lo,hi in zip(cuts,cuts[1:]) if hi>lo]
        events=[u for u in cuts if not valid(u)]
        res={'pieces':pieces,'events':events,'blocked':obs,'radius_certified':False};self.cache[key]=res;return res
    def point(self,a,p,kind):
        prof=self.profile(a,p,p,kind);blocked=bool(self.blocked(a,p,p));d=float(np.linalg.norm(np.array(a)-p));loss=self.base+20*math.log10(max(d,1e-9))+self.obstacle*blocked
        return dict(valid=loss<=self.limits[kind]+1e-8,blocked=blocked,distance=d,loss=loss,margin=self.limits[kind]-loss)

def phases(route,P):
    m=P.models[route['model']];t=route['prep'];prev='O01';out=[];data=P.data
    for leg,(dest,bs) in enumerate(list(route['stops'])+[('O01',[])],1):
        a=data['nodes'][prev];b=data['nodes'][dest];x0,y0=FORWARD.transform(a['lon'],a['lat']);x1,y1=FORWARD.transform(b['lon'],b['lat'])
        z0=a['z']+(30 if prev!='O01' else 0);z1=b['z']+(30 if dest!='O01' else 0);d,H,up,down=P.geo[prev,dest]
        seq=[('爬升',[x0,y0,z0],[x0,y0,H],up/m['up']),('巡航',[x0,y0,H],[x1,y1,H],d/m['speed']),('下降',[x1,y1,H],[x1,y1,z1],down/m['down'])]
        if bs:seq.append(('交接',[x1,y1,z1],[x1,y1,z1],m['handover']+m['handover_box']*len(bs)))
        for typ,p0,p1,dt in seq:
            if dt>1e-10:out.append(dict(phase=len(out)+1,leg=leg,origin=prev,destination=dest,type=typ,a=t,b=t+dt,p0=p0,p1=p1))
            t+=dt
        prev=dest
    assert abs(t-route['duration'])<1e-7
    return out

def profile_bad_intervals(profile,a,b,padding=1e-5):
    # Expanded boundaries include isolated obstructed contacts; no sampling gap.
    iv=[[max(a,a+lo*(b-a)-padding),min(b,a+hi*(b-a)+padding)] for lo,hi,ok in profile['pieces'] if not ok]
    iv += [[max(a,a+u*(b-a)-padding),min(b,a+u*(b-a)+padding)] for u in profile['events']]
    ans=[]
    for lo,hi in sorted(iv):
        if ans and lo<=ans[-1][1]+1e-8:ans[-1][1]=max(ans[-1][1],hi)
        else:ans.append([lo,hi])
    return ans

