import json,math
R=json.load(open('body_rows.json'))
def corr(xs,ys):
    p=[(x,y) for x,y in zip(xs,ys) if x is not None and y is not None]; n=len(p)
    if n<20: return None
    mx=sum(x for x,_ in p)/n; my=sum(y for _,y in p)/n
    sx=math.sqrt(sum((x-mx)**2 for x,_ in p)); sy=math.sqrt(sum((y-my)**2 for _,y in p))
    if sx==0 or sy==0: return None
    r=sum((x-mx)*(y-my) for x,y in p)/(sx*sy); se=1/math.sqrt(n-3); zr=math.atanh(r)
    pval=math.erfc(abs(zr)/se/math.sqrt(2)); return r,n,math.tanh(zr-1.96*se),math.tanh(zr+1.96*se),pval
def show(label,c):
    if c: print(f"{label:34s} r={c[0]:+.3f}  n={c[1]:5d}  95% CI [{c[2]:+.3f}, {c[3]:+.3f}]  p={c[4]:.3f}")
print("PRIMARY - engine as it is (all people)")
show("engine height score vs height", corr([r.get('engH') for r in R],[r['hz'] for r in R]))
show("engine build score vs BMI", corr([r.get('engB') for r in R],[r['bz'] for r in R]))
print("\nEXPLORATION - half A")
A=[r for r in R if r['half']=='A']; B=[r for r in R if r['half']=='B']
keep=[]
for tgt,lab in (('hz','height'),('bz','BMI')):
    for k in R[0]['F']:
        c=corr([r['F'][k] for r in A],[r[tgt] for r in A])
        if c and c[4]<0.05: keep.append((tgt,lab,k)); show(f"{lab}: {k}",c)
print(f"\n{len(keep)} features carried to half B (Bonferroni threshold p<{0.05/max(1,len(keep)):.4f})")
print("CONFIRMATION - half B")
for tgt,lab,k in keep:
    c=corr([r['F'][k] for r in B],[r[tgt] for r in B]); show(f"{lab}: {k}",c)
    if c: print("   ->", "CONFIRMED" if c[4]<0.05/len(keep) and (c[0]>0)==(corr([r['F'][k] for r in A],[r[tgt] for r in A])[0]>0) else "not confirmed")
