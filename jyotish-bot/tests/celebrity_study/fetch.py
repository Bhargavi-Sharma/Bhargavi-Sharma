import json, urllib.request, urllib.parse, time, os
API="https://www.astro.com/wiki/astro-databank/api.php"
def get(params):
    url=API+"?"+urllib.parse.urlencode({**params,"format":"json"})
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"research-script"}),timeout=60) as r: return json.load(r)
        except Exception as e: time.sleep(2**i)
    raise SystemExit("fail "+url)
cats=["Notable : Awards : Oscar","Notable : Awards : Nobel prize","Notable : Awards : Grammy","Notable : Awards : Emmy","Notable : Awards : Olympics","Notable : Awards : Sports Championship","Notable : Awards : Knighted","Notable : Awards : Pulitzer prize","Notable : Awards : Tony"]
titles=set()
for c in cats:
    p={"action":"query","list":"categorymembers","cmtitle":"Category:"+c,"cmlimit":"500"}
    while True:
        d=get(p); titles|={m["title"] for m in d["query"]["categorymembers"]}
        if "continue" in d: p={**p,**d["continue"]}
        else: break
titles=sorted(titles); print("titles",len(titles))
out={}
json.dump(titles,open("titles.json","w"))
for i in range(0,len(titles),20):
    d=get({"action":"query","prop":"revisions","rvprop":"content","titles":"|".join(titles[i:i+20])})
    if "query" not in d: print("ERR",i,str(d)[:300]); continue
    for pg in d["query"]["pages"].values():
        if "revisions" in pg: out[pg["title"]]=pg["revisions"][0]["*"]
    time.sleep(0.3)
    if i%500==0: print(i,len(out),flush=True)
json.dump(out,open("raw.json","w")); print("pages",len(out))
