global.Astronomy=require(process.env.ASTRONOMY_ENGINE || 'astronomy-engine');
const J=require('../../artifact/engine-time.js');
const fs=require('fs'); const DAY=86400000;
const recs=JSON.parse(fs.readFileSync(process.env.REC||'aa.json'));
// PRE-REGISTERED mapping (fixed before looking at any score)
const MAP={'Relationship : Marriage':'marriage','Relationship : Divorce dates':'marriage','Death of Mate':'marriage',
 'Relationship : Begin significant relationship':'love','Relationship : End significant relationship':'love','Relationship : Meet a significant person':'love',
 'Death of Father':'father','Death of Mother':'mother','Death of Sibling':'siblings','Death of Child':'children','Family : Adopted a child':'children',
 'Health : Accident (Non-fatal)':'accidents_surgery','Health : Violent trauma':'accidents_surgery','Health : Job related injury':'accidents_surgery','Health : Medical procedure':'accidents_surgery','Death by Accident':'accidents_surgery',
 'Health : Medical diagnosis':'health','Health : Acute illness':'health','Death by Disease':'health','Death by Heart Attack':'health','Death, Cause unspecified':'health',
 'Work : Prize':'govt_authority','Work : Great Achievement':'govt_authority','Work : Gain social status':'govt_authority','Social : Great Publicity':'govt_authority',
 'Work : New Job':'career','Work : New Career':'career','Work : Fired/Laid off/Quit':'career','Work : Retired':'career','Work : Lose social status':'career','Work : Begin Major Project':'career','Work : Published/ Exhibited/ Released':'career','Work : Start Business':'career',
 'Financial : Gain significant money':'wealth','Financial : Lose significant money':'wealth','Financial : Bankruptcy':'wealth',
 'Financial : Buy/Sell Property':'property','Family : Change residence':'property',
 'Crime : Arrest':'litigation','Crime : Law suit':'litigation','Crime : Trial dates':'litigation'};
const childRe=/\b(child|son|daughter|born|birth|baby)\b/i;
const MINA={love:15,marriage:16,children:16,career:14,govt_authority:10,wealth:16,property:16};
const NOW=Date.UTC(2026,9,1);
function prep(r){const b={name:r.name,y:r.y,mo:r.mo,d:r.d,h:r.h,mi:r.mi,s:0,tz:r.tz,lat:r.lat,lon:r.lon,gender:r.gender};
  const c=new J.Chart(b,{}); const bm=c.utc.getTime();
  const death=r.events.filter(e=>/^Death(,| by)/.test(e[0])).map(e=>Date.parse(e[1]+'-15'))[0];
  const end=Math.min(bm+85*365.25*DAY, death?death+60*DAY:Infinity, NOW); return {c,bm,end};}
const cache={};
function months(P,key,area){ // monthly raw scores + named windows for this chart/area
  const k=key+'|'+area; if(cache[k]) return cache[k];
  const st=P.bm+365.25*(MINA[area]??0)*DAY;
  const raw=J.eventWindows(P.c,area,st,P.end,0,true); const named=J.eventWindows(P.c,area,st,P.end,8).windows;
  const n=Math.max(1,Math.round((P.end-st)/(30*DAY)));
  return cache[k]={st,raw,named,n};}
function pct(P,key,area,when){const M=months(P,key,area); if(when<M.st||when>P.end) return null;
  const hit=M.raw.find(w=>when>=w.start&&when<w.start+30*DAY), sc=hit?hit.score:0;
  const below=M.raw.filter(w=>w.score<sc).length+(sc>0?M.n-M.raw.length:0), ties=M.raw.filter(w=>w.score===sc).length+(sc===0?M.n-M.raw.length:0);
  const ms=ym=>Date.parse(ym+'-01T00:00:00Z');
  const inNamed=M.named.some(w=>when>=ms(w.start)-31*DAY&&when<=ms(w.end)+31*DAY);
  return {p:100*(below+ties/2)/M.n, named:inNamed};}
let seed=12345; const rnd=()=>(seed=(seed*1103515245+12345)%2147483648)/2147483648;
const [a0,a1]=[+process.argv[2]||0,+process.argv[3]||recs.length];
const out=[]; const P={};
for(let i=a0;i<Math.min(a1,recs.length);i++){const r=recs[i];
  const evs=[]; for(const [code,ym,note] of r.events){let area=MAP[code]; if(code==='Family : Change in family responsibilities'&&childRe.test(note)) area='children'; if(area) evs.push([area,ym,code]);}
  if(!evs.length) continue;
  try{ P[i]=P[i]||prep(r);}catch(e){continue;}
  for(const [area,ym,code] of evs){const when=Date.parse(ym+'-15T00:00:00Z'); const real=pct(P[i],i,area,when); if(!real) continue;
    // control: same age, different random person
    let ctl=null; for(let t=0;t<10&&!ctl;t++){const j=Math.floor(rnd()*recs.length); if(j===i) continue; try{P[j]=P[j]||prep(recs[j]);}catch(e){continue;}
      const w2=P[j].bm+(when-P[i].bm); ctl=pct(P[j],j,area,w2);}
    out.push({i,name:r.name,area,code,ym,real:Math.round(real.p),realNamed:real.named,ctl:ctl?Math.round(ctl.p):null,ctlNamed:ctl?ctl.named:null});}
  if(i%50===0) process.stderr.write(i+' ');
}
fs.writeFileSync(`${process.env.OUT||'res'}_${a0}_${a1}.json`,JSON.stringify(out));
