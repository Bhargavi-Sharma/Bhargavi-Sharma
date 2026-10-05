const {P}=require('./myth.js'); const J=require('../../artifact/engine-time.js'); const DAY=86400000;
const EV={
 Rama:{span:80,ev:[['marriage',13,'marriage to Sita (~12 yrs before exile, Aranya 47)'],['father',25,'Dasharatha dies days after the exile'],['foreign',25,'exile to the forest'],['property',25,'loses the throne / home'],['marriage',38,'Sita abducted (13th year of exile)'],['litigation',39,'war with Ravana'],['govt_authority',39,'return and coronation']]},
 Krishna:{span:126,ev:[['litigation',11,'kills Kamsa'],['litigation',89,'Kurukshetra war'],['health',125,'leaves the body (start of Kali Yuga by the same chronology)']]},
};
for(const [n,{span,ev}] of Object.entries(EV)){
  const c=new J.Chart({name:n,...P[n]},{}); const bm=c.utc.getTime();
  console.log('==',n);
  const hits=[];
  for(const [area,age,what] of ev){
    const raw=J.eventWindows(c,area,bm,bm+span*365.25*DAY,0,true);
    const yr=Array.from({length:span},(_,a)=>{const s=bm+a*365.25*DAY,e=s+365.25*DAY; const w=raw.filter(x=>x.start>=s&&x.start<e); return w.length?Math.max(...w.map(x=>x.score)):0;});
    const sc=yr[age], below=yr.filter(v=>v<sc).length, tie=yr.filter(v=>v===sc).length, pct=Math.round(100*(below+tie/2)/span);
    const run=J.runningDasha(J.vimshottari(c.lon.Moon,bm,365.25),bm+(age+0.5)*365.25*DAY);
    const top=[...yr.keys()].sort((a,b)=>yr[b]-yr[a]).slice(0,5);
    console.log(`  age ${String(age).padStart(3)} ${area.padEnd(15)} percentile ${String(pct).padStart(3)}  dasha ${run.md.lord}/${run.ad.lord}  engine's top-5 ages: ${top.join(',')}   (${what})`);
    hits.push(pct);
  }
  console.log('  mean percentile',Math.round(hits.reduce((a,b)=>a+b)/hits.length));
}
