from support import OUT, PROJECT
import json,math,hashlib,itertools,random
from collections import defaultdict,Counter

def charge(s,full):
    return full*(.65*(.9-s)/.9+.35) if s<.9 else full*.35*(1-s)/.1

class Physics:
    def __init__(self,rho=.2,energy_scale=1.,flight_scale=1.,horizontal_scale=1.):
        self.data=json.loads((OUT/'normalized_inputs.json').read_text(encoding='utf-8'))
        self.boxes={b['id']:b for b in self.data['boxes']};self.models=self.data['models']
        self.rho=rho;self.es=energy_scale;self.fs=flight_scale;self.hs=horizontal_scale
        self.geo={}
        for g in json.loads((OUT/'terrain_evidence_all.json').read_text(encoding='utf-8'))['legs']:
            for a,b in [(g['start'],g['end']),(g['end'],g['start'])]:
                z=self.data['nodes'][a]['z']+(0 if a=='O01' else 30)
                z2=self.data['nodes'][b]['z']+(0 if b=='O01' else 30)
                self.geo[a,b]=(g['distance_m'],g['cruise_m'],g['cruise_m']-z,g['cruise_m']-z2)
        self.legs={}
        for typ,m in self.models.items():
            for (a,b),(d,H,up,down) in self.geo.items():
                self.legs[typ,a,b]=(self.fs*(up/m['up']+d/m['speed']+down/m['down']),d,up)

    def evaluate(self,typ,stops,screen=True):
        # stops are ordered nonempty visits; repeated nonadjacent service is supported.
        stops=[(s,tuple(sorted(bs))) for s,bs in stops if bs]
        ids=tuple(b for _,bs in stops for b in bs)
        if not ids or len(set(ids))!=len(ids):return None
        if any(self.boxes[b]['service']!=s for s,bs in stops for b in bs):return None
        if any(stops[i][0]==stops[i+1][0] for i in range(len(stops)-1)):return None
        m=self.models[typ];mass=sum(self.boxes[b]['weight'] for b in ids);vol=sum(self.boxes[b]['volume_L'] for b in ids)
        if mass>m['Q'] or vol>m['volume_L']:return None
        q=mass;E=0;time=m['prep']+m['load']*len(ids);prep=time;arr=[];flights=[];a='O01';smax=math.inf
        for s,bs in stops+[('O01',())]:
            fly,d,up=self.legs[typ,a,s]
            L=m['L0']-(m['L0']-m['LF'])*(q/m['Q'])**1.5
            e=self.es*(self.hs*m['Euse']*d/L+(m['m0']+q)*9.81*up/(m['eta']*3600000))
            E+=e;time+=fly;flights.append(fly)
            if bs:
                arr.append(time)
                hd=sorted(self.boxes[b]['hard_due'] for b in bs if self.boxes[b]['hard_due'] is not None)
                for j,due in enumerate(hd,1):smax=min(smax,due-time-m['handover']-m['handover_box']*j)
                time+=m['handover']+m['handover_box']*len(bs)
                q-=sum(self.boxes[b]['weight'] for b in bs)
            a=s
        if E>(1-self.rho)*m['Euse']+1e-10 or (screen and smax<-1e-9):return None
        key=json.dumps([typ,stops],separators=(',',':'))
        return dict(id=hashlib.sha256(key.encode()).hexdigest()[:18],model=typ,stops=stops,boxes=list(ids),mass=mass,volume=vol,energy=E,soc=1-E/m['Euse'],duration=time,prep=prep,charge=charge(1-E/m['Euse'],self.data['Tfull'][typ]),arrivals=arr,flights=flights,max_start=None if math.isinf(smax) else smax)

def add(pool,r):
    if r is not None:pool[r['id']]=r

def initial_pool(P,seed=0):
    rng=random.Random(seed);pool={};by=defaultdict(list)
    for b in P.boxes.values():by[b['service']].append(b['id'])
    for s,bs in by.items():
        n=len(bs)
        masks=range(1,1<<n) if n<=9 else sorted(set([1<<i for i in range(n)]+[rng.randrange(1,1<<n) for _ in range(1100)]+[(1<<n)-1]))
        for mask in masks:
            ids=[b for i,b in enumerate(bs) if mask>>i&1]
            for typ in P.models:add(pool,P.evaluate(typ,[(s,ids)]))
        hard=[b for b in bs if P.boxes[b]['hard_due'] is not None]
        for subset in [hard,bs]+[[b] for b in bs]:
            for typ in P.models:add(pool,P.evaluate(typ,[(s,subset)]))
    for b in json.loads((PROJECT/'问题1/results/batches.json').read_text(encoding='utf-8')):
        for typ in P.models:add(pool,P.evaluate(typ,[(b['service'],b['boxes'])]))
    return pool

