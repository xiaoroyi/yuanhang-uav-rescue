import env
from env import ROOT,PROJECT,OUT
from data_io import read_inputs,dump,table,sha
from terrain import leg_geometry
from openpyxl import load_workbook
from collections import Counter
from itertools import combinations
import json,zipfile
from xml.etree import ElementTree as ET

def load():
    data=read_inputs()
    file=next((PROJECT.parent/'D题').rglob('运输无人机数据.xlsx'))
    wb=load_workbook(file,data_only=True,read_only=True)
    aircraft={};stock={};full={}
    for row in wb['数据'].values:
        if isinstance(row[0],str) and row[0].startswith('U') and row[1] in 'ABC':aircraft[row[0]]=row[1]
        if row[0] in ('A','B','C') and isinstance(row[1],int):stock[row[0]]=row[1];full[row[0]]=row[2]
    wb.close()
    for b in data['boxes']:
        deadlines=([b['expected_s']] if b['category']=='MED' else [])+([b['first_deadline_s']] if b['first'] else [])
        b['hard_due']=min(deadlines) if deadlines else None
    data.update(aircraft=aircraft,K=stock,M=dict(Counter(aircraft.values())),Tfull=full)
    return data

def prepare():
    data=load()
    audit=data['audit'];hard=[b for b in data['boxes'] if b['hard_due'] is not None]
    audit.update(hard_boxes=len(hard),hard_hist=dict(Counter(b['hard_due'] for b in hard)),medical=sum(b['category']=='MED' for b in data['boxes']),medical_first=sum(b['category']=='MED' and b['first'] for b in data['boxes']),M=data['M'],K=data['K'],Tfull=data['Tfull'])
    assert audit['hard_hist']=={3600:17,7200:7,10800:7}
    assert (audit['boxes'],audit['mass_kg'],audit['volume_L'],len(hard))==(80,758,2011,31)
    assert data['M']=={'A':4,'B':2,'C':2} and data['K']=={'A':6,'B':4,'C':4}
    q1=json.loads((PROJECT/'问题1/results/run_manifest.json').read_text(encoding='utf-8'))
    dump(OUT/'input_audit.json',audit)
    dump(OUT/'normalized_inputs.json',{k:data[k] for k in ('nodes','models','boxes','aircraft','M','K','Tfull')})
    table(OUT/'hard_deadlines.csv',hard)
    doc=next(p for p in (PROJECT.parent/'D题').glob('*.docx') if not p.name.startswith('~$'))
    with zipfile.ZipFile(doc) as z:
        root=ET.fromstring(z.read('word/document.xml'))
        lines=[''.join(p.itertext()) for p in root.findall('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p')]
    (OUT/'原题文字核对.txt').write_text('\n'.join(lines),encoding='utf-8')
    cache=OUT/'terrain_evidence_all.json'
    if cache.exists():
        saved=json.loads(cache.read_text(encoding='utf-8'))
        assert saved['inputs']==audit['inputs']
        geos=saved['legs']
    else:
        geos=[]
        for n,(a,b) in enumerate(combinations(sorted(data['nodes']),2)):
            geos.append(leg_geometry(data,a,b,verify=True))
            if n%20==19:print(f'Geometry {n+1}/120 verified',flush=True)
        dump(cache,dict(inputs=audit['inputs'],method='UTM49N straight; 5m supercover vs independent 1m GEOS; closed pixels',legs=geos))
    table(OUT/'leg_geometry_all.csv',[{k:v for k,v in g.items() if k not in ('cells','route_lonlat','geometry_check')} for g in geos])
    old=json.loads((PROJECT/'问题1/results/terrain_evidence.json').read_text(encoding='utf-8'))
    dump(OUT/'assumptions.json',dict(objective_order=['weighted_tardiness','makespan','energy','sorties'],start='preparation_start',battery='full_at_preparation_start',delivery='base_then_sequential_box',charging_capacity=None,station_capacity=None,energy='Q1 unchanged horizontal Euse*d/L(q) + climb mgh/eta; no hover or extra descent energy',repeated_visits='supported in route evaluator; search bounded, not proven unnecessary',time_quantum_s=0.1,energy_quantum_kwh=1e-6,route_pool_complete=False))
    print(json.dumps(audit,ensure_ascii=False),flush=True)

if __name__=='__main__':prepare()
