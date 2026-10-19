"""UTM straight routes; closed-cell supercover, independent GEOS verification."""
import math
import numpy as np
from pyproj import Transformer
import shapely

FORWARD = Transformer.from_crs(4326, 32649, always_xy=True)
INVERSE = Transformer.from_crs(32649, 4326, always_xy=True)
CELL_TOL = 1e-9  # raster-cell units (~3e-8 m); only for boundary arithmetic

def touched_axis(x):
    k = round(x)
    return (k-1, k) if abs(x-k)<=CELL_TOL else (math.floor(x),)

def supercover_segment(p, q):
    """All closed unit squares touched, including endpoints/edges/corners."""
    p, q = np.asarray(p, float), np.asarray(q, float)
    v = q-p
    cuts = [0., 1.]
    for axis in (0,1):
        if abs(v[axis]) > 1e-15:
            for k in range(math.ceil(min(p[axis],q[axis])), math.floor(max(p[axis],q[axis]))+1):
                t = (k-p[axis])/v[axis]
                if 0<=t<=1:
                    cuts.append(float(t))
    cuts = sorted(set(cuts))
    probes = cuts + [(a+b)/2 for a,b in zip(cuts,cuts[1:])]
    cells = set()
    for t in probes:
        x,y = p+t*v
        cells.update((r,c) for c in touched_axis(x) for r in touched_axis(y))
    return cells

def geos_cells(points):
    """Independent closed-rectangle intersection; does not use supercover."""
    xy = np.asarray(points)
    line = shapely.LineString(xy)
    shapely.prepare(line)
    lo=np.floor(xy.min(axis=0)).astype(int)-1
    hi=np.ceil(xy.max(axis=0)).astype(int)+1
    cols,rows=np.meshgrid(np.arange(lo[0],hi[0]+1),np.arange(lo[1],hi[1]+1))
    cols,rows=cols.ravel(),rows.ravel()
    rectangles=shapely.box(cols, rows, cols+1, rows+1)
    hit=shapely.intersects(line, rectangles)
    return set(zip(rows[hit].tolist(), cols[hit].tolist()))

def route_points(data, a, b, step):
    x0,y0=FORWARD.transform(a['lon'],a['lat'])
    x1,y1=FORWARD.transform(b['lon'],b['lat'])
    distance=math.hypot(x1-x0,y1-y0)
    t=np.linspace(0,1,max(2,math.ceil(distance/step)+1))
    lon,lat=INVERSE.transform(x0+t*(x1-x0),y0+t*(y1-y0))
    dx=float(data['lon'][1]-data['lon'][0]); dy=float(data['lat'][0]-data['lat'][1])
    pixels=np.column_stack(((lon-data['lon'][0])/dx+.5,(data['lat'][0]-lat)/dy+.5))
    return distance,pixels,np.column_stack((lon,lat))

def leg_geometry(data, start_id, end_id, verify=True):
    a,b=data['nodes'][start_id],data['nodes'][end_id]
    d,points,ll=route_points(data,a,b,5.)
    cells=set()
    for p,q in zip(points,points[1:]):
        cells.update(supercover_segment(p,q))
    check={}
    if verify:
        _,fine,_=route_points(data,a,b,1.)
        independent=geos_cells(fine)
        check=dict(main_cells=len(cells), independent_cells=len(independent), symmetric_difference=len(cells^independent))
        assert cells==independent, (start_id,end_id,check,'5m/1m geometry disagreement')
    dem=data['dem']; nr,nc=dem.shape
    assert all(0<=r<nr and 0<=c<nc for r,c in cells), 'route outside DEM'
    r,c=max(sorted(cells),key=lambda rc:float(dem[rc]))
    H=float(dem[r,c])+50.
    z0=a['z']+(0 if start_id=='O01' else 30)
    z1=b['z']+(0 if end_id=='O01' else 30)
    assert H>=max(z0,z1), 'cruise altitude below operation altitude'
    return dict(start=start_id,end=end_id,service=end_id,distance_m=d,highest_dem_m=H-50,cruise_m=H,start_work_z=z0,end_work_z=z1,out_up_m=H-z0,out_down_m=H-z1,back_up_m=H-z1,back_down_m=H-z0,cell_count=len(cells),highest_row=r,highest_col=c,highest_lon=float(data['lon'][c]),highest_lat=float(data['lat'][r]),cells=sorted(cells),geometry_check=check,route_lonlat=ll.tolist())

def independent_geometry(data, service):
    a,b=data['nodes']['O01'],data['nodes'][service]
    d,points,_=route_points(data,a,b,1.)
    cells=geos_cells(points)
    H=max(float(data['dem'][r,c]) for r,c in cells)+50
    return d,H
