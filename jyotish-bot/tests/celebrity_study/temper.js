global.Astronomy=require(process.env.ASTRONOMY_ENGINE || 'astronomy-engine');
const J=require('../../artifact/engine-time.js'); const fs=require('fs');
const AS=['Aggressive/ brash','Temper','Fiery','Courageous'].map(x=>'Traits : Personality : '+x), RE=['Shy','Passive/ Bland','Solitary/ Introvert','Private'].map(x=>'Traits : Personality : '+x);
const G={assertive:[],reserved:[]};
for(const line of fs.readFileSync('all_pages.jsonl','utf8').split('\n')){ if(!line) continue; const d=JSON.parse(line), t=d.c;
  const f=k=>{const m=t.match(new RegExp('^\\|'+k+'=(.*)$','m')); return m?m[1].trim():'';};
  if(!['AA','A','B'].includes(f('sroddenrating'))) continue;
  const cats=[...t.matchAll(/^\|scat=(.*)$/gm)].map(m=>m[1].trim()); const a=cats.some(c=>AS.includes(c)), r=cats.some(c=>RE.includes(c));
  if(a===r) continue;
  const sbli=f('sbli').split(','); if(sbli.length<8) continue; const m=sbli[7].match(/^h(\d+)([ew])(\d*)$/); if(!m) continue;
  const dt=f('sbdate'), tm=f('sbtime'); if(!/^\d{4}\/\d\d\/\d\d$/.test(dt)||!/^\d\d:\d\d$/.test(tm)) continue;
  const deg=s=>{const q=s.match(/(\d+)([nsew])(\d+)/); if(!q) return null; const v=+q[1]+ +q[3]/60; return 'sw'.includes(q[2])?-v:v;};
  const lat=deg(f('slati')), lon=deg(f('slong')); if(lat==null||lon==null) continue;
  const [y,mo,dd]=dt.split('/').map(Number), [h,mi]=tm.split(':').map(Number);
  try{ const c=new J.Chart({y,mo,d:dd,h,mi,s:0,tz:(+m[1]+(m[3]?+m[3]/60:0))*(m[2]==='e'?1:-1),lat,lon,gender:sbli[2]==='f'?'F':'M'},{});
    const fire=[0,4,8];
    G[a?'assertive':'reserved'].push({mars_on_lagna:c.occupants(1).includes('Mars')||c.aspectedBy(1,true).includes('Mars')||J.SIGN_LORD[c.lagna]==='Mars',
      fire_lagna:fire.includes(c.lagna), fire_moon:fire.includes(c.moonSign), strong_mars:(J.DIGNITY_SCORE[c.dig.Mars]??0)>=3});
  }catch(e){}
}
for(const k of ['mars_on_lagna','fire_lagna','fire_moon','strong_mars']){
  const p=g=>G[g].filter(x=>x[k]).length/G[g].length, pa=p('assertive'), pr=p('reserved');
  const se=Math.sqrt(pa*(1-pa)/G.assertive.length+pr*(1-pr)/G.reserved.length);
  console.log(`${k.padEnd(14)} assertive ${(100*pa).toFixed(1)}% (n=${G.assertive.length})  reserved ${(100*pr).toFixed(1)}% (n=${G.reserved.length})  diff ${(100*(pa-pr)).toFixed(1)} ±${(196*se).toFixed(1)}`);
}
