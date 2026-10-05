/* Timing-method harness: percentile rank of real dated events among all scanned months (50 = chance),
   for several principled scoring variants. Run: ASTRONOMY_ENGINE=/path/to/astronomy-engine node tests/timing_harness.js */
global.Astronomy=require(process.env.ASTRONOMY_ENGINE || 'astronomy-engine');
const J=require('../artifact/engine-time.js');
const {PLANETS,SIGNS,SIGN_LORD,houseFrom,signOf,nakshatraOf,vimshottari,runningDasha,DAY}=J; const Astro=J.Astro;
const CH={
 B:{b:{y:2002,mo:7,d:24,h:2,mi:58,s:0,tz:'Asia/Kolkata',lat:28.9931,lon:77.0151,gender:'F'},ev:[
  ['education','2020-12'],['education','2021-03'],['education','2022-02'],
  ['career','2024-01'],['career','2024-08'],['career','2025-04'],['career','2026-06'],
  ['love','2020-09'],['love','2022-01'],['love','2022-05'],['love','2025-04'],['love','2025-05'],['love','2026-02'],
  ['accidents_surgery','2023-11'],['accidents_surgery','2025-05'],['accidents_surgery','2026-09'],
  ['siblings','2017-11'],['mother','2024-06'],['mother','2017-11']]},
 M:{b:{y:1977,mo:8,d:23,h:16,mi:52,s:0,tz:'Asia/Kolkata',lat:28.99,lon:77.02,gender:'F'},ev:[
  ['marriage','2001-01'],['children','2002-07'],['children','2017-11'],['health','2024-06']]},
};
const MIN={love:15,marriage:18,children:20,career:18,education:16};
// transit cache per month
const tcache={};
function tr(t){const k=Math.floor(t/(30*DAY)); if(!tcache[k]){const jd=Astro.dateToJd(new Date(t)); tcache[k]={J:signOf(Astro.siderealLon('Jupiter',jd)),S:signOf(Astro.siderealLon('Saturn',jd))};} return tcache[k];}
function infl(base,sign,p){const h=houseFrom(base,sign),o=new Set([h]); for(const n of (J.SPECIAL_ASPECTS[p]||[7])) o.add(((h+n-2)%12)+1); return o;}
// tiered significator weight
function tierW(c,houses,main,kar,W){
  const w={}; const add=(p,x)=>w[p]=Math.max(w[p]||0,x);
  for(const h of houses){const m=h===main?1:W.other; const L=c.lordOfHouse(h);
    add(L,W.lord*m); for(const p of c.occupants(h)) add(p,W.occ*m);
    for(const p of c.aspectedBy(h,true)) add(p,W.asp*m); for(const p of c.conjunct(L)) add(p,W.conj*m);}
  for(const p of PLANETS){const nl=nakshatraOf(c.lon[p]).lord; if((w[nl]||0)>=W.lord*0.99) add(p,W.nak);}
  for(const n of ['Rahu','Ketu']){const d=SIGN_LORD[c.sign[n]]; add(n,(w[d]||0)*W.disp);}
  if(kar) add(kar,(w[kar]||0)+W.kar);
  return w;
}
function scoreFn(c,area,W){
  const spec=J.AREAS[area],main=spec.main,kar=spec.karaka_m?(c.birth.gender==='F'?spec.karaka_f:spec.karaka_m):spec.karaka;
  let w=tierW(c,spec.houses,main,kar,W); const v=vimshottari(J.Astro.norm(c.lon.Moon+(W.moonOff||0)),c.utc.getTime(),W.year||365.25);
  if(W.kp){const w2={}; for(const p of PLANETS){const sl=nakshatraOf(c.lon[p]).lord; w2[p]=W.kp*(w[sl]||0)+(1-W.kp)*(w[p]||0);} w=w2;}
  const lordH=houseFrom(c.lagna,c.sign[c.lordOfHouse(main)]);
  return t=>{const r=runningDasha(v,t); if(!r) return 0; let s=W.md*(w[r.md.lord]||0)+W.ad*(w[r.ad.lord]||0)+W.pd*(w[r.pd.lord]||0);
    if(W.tr){const x=tr(t),jh=infl(c.lagna,x.J,'Jupiter'),sh=infl(c.lagna,x.S,'Saturn'); if(jh.has(main)&&sh.has(main)) s+=W.tr; if(jh.has(lordH)&&sh.has(lordH)) s+=W.tr*0.75;}
    return s;};
}
function evaluate(W,filter){
  const res=[];
  for(const [k,{b,ev}] of Object.entries(CH)){const c=new J.Chart(b,{}); const bm=c.utc.getTime();
    for(const [i,[area,ym]] of ev.entries()){ if(filter && !filter(i)) continue;
      const f=scoreFn(c,area,W), st=bm+365.25*(MIN[area]??0)*DAY, en=bm+365.25*Math.min(60,Math.max(35,(Date.UTC(2026,9,1)-bm)/DAY/365.25+5))*DAY;
      const when=Date.parse(ym+'-15T00:00:00Z'), se=f(when); let below=0,tie=0,n=0;
      for(let t=st;t<en;t+=30*DAY){const s=f(t); n++; if(s<se) below++; else if(s===se) tie++;}
      res.push({k,area,ym,pct:Math.round(100*(below+tie/2)/n)});}}
  return res;
}
module.exports={evaluate,CH};
if(require.main===module){
 const base={lord:3,occ:3,asp:1,conj:0.5,nak:0.5,disp:0.5,kar:2,other:0.5,md:1,ad:1,pd:0.75,tr:2};
 const V={base, kp_starlord:{...base,kp:1}, kp_mix:{...base,kp:0.5}, year360:{...base,year:360}};
 for(const off of [-1.5,-1,-0.5,0.5,1,1.5]) V['moon'+off]={...base,moonOff:off};
 for(const [n,W] of Object.entries(V)){const r=evaluate(W); const m=a=>Math.round(a.reduce((x,y)=>x+y.pct,0)/a.length);
  console.log(n.padEnd(14),'all',m(r),'B',m(r.filter(x=>x.k=='B')),'M',m(r.filter(x=>x.k=='M')),'even',m(r.filter((_,i)=>i%2==0)),'odd',m(r.filter((_,i)=>i%2)));}
}
