import json,glob,math,collections,random
R=[]
for f in ['res_0_700.json','res_700_1400.json','res_1400_2100.json','res_2100_2800.json']: R+=json.load(open(f))
R=[r for r in R if r['ctl'] is not None]
def summ(rows,label):
    n=len(rows); 
    if n<15: return
    re=[r['real'] for r in rows]; ct=[r['ctl'] for r in rows]
    mr,mc=sum(re)/n,sum(ct)/n
    d=[a-b for a,b in zip(re,ct)]; md=sum(d)/n; sd=(sum((x-md)**2 for x in d)/(n-1))**.5; se=sd/n**.5
    hn=sum(r['realNamed'] for r in rows)/n*100; hc=sum(r['ctlNamed'] for r in rows)/n*100
    print(f"{label:22s} n={n:5d}  real {mr:5.1f}  control {mc:5.1f}  diff {md:+5.1f} ±{1.96*se:4.1f}   in-named-window real {hn:4.1f}%  control {hc:4.1f}%")
print("people",len({r['i'] for r in R}))
summ(R,"ALL")
for a in sorted({r['area'] for r in R}): summ([r for r in R if r['area']==a],a)
