import json,re,collections
raw=json.load(open('raw.json')); recs=[]
def f(txt,k):
    m=re.search(r'^\|'+k+r'=(.*)$',txt,re.M); return m.group(1).strip() if m else ''
def deg(s):
    m=re.match(r'(\d+)([nsew])(\d+)',s)
    if not m: return None
    v=int(m[1])+int(m[3])/60; return -v if m[2] in 'sw' else v
for t,txt in raw.items():
    if f(txt,'sroddenrating')!='AA': continue
    sbli=f(txt,'sbli').split(',')
    if len(sbli)<8: continue
    g=sbli[2]; tzs=sbli[7]
    m=re.match(r'h(\d+)([ew])(\d*)$',tzs)
    if not m: continue  # skip LMT / unusual
    off=(int(m[1])+(int(m[3])/60 if m[3] else 0))*(1 if m[2]=='e' else -1)
    d=f(txt,'sbdate'); tm=f(txt,'sbtime')
    if not re.match(r'\d{4}/\d\d/\d\d$',d) or not re.match(r'\d\d:\d\d$',tm): continue
    lat,lon=deg(f(txt,'slati')),deg(f(txt,'slong'))
    if lat is None or lon is None: continue
    ev=[]
    for blk in re.findall(r'\{\{ASTRODATABANK_evn(.*?)\}\}',txt,re.S):
        code=f(blk,'sevcode'); dt=f(blk,'sevdate'); note=f(blk,'EventNotes')
        mm=re.match(r'(\d{4})/(\d\d)/(\d\d)',dt)
        if mm and mm[2]!='00': ev.append((code,f"{mm[1]}-{mm[2]}",note))
    y,mo,dd=map(int,d.split('/')); h,mi=map(int,tm.split(':'))
    recs.append(dict(name=t,y=y,mo=mo,d=dd,h=h,mi=mi,tz=off,lat=lat,lon=lon,gender='F' if g=='f' else 'M',events=ev))
json.dump(recs,open('aa.json','w'))
print('AA usable',len(recs),'with events',sum(1 for r in recs if r['events']),'events',sum(len(r['events']) for r in recs))
c=collections.Counter(e[0] for r in recs for e in r['events'])
for k,v in c.most_common(80): print(v,k)
