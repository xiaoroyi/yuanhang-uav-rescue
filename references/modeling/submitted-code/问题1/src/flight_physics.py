"""Shared energy and time assumptions; 50-digit coefficients for finite DP."""
import bootstrap
from decimal import Decimal, getcontext
getcontext().prec=50

def D(x):
    return x if isinstance(x,Decimal) else Decimal(str(x))

def equivalent_range(m,q):
    ratio=D(q)/D(m['Q'])
    return D(m['L0'])-(D(m['L0'])-D(m['LF']))*ratio*ratio.sqrt()

def leg_energy(m,distance,climb,payload,eta_scale=1):
    assert 0<=payload<=m['Q'] and climb>=0
    hor=D(m['Euse'])*D(distance)/equivalent_range(m,payload)
    up=(D(m['m0'])+D(payload))*D('9.81')*D(climb)/(D(m['eta'])*D(eta_scale)*D(3600000))
    return hor,up

def metrics(m,geo,q,n,eta_scale=1):
    oh,ou=leg_energy(m,geo['distance_m'],geo['out_up_m'],q,eta_scale)
    bh,bu=leg_energy(m,geo['distance_m'],geo['back_up_m'],0,eta_scale)
    energy=(oh+ou+bh+bu).quantize(D('1e-30'))
    fly=2*D(geo['distance_m'])/D(m['speed'])+(D(geo['out_up_m'])+D(geo['back_up_m']))*(1/D(m['up'])+1/D(m['down']))
    prep=D(m['prep'])+D(m['load'])*n
    hand=D(m['handover'])+D(m['handover_box'])*n
    return dict(E=energy,T=(fly+prep+hand).quantize(D('1e-30')),SOC=1-energy/D(m['Euse']),out_horizontal_kwh=oh,out_climb_kwh=ou,back_horizontal_kwh=bh,back_climb_kwh=bu,flight_time_s=fly,preparation_time_s=prep,handover_time_s=hand,air_time_s=fly+hand,operation_time_s=fly+prep+hand)

def safe_capacity(m,geo,rho):
    limit=(1-D(rho))*D(m['Euse'])
    e0=metrics(m,geo,0,0)['E']; ef=metrics(m,geo,m['Q'],0)['E']
    result=dict(rho=float(rho),empty_energy_kwh=float(e0),full_energy_kwh=float(ef),allowed_kwh=float(limit))
    if e0>limit:
        return dict(result,capacity_kg=None,limit='empty_roundtrip_infeasible',root_width_kg=None,residual_kwh=None)
    lo,hi=D(0),D(m['Q'])
    if ef<=limit:
        lo=hi
        status='rated_payload'
    else:
        status='energy'
        for _ in range(100):
            mid=(lo+hi)/2
            if metrics(m,geo,mid,0)['E']<=limit: lo=mid
            else: hi=mid
            if hi-lo<D('1e-12'): break
    residual=limit-metrics(m,geo,lo,0)['E']
    assert residual>=0
    return dict(result,capacity_kg=float(lo),limit=status,root_width_kg=float(hi-lo),residual_kwh=float(residual))
