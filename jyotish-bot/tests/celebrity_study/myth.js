global.Astronomy=require(process.env.ASTRONOMY_ENGINE || 'astronomy-engine');
const J=require('../../artifact/engine-time.js');
// Julian-calendar date -> JD -> proleptic Gregorian (JS Date is Gregorian)
function julToGreg(y,m,d){ if(m<=2){y-=1;m+=12;} const jd=Math.floor(365.25*(y+4716))+Math.floor(30.6001*(m+1))+d-1524.5; const ms=(jd-2440587.5)*86400000; const t=new Date(ms); return [t.getUTCFullYear(),t.getUTCMonth()+1,t.getUTCDate()]; }
const P={
 Rama:{y:-5114,mo:1,d:10,h:12,mi:14,s:31,tz:82.2/15,lat:26.8,lon:82.2,gender:'M'},
 Krishna:(()=>{const [y,mo,d]=julToGreg(-3227,7,20); return {y,mo,d,h:0,mi:10,s:0,tz:(77+41/60)/15,lat:27.5,lon:77.68,gender:'M'};})(),
};
for (const [n,b] of Object.entries(P)) {
  const c=new J.Chart({name:n,...b},{});
  console.log('==',n,JSON.stringify(b),'lagna',J.SIGNS[c.lagna],'| Moon nak',J.nakshatraOf(c.lon.Moon).name,'| ayanamsa',J.Astro.ayanamsa? '':'' );
  console.log(J.PLANETS.map(p=>`${p} ${J.SIGNS[c.sign[p]]} ${c.dig[p]}`).join(' | '));
  const el=J.Astro.norm(c.lon.Moon-c.lon.Sun); console.log('tithi',Math.floor(el/12)+1);
}
module.exports={P};
