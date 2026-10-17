"""Read original inputs without modifying them; no cached handoff tables."""
from bootstrap import ROOT, PROJECT
from pathlib import Path
from collections import Counter
from decimal import Decimal
import csv
import hashlib
import json
import numpy as np
from openpyxl import load_workbook
from scipy.io import loadmat

SOURCE = PROJECT.parent / 'D题'
CATEGORIES = ('MED', 'WAT', 'FOD', 'HYG')

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def dump(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=lambda x: x.item() if isinstance(x, np.generic) else str(x), allow_nan=False), encoding='utf-8')

def table(path, rows):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        Path(path).write_text('', encoding='utf-8-sig')
        return
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list, tuple)) else v for k, v in r.items()})

def liters(value):
    x = Decimal(str(value)) * 1000
    assert x == x.to_integral_value(), ('volume not integral liters', value)
    return int(x)

def read_inputs(source=SOURCE):
    files = {p.name: p for p in Path(source).rglob('*.xlsx') if not p.name.startswith('~$')}
    def rows(name, sheet='数据'):
        wb = load_workbook(files[name], data_only=True, read_only=True)
        values = [list(r) for r in wb[sheet].values if any(x is not None for x in r)]
        wb.close()
        return values
    nodes = {}
    for r in rows('调度中心与服务区.xlsx'):
        if r[0] == 'O01' or (isinstance(r[0], str) and r[0].startswith('S') and r[0][1:].isdigit()):
            nodes[r[0]] = dict(id=r[0], name=r[1], lon=float(r[2]), lat=float(r[3]), z=float(r[4]))
    models = {}
    keys = ['m0', 'Q', 'V', 'speed', 'L0', 'LF', 'Euse', 'rho_percent', 'prep', 'load', 'handover', 'handover_box', 'up', 'down', 'eta', 'down_eff']
    for r in rows('运输无人机数据.xlsx'):
        if r[0] in ('A', 'B', 'C') and r[0] not in models and len(r)>=18 and isinstance(r[2],(int,float)):
            m = dict(zip(keys, r[2:18]))
            m.update(id=r[0], volume_L=liters(m['V']), rho=m['rho_percent']/100)
            assert m['down_eff'] == 0 and m['eta'] > 0 and m['L0'] >= m['LF'] > 0
            models[r[0]] = m
    br = rows('物资需求与配送时限.xlsx', '逐箱货箱清单')
    boxes = []
    attributes = {}
    for r in br[1:]:
        b = dict(id=r[0], service=r[1], category=r[0].split('-')[1], weight=r[3], volume_L=liters(r[4]), first=r[5]=='是', first_deadline_s=r[6], expected_s=r[7], priority=r[8], original=dict(zip(br[0], r)))
        assert b['service'] in nodes and b['category'] in CATEGORIES
        attr = (b['weight'], b['volume_L'])
        assert b['category'] not in attributes or attributes[b['category']] == attr
        attributes[b['category']] = attr
        boxes.append(b)
    assert len({b['id'] for b in boxes}) == len(boxes)
    for r in rows('物资需求与配送时限.xlsx')[1:]:
        subset = [b for b in boxes if b['service']==r[0] and b['original']['物资类型']==r[1]]
        assert len(subset)==r[2] and sum(b['first'] for b in subset)==r[3]
        assert all(b['weight']==r[4] and b['volume_L']==liters(r[5]) and b['priority']==r[6] and b['expected_s']==r[8] and (not b['first'] or b['first_deadline_s']==r[7]) for b in subset)
    services = sorted(set(b['service'] for b in boxes))
    counts = {s: tuple(sum(b['service']==s and b['category']==c for b in boxes) for c in CATEGORIES) for s in services}
    mat_path = next(Path(source).rglob('*DEM.mat'))
    mat = loadmat(mat_path)
    dem, lon, lat = mat['dem'], mat['longitude'].ravel(), mat['latitude'].ravel()
    assert dem.shape == (len(lat), len(lon)) and np.all(np.diff(lon)>0) and np.all(np.diff(lat)<0)
    assert np.allclose(np.diff(lon), np.diff(lon)[0]) and np.allclose(np.diff(lat), np.diff(lat)[0])
    assert int(mat['epsg_code'].item())==4326
    assert np.all(np.isfinite(dem)) and not np.any(dem==mat['nodata'].item())
    used = [files[n] for n in ('调度中心与服务区.xlsx','运输无人机数据.xlsx','物资需求与配送时限.xlsx','结果提交模板.xlsx')] + [mat_path, next(p for p in Path(source).glob('*.docx') if not p.name.startswith('~$'))]
    audit = dict(boxes=len(boxes), mass_kg=sum(b['weight'] for b in boxes), volume_L=sum(b['volume_L'] for b in boxes), first_boxes=sum(b['first'] for b in boxes), states=sum(int(np.prod(np.array(c)+1)) for c in counts.values()), dem_shape=list(dem.shape), inputs={str(p):sha(p) for p in used}, nodes=[])
    for n in nodes.values():
        i,j=int(np.argmin(abs(lat-n['lat']))),int(np.argmin(abs(lon-n['lon'])))
        assert lon[0]<=n['lon']<=lon[-1] and lat[-1]<=n['lat']<=lat[0]
        audit['nodes'].append(dict(id=n['id'], excel_z=n['z'], dem_z=float(dem[i,j]), difference_m=n['z']-float(dem[i,j]), row=i, col=j))
    return dict(nodes=nodes, models=models, boxes=boxes, attributes=attributes, counts=counts, services=services, dem=dem, lon=lon, lat=lat, audit=audit, template=files['结果提交模板.xlsx'])
