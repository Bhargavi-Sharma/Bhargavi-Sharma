global.Astronomy=require(process.env.ASTRONOMY_ENGINE || 'astronomy-engine');
const J=require('../../artifact/engine-time.js');
const fs=require('fs'), crypto=require('crypto');
const rows=[];
for(const line of fs.readFileSync('all_pages.jsonl','utf8').split('\n')){ if(!line) continue; const d=JSON.parse(line), t=d.c;
  const f=k=>{const m=t.match(new RegExp('^\\|'+k+'=(.*)$','m')); return m?m[1].trim():'';};
  if(!['AA','A','B'].includes(f('sroddenrating'))) continue;
  const cats=[...t.matchAll(/\{\{ASTRODATABANK_cat([\s\S]*?)\}\}/g)].map(m=>m[1]);
  let hm=null,kg=null;
  for(const b of cats){const sc=(b.match(/\|scat=(.*)/)||[])[1]||'', n=((b.match(/\|CategoryNotes=(.*)/)||[])[1]||'').toLowerCase();
    if(sc.trim()==='Traits : Body : Size'){const m=n.match(/(\d\.\d\d)\s*m\b/); if(m) hm=+m[1];}
    if(sc.trim()==='Traits : Body : Weight'){const m=n.match(/(\d{2,3})\s*kg/); if(m) kg=+m[1];}}
  if(!hm||hm<1.3||hm>2.3) continue;
  const sbli=f('sbli').split(','); if(sbli.length<8) continue; const m=sbli[7].match(/^h(\d+)([ew])(\d*)$/); if(!m) continue;
  const dt=f('sbdate'), tm=f('sbtime'); if(!/^\d{4}\/\d\d\/\d\d$/.test(dt)||!/^\d\d:\d\d$/.test(tm)) continue;
  const deg=s=>{const q=s.match(/(\d+)([nsew])(\d+)/); if(!q) return null; const v=+q[1]+ +q[3]/60; return 'sw'.includes(q[2])?-v:v;};
  const lat=deg(f('slati')), lon=deg(f('slong')); if(lat==null||lon==null) continue;
  const [y,mo,dd]=dt.split('/').map(Number), [h,mi]=tm.split(':').map(Number);
  rows.push({name:d.t,y,mo,d:dd,h,mi,s:0,tz:(+m[1]+(m[3]?+m[3]/60:0))*(m[2]==='e'?1:-1),lat,lon,gender:sbli[2]==='f'?'F':'M',hm,kg,
    half:parseInt(crypto.createHash('md5').update(d.t).digest('hex').slice(-1),16)%2?'B':'A'});
}
console.error('people with height',rows.length,'with weight',rows.filter(r=>r.kg).length);
// standardise within sex x birth decade
function z(key,val){const g={}; for(const r of rows){const v=val(r); if(v==null) continue; const k=r.gender+Math.floor(r.y/10); (g[k]=g[k]||[]).push(v);}
  const st={}; for(const [k,a] of Object.entries(g)){const m=a.reduce((x,y)=>x+y,0)/a.length, s=Math.sqrt(a.reduce((x,y)=>x+(y-m)**2,0)/a.length)||1; st[k]=[m,s,a.length];}
  for(const r of rows){const v=val(r); const k=r.gender+Math.floor(r.y/10); r[key]=(v!=null&&st[k][2]>=10)?(v-st[k][0])/st[k][1]:null;}}
z('hz',r=>r.hm); z('bz',r=>r.kg?r.kg/r.hm**2:null);
const CLS=[-1,-1,0,0,1,1,1,1,0,0,-1,-1]; // hrasva/sama/dirgha
const DS=J.DIGNITY_SCORE;
for(const r of rows){ try{ const c=new J.Chart(r,{}); const pr=J.profiles(c).self_appearance.traits;
  r.engH=pr.height.score; r.engB=pr.build.score; const L=J.SIGN_LORD[c.lagna];
  const F={lagna_class:CLS[c.lagna], lagnalord_sign_class:CLS[c.sign[L]], moon_sign_class:CLS[c.moonSign], d9_lagna_class:CLS[c.vargas[9].Lagna], lagnalord_dignity:DS[c.dig[L]]??0};
  for(const p of J.PLANETS) F['in_lagna_'+p]=c.occupants(1).includes(p)?1:0;
  const asp=c.aspectedBy(1,true); for(const p of ['Jupiter','Saturn','Mars']) F['aspects_lagna_'+p]=asp.includes(p)?1:0;
  r.F=F; }catch(e){ r.bad=1; } }
fs.writeFileSync('body_rows.json',JSON.stringify(rows.filter(r=>!r.bad)));
