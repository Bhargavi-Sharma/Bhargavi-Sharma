import json, urllib.request, urllib.parse, time, os, gzip
API="https://www.astro.com/wiki/astro-databank/api.php"
def get(params):
    url=API+"?"+urllib.parse.urlencode({**params,"format":"json"})
    for i in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"research-script (non-commercial study)"}),timeout=90) as r: return json.load(r)
        except Exception as e: time.sleep(2**i)
    return None
state=json.load(open("all_state.json")) if os.path.exists("all_state.json") else {"cont":{},"n":0}
out=open("all_pages.jsonl","a")
p={"action":"query","generator":"allpages","gapnamespace":"0","gaplimit":"50","prop":"revisions","rvprop":"content"}
while True:
    d=get({**p,**state["cont"]})
    if d is None: print("give up at",state); break
    for pg in d.get("query",{}).get("pages",{}).values():
        if "revisions" in pg: out.write(json.dumps({"t":pg["title"],"c":pg["revisions"][0]["*"]})+"\n"); state["n"]+=1
    out.flush()
    if "continue" not in d: print("done",state["n"]); break
    state["cont"]={k:v for k,v in d["continue"].items()}
    json.dump(state,open("all_state.json","w"))
    time.sleep(0.4)
