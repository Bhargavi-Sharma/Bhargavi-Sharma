import json,re
def f(txt,k):
    m=re.search(r'^\|'+k+r'=(.*)$',txt,re.M); return m.group(1).strip() if m else ''
def deg(s):
    m=re.match(r'(\d+)([nsew])(\d+)',s)
    if not m: return None
    v=int(m[1])+int(m[3])/60; return -v if m[2] in 'sw' else v
first=set(json.load(open('titles.json')))
out={'G1':[],'G2':[]}
for line in open('all_pages.jsonl'):
    d=json.loads(line); t,txt=d['t'],d['c']
    rr=f(txt,'sroddenrating'); g='G1' if rr=='AA' else 'G2' if rr in('A','B') else None
    if not g: continue
    sbli=f(txt,'sbli').split(',')
    if len(sbli)<8: continue
    m=re.match(r'h(\d+)([ew])(\d*)$',sbli[7])
    if not m: continue
    off=(int(m[1])+(int(m[3])/60 if m[3] else 0))*(1 if m[2]=='e' else -1)
    dt=f(txt,'sbdate'); tm=f(txt,'sbtime')
    if not re.match(r'\d{4}/\d\d/\d\d$',dt) or not re.match(r'\d\d:\d\d$',tm): continue
    lat,lon=deg(f(txt,'slati')),deg(f(txt,'slong'))
    if lat is None or lon is None: continue
    ev=[]
    for blk in re.findall(r'\{\{ASTRODATABANK_evn(.*?)\}\}',txt,re.S):
        mm=re.match(r'(\d{4})/(\d\d)/(\d\d)',f(blk,'sevdate'))
        if mm and mm[2]!='00': ev.append((f(blk,'sevcode'),f"{mm[1]}-{mm[2]}",f(blk,'EventNotes')))
    voc=[c.strip() for c in re.findall(r'^\|scat=(Vocation[^\n]*)$',txt,re.M)]
    y,mo,dd=map(int,dt.split('/')); h,mi=map(int,tm.split(':'))
    out[g].append(dict(name=t,y=y,mo=mo,d=dd,h=h,mi=mi,tz=off,lat=lat,lon=lon,gender='F' if sbli[2]=='f' else 'M',events=ev,voc=voc,in_first=t in first))
for g,v in out.items(): json.dump(v,open(g+'.json','w')); print(g,len(v),'with events',sum(1 for r in v if r['events']),'new (not in first study)',sum(1 for r in v if not r['in_first']))