def greedy_construct(P,seed=0,max_stops=3):
    # Serial list scheduling with explicit aircraft and battery availability.
    rng=random.Random(seed);remaining=set(P.boxes);ua={g:[0.]*P.data['M'][g] for g in P.models};ba={g:[0.]*P.data['K'][g] for g in P.models};out=[];pool={}
    def rank(b):
        v=P.boxes[b];return (v['hard_due'] if v['hard_due'] is not None else v['expected_s']+20000, -v['priority'],rng.random())
    while remaining:
        focus=min(sorted(remaining),key=rank);options=[]
        for typ in P.models:
            start=max(min(ua[typ]),min(ba[typ]));s=P.boxes[focus]['service'];r=P.evaluate(typ,[(s,[focus])])
            if r is None or (r['max_start'] is not None and start>r['max_start']):continue
            # Each insertion evaluated physically; priority boxes get service first for construction only.
            candidates=sorted(sorted(remaining-{focus}),key=lambda b:(P.boxes[b]['hard_due'] or P.boxes[b]['expected_s'],P.geo[s,P.boxes[b]['service']][0] if P.boxes[b]['service']!=s else 0,rng.random()))
            if seed%3==1:rng.shuffle(candidates)
            for b in candidates:
                trials=[];dest=P.boxes[b]['service']
                for i,(node,bs) in enumerate(r['stops']):
                    if node==dest:
                        st=[(n,list(v)) for n,v in r['stops']];st[i][1].append(b);trials.append(st)
                if len(r['stops'])<max_stops:
                    for i in range(len(r['stops'])+1):
                        st=list(r['stops']);st.insert(i,(dest,[b]));trials.append(st)
                valid=[]
                for st in trials:
                    rr=P.evaluate(typ,st)
                    if rr is None or (rr['max_start'] is not None and start>rr['max_start']):continue
                    # Avoid constructively making any expected deadline late when avoidable.
                    good=True
                    for j,(_,ids) in enumerate(rr['stops']):
                        ids=sorted(ids,key=lambda x:(P.boxes[x]['hard_due'] or P.boxes[x]['expected_s'], -P.boxes[x]['priority']))
                        for k,x in enumerate(ids,1):
                            C=start+rr['arrivals'][j]+P.models[typ]['handover']+P.models[typ]['handover_box']*k
                            if C>(P.boxes[x]['hard_due'] or P.boxes[x]['expected_s'])+1e-8:good=False
                    if good:valid.append(rr)
                if valid:r=min(valid,key=lambda x:x['duration']+100*x['energy']/(1+len(x['boxes'])))
            urgency=P.boxes[focus]['hard_due'] or P.boxes[focus]['expected_s']
            # Favor work throughput while including resource finish; randomize modestly across seeds.
            score=(start+r['duration'])/len(r['boxes'])**.62*(.9+.2*rng.random())
            options.append((score,start,r))
        if not options:return None,pool
        _,start,r=min(options,key=lambda x:x[0]);typ=r['model']
        u=min(range(len(ua[typ])),key=ua[typ].__getitem__);b=min(range(len(ba[typ])),key=ba[typ].__getitem__)
        ua[typ][u]=start+r['duration'];ba[typ][b]=start+r['duration']+r['charge']
        out.append(dict(route=r,start=start));add(pool,r);remaining.difference_update(r['boxes'])
    return out,pool

def expand(P,pool,selected,seed=0,limit=1800):
    rng=random.Random(seed);new={};routes=[x.get('route',x) for x in selected]
    def emit(stops):
        for typ in P.models:add(new,P.evaluate(typ,stops))
    def regroup(ids,order):
        return [(s,[b for b in ids if P.boxes[b]['service']==s]) for s in order]
    for r in routes:
        emit(r['stops'])
        for b in r['boxes']:
            ids=set(r['boxes'])-{b};emit([(s,[x for x in bs if x in ids]) for s,bs in r['stops']]);emit([(P.boxes[b]['service'],[b])])
        if len(r['stops'])<=5:
            for st in itertools.permutations(r['stops']):emit(st)
    pairs=list(itertools.combinations(routes,2));rng.shuffle(pairs)
    for r,t in pairs:
        ids=list(dict.fromkeys(r['boxes']+t['boxes']));nodes=list(dict.fromkeys(P.boxes[b]['service'] for b in ids))
        if len(nodes)>5:continue
        orders=list(itertools.permutations(nodes)) if len(nodes)<=3 else [tuple(nodes),tuple(reversed(nodes))]+[tuple(rng.sample(nodes,len(nodes))) for _ in range(5)]
        for order in orders:emit(regroup(ids,order))
        # Relocate and swap in the union; complements retained to enable exact coverage.
        for _ in range(min(14,len(ids)*2)):
            left=set(r['boxes']);right=set(t['boxes'])
            a=rng.choice(sorted(left));left.remove(a);right.add(a)
            if rng.random()<.6 and len(right)>1:
                b=rng.choice(sorted(right-{a}));right.remove(b);left.add(b)
            order=rng.choice(orders);emit(regroup(left,order));emit(regroup(right,order))
        if len(new)>=limit:break
    # Repeated visit probes: split a multi-box station around a different service visit.
    for r in routes:
        if len(r['stops'])<2:continue
        for j,(s,bs) in enumerate(r['stops']):
            if len(bs)>1:
                st=list(r['stops']);st[j]=(s,bs[:1]);st.append((s,bs[1:]));emit(st)
    before=len(pool);pool.update(new)
    return len(pool)-before

def save_pool(pool,path):
    with path.open('w',encoding='utf-8') as f:
        for r in pool.values():f.write(json.dumps(r,ensure_ascii=False)+'\n')

def read_pool(path):
    return {r['id']:r for r in (json.loads(l) for l in path.read_text(encoding='utf-8').splitlines())}
