from legacy_radio import *
from support import *
from legacy_routes import Physics
import time

def all_pass(prof,lo,hi):
    return not any(not ok and b>lo+1e-12 and a<hi-1e-12 for a,b,ok in prof['pieces']) and not any(lo-1e-12<=x<=hi+1e-12 for x in prof['events'])

def build_route(route,P,radio,sites,max_block=60):
    out=[];pout=phases(route,P)
    for p in pout:
        direct=radio.profile(radio.data['gateway'],p['p0'],p['p1'],'direct');p['direct_profile']=direct
        bad=profile_bad_intervals(direct,0.,1.,padding=1e-7)
        if not bad:continue
        access={s['id']:radio.profile([s['x'],s['y'],s['z']],p['p0'],p['p1'],'access') for s in sites}
        for alo,ahi in bad:
            cuts={alo,ahi}
            for prof in access.values():
                for lo,hi,ok in prof['pieces']:
                    if alo<lo<ahi:cuts.add(lo)
                    if alo<hi<ahi:cuts.add(hi)
                cuts.update(x for x in prof['events'] if alo<x<ahi)
            base=sorted(cuts);parts=[]
            for lo,hi in zip(base,base[1:]):
                K=[sid for sid,prof in access.items() if all_pass(prof,lo,hi)]
                if parts and K==parts[-1][2] and abs(parts[-1][1]-lo)<1e-10:parts[-1][1]=hi
                else:parts.append([lo,hi,K])
            for lo,hi,K in parts:
                a=p['a']+lo*(p['b']-p['a']);b=p['a']+hi*(p['b']-p['a'])
                n=max(1,math.ceil((b-a)/max_block))
                for j in range(n):out.append(dict(a=a+(b-a)*j/n,b=a+(b-a)*(j+1)/n,sites=K,phase=p['phase']))
    return out,pout

