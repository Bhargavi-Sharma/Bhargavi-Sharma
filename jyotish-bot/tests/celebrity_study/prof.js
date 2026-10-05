global.Astronomy=require(process.env.ASTRONOMY_ENGINE || 'astronomy-engine');
const J=require('../../artifact/engine-time.js');
const fs=require('fs');
const G={Mars:[/^Vocation : Military/,/^Vocation : Law : Police/,/^Vocation : Medical : Surgeon/,/^Vocation : Sports : /],
 Sun:[/Politics : Heads of state/,/Politics : Public office/,/Politics : Government employee/,/Politics : Diplomat/,/Medical : Physician/],
 Venus:[/Entertainment : Actor\/ Actress/,/^Vocation : Beauty/,/^Vocation : Entertain\/Music/,/Art : Fine art artist/],
 Mercury:[/^Vocation : Writers : (?!Astrology)/,/Entertainment : News journalist/,/Science : Mathematics/],
 Jupiter:[/Law : Attorney/,/Law : Jurist/,/^Vocation : Religion/,/Education : Teacher/,/Business : Banker/]};
const PL=Object.keys(G);
function group(voc){const s=new Set(); for(const v of voc) for(const p of PL) if(G[p].some(re=>re.test(v))) s.add(p); return s.size===1?[...s][0]:null;}
function link(c,p){const h10=(c.lagna+9)%12, l10=c.lordOfHouse(10), nd=J.SIGN_LORD[c.vargas[9][l10]], m10=(c.moonSign+9)%12;
  return c.sign[p]===h10||l10===p||nd===p||c.sign[p]===m10?1:0;}
for(const g of process.argv.slice(2)){
  const R=JSON.parse(fs.readFileSync(g+'.json')); const rows=[];
  for(const r of R){const gp=group(r.voc); if(!gp) continue; let c; try{c=new J.Chart({...r,s:0},{});}catch(e){continue;}
    rows.push({gp,L:Object.fromEntries(PL.map(p=>[p,link(c,p)]))});}
  console.log(`\n${g}: ${rows.length} people with a single-planet profession group`);
  for(const p of PL){const a=rows.filter(x=>x.gp===p), b=rows.filter(x=>x.gp!==p);
    const pa=a.reduce((s,x)=>s+x.L[p],0)/a.length, pb=b.reduce((s,x)=>s+x.L[p],0)/b.length;
    const se=Math.sqrt(pa*(1-pa)/a.length+pb*(1-pb)/b.length);
    console.log(`${p.padEnd(8)} n=${String(a.length).padStart(5)}  linked in own profession ${(100*pa).toFixed(1)}%  in other professions ${(100*pb).toFixed(1)}%  diff ${(100*(pa-pb)>=0?'+':'')}${(100*(pa-pb)).toFixed(1)} ±${(196*se).toFixed(1)}`);}
}
