import json, html, os, shutil
from datetime import datetime
from site_css import CSS
from use_cases import UC
from recipes import render_recipes
C = json.load(open('data/catalog.json'))
BENCH = json.load(open('data/benchmarks.json'))
# Our own one-M5 result (strix1), read from the data so the cards and home page never drift from it.
OURS = next((r for r in BENCH['rows'] if r.get('id') == 'strix1-flash-next-iq4xs-512'), None)
OURS_DECODE = f"{OURS['decode_tok_s']:.1f}" if OURS else "Pending"
OURS_PREFILL = f"{OURS['prefill_tok_s']:,.0f}" if OURS else ""
OUT = '.'
# Never rmtree the repo root (that would delete .git, CNAME, tools, and this script).
if os.path.abspath(OUT) == os.path.abspath('.'):
    shutil.rmtree(os.path.join(OUT, 'models'), ignore_errors=True)
    os.makedirs(OUT+'/models', exist_ok=True)
    os.makedirs(OUT+'/data', exist_ok=True)
else:
    shutil.rmtree(OUT, ignore_errors=True)
    os.makedirs(OUT+'/models')
    os.makedirs(OUT+'/data')
E = html.escape
FLEET = C['fleet']; MODELS = C['models']; IDS = [f['id'] for f in FLEET]
VLABEL = {"fits":"Fits","offload":"Tight / offload","convert":"Quantize first","after-RAM-upgrade":"After 128 GB RAM","no":"No","unknown":"Unknown"}

# public copy: drop private paths
pub = json.loads(json.dumps(C))
for m in pub['models']:
    m.pop('nas_path', None); m.pop('override', None); m.pop('est_override', None)
if 'on_device' in pub:
    pub['on_device'].pop('nas_root', None)
    for i in pub['on_device']['items']:
        i.pop('nas_path', None); i['locations']=[{'machine':l['machine']} for l in i['locations']]
json.dump(pub, open(OUT+'/data/catalog.json','w'), indent=1)

open(OUT+'/style.css','w').write(CSS)

NAV = [("index.html","Overview"),("catalog.html","Catalog"),("fleet.html","Fleet & fit"),("benchmarks.html","Benchmarks"),("recipes.html","Recipes"),("use-cases.html","Use cases"),("licenses.html","Licenses")]
def page(fn, title, body, depth=0):
    pre = "../"*depth
    canon = "https://aimodels.remnantsecurity.com/" if fn == "index.html" else f"https://aimodels.remnantsecurity.com/{fn}"
    desc = "Remnant Security's local AI model archive: what we keep, what runs on which machine, and how to run it."
    nav = "".join(
        f'<a class="l{" on" if fn.endswith(h) else ""}" href="{pre}{h}"'
        f'{" aria-current=\"page\"" if fn.endswith(h) else ""}>{t}</a>'
        for h,t in NAV
    )
    open(OUT+'/'+fn,'w').write(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · Remnant AI Models</title><meta name="description" content="{E(desc)}">
<meta name="color-scheme" content="dark"><meta name="theme-color" content="#0b0d10">
<link rel="canonical" href="{canon}"><link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%230b0d10'/%3E%3Ccircle cx='32' cy='32' r='10' fill='%23e5484d'/%3E%3C/svg%3E">
<meta property="og:type" content="website"><meta property="og:site_name" content="Remnant AI Models">
<meta property="og:title" content="{E(title)} · Remnant AI Models"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{canon}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{E(title)} · Remnant AI Models"><meta name="twitter:description" content="{E(desc)}">
<link rel="stylesheet" href="{pre}style.css"></head><body>
<a class="skip" href="#main">Skip to content</a>
<header><nav class="nav" aria-label="Primary"><a class="brand" href="{pre}index.html">Remnant <span>AI Models</span></a>{nav}</nav></header>
<main id="main" tabindex="-1">{body}</main><footer>Remnant Security · Local model archive notes. Facts come from each model's Hugging Face card; speed and memory figures are estimates unless marked measured. Hardware, sources and measured results are on the <a href="{pre}benchmarks.html">Benchmarks</a> page.</footer></body></html>""")

def badge(v, cls=None): return f'<span class="b {cls or v}">{E(VLABEL.get(v,v))}</span>'
def params(m):
    t = f"{m['params_total_b']}B" if m['params_total_b'] else "unknown"
    if m['moe']: t += f" total / {str(m['params_active_b'])+'B' if m['params_active_b'] else 'unknown'} active"
    return t
def mem(m): return f"~{m['est_memory_gb']} GB" if m['est_memory_gb'] else "unknown"
def fitcell(m,i):
    f=m['fit'][i]; s=badge(f['verdict'])
    if f['est_tok_s']: s+=f'<div class="small mut">≈{f["est_tok_s"]} tok/s ceiling</div>'
    return s

SHORT = {"m5x1":"M5×1","m5x2":"M5×2","mbp":"MBP","mini":"mini","omarchy":"omarchy","nas":"NAS","neo":"Neo"}

def bench_table(rows, link_models=True):
    body=""
    for b in rows:
        if link_models and b.get('model_id'):
            model=f"<a href='models/{b['model_id']}.html'>{E(b['model'])}</a>"
        else:
            model=E(b['model'])
        prefill=f"{b['prefill_tok_s']:.0f}" if b.get('prefill_tok_s') is not None else "n/a"
        decode=f"{b['decode_tok_s']:.1f}" if b.get('decode_tok_s') is not None else "n/a"
        ttft=f"{b['ttft_s']:.2f} s" if b.get('ttft_s') is not None else "n/a"
        body+=f"""<tr><td>{model} <span class="b measured">measured</span>{' <span class="b measured">ours</span>' if b.get('ours') else ''}<div class="small mut">{E(b['machine'])} · {E(b['hardware'])} · {E(b['os'])}</div><div class="small mut">{E(b['note'])}</div></td><td data-label="Engine">{E(b['engine'])}</td><td data-label="Context">{E(b['context'])}</td><td class="num" data-label="Prefill (tok/s)">{prefill}</td><td class="num" data-label="Decode (tok/s)">{decode}</td><td class="num" data-label="TTFT">{ttft}</td><td data-label="Source"><a href="{b['source']}">source</a></td></tr>"""
    return f'<div class="wrap" tabindex="0" role="region" aria-label="Measured benchmarks, scrollable"><table class="bench-table"><caption class="sr-only">Measured benchmark results with hardware and source</caption><thead><tr><th scope="col">Model</th><th scope="col">Engine</th><th scope="col">Context</th><th scope="col">Prefill (tok/s)</th><th scope="col">Decode (tok/s)</th><th scope="col">TTFT</th><th scope="col">Source</th></tr></thead><tbody>{body}</tbody></table></div>'

def tag(m):
    return ' <span class="tag">extra</span>' if m.get('kind') == 'extra' else ''
def fit_summary(m):
    return " · ".join(f"{SHORT[i]} {VLABEL.get(m['fit'][i]['verdict'], m['fit'][i]['verdict'])}" for i in IDS)
def fmt_date(s):
    try:
        return datetime.strptime(str(s)[:10], "%Y-%m-%d").strftime("%d %b %Y")
    except Exception:
        return str(s)[:10]

OD = C.get('on_device') or {'items':[]}; ODI = OD['items']
BKP = {"copying":"NAS copy in progress","verified":"Backed up to NAS (verified)","failed":"NAS copy failed"}
def odsize(b): return f"{b/1e9:.1f} GB" if b>=1e9 else f"{b/1e6:.0f} MB"
def odbkp(i): return {"copying":'<span class="b in-progress">copying</span>',"verified":'<span class="b done">backed up</span>',"failed":'<span class="b needs-Ian">failed</span>'}.get(i['backup_status'],E(i['backup_status']))
NCLIC = ("cc-by-nc-4.0","flux-1-dev-non-commercial-license")
def odrows(items):
    r=""
    for i in sorted(items, key=lambda x:-x['size_bytes']):
        nm = f"<a href='{i['hf_url']}'>{E(i['name'])}</a>" if i.get('hf_url') else E(i['name'])
        sub = E(i['repo']) if i.get('repo') else ('Ollama library' if i['format'].startswith('Ollama') else 'local file')
        lic = E(i['license']) + (' <span class="b nc">non-commercial</span>' if i['license'] in NCLIC else '')
        note = f"<div class='small mut' style='margin-top:4px'>{E(i['notes'])}</div>" if i['notes'] else ''
        r+=f"<tr><td style='min-width:260px'>{nm}<div class='small mut'>{sub}</div>{note}</td><td>{E(i['use'])}</td><td>{E(i['format'])}</td><td style='white-space:nowrap'>{odsize(i['size_bytes'])}</td><td>{'<br>'.join(E(m) for m in i['macs'])}</td><td>{lic}<div class='small mut'>{E(i['license_source'])}</div></td><td>{odbkp(i)}</td></tr>"
    return r

# ---------- overview
cnt = {s: sum(1 for m in MODELS if m['status']==s) for s in ["done","in-progress","queued","needs-Ian"]}
tot_gib = sum(m['size_gib'] for m in MODELS if m['status']!='needs-Ian')
last_checked = fmt_date(C.get('generated',''))
mac_scan = fmt_date(OD.get('generated',''))
def can_run(m):
    return any(m['fit'][i]['verdict'] in ('fits','offload','after-RAM-upgrade') for i in ('m5x1','m5x2','mbp'))
m5 = [m for m in MODELS if 'LLM' in m['modality'] and m['kind'] != 'official' and can_run(m) and 'mirai' not in m['engine'].lower()]
RANK = {
 'qwen3-8-flash-next-gguf-ud-iq4-xs':0,
 'qwen3-8-flash-next-abliterated-gsq-rco-strata-gguf-gsq-rco':1,
 'glm-5-3-flash-gguf-ud-iq2-xxs':2,
 'gemma-4-26b-a4b-it-heretic-nsfw-gguf-selected':3,
 'mellum21-12b-a2.5b-thinking-q4km':4,
 'qwen3-8-27b-gguf-ud-q8-k-xl':5,
 'huihui-qwen3-8-27b-abliterated-gguf-q4-k':6,
 'huihui-qwen3-8-27b-abliterated-gguf-bf16':7,
 'huihui-qwen3-8-flash-next-abliterated-v2-gguf-ud-q4-k-xl':8,
 'deepseek-v4-1-flash-1017-gsq-rco-gguf-gsq-rco':9,
}
def m5rows(ids):
    r=""
    for m in sorted(m5, key=lambda x:(RANK.get(x['id'],99), -x['size_gib'])):
        r+=f"""<tr><td><a href='models/{m['id']}.html'>{E(m['family'])}</a>{tag(m)}<div class='small mut'>{E(m['quant_format'])}</div><div class='fit-line'>{E(fit_summary(m))}</div></td>
<td data-label="Est. memory">{mem(m)}</td>
<td data-label="M5 ×1">{fitcell(m,'m5x1')}</td>
<td data-label="M5 ×2">{fitcell(m,'m5x2')}</td>
<td data-label="MacBook Pro">{fitcell(m,'mbp')}</td>
<td data-label="Abliterated">{'<span class="b abl">yes</span>' if m['abliterated'] else 'no'}</td></tr>"""
    return r
pipeline = f"Pipeline: {cnt['done']} done · {cnt['in-progress']} downloading · {cnt['queued']} queued · {cnt['needs-Ian']} gated."
body = f"""<h1>Every model we keep, and where it runs.</h1>
<p class="lead">Remnant Security's local AI archive: {len(MODELS)} model builds across text, code, vision, speech, music, image, video and embeddings, about {tot_gib/1024:.1f} TiB on disk. For each one: what it is, its license, how much memory it needs, and whether it runs on our machines, including the planned Bosgame M5 boxes, one or two of them.</p>
<div class="cards stats">
<div class="card"><div class="k">Archive builds</div><div class="v">{len(MODELS)}</div><div class="small mut">{tot_gib/1024:.1f} TiB on the NAS</div></div>
<div class="card"><div class="k">Mac on-device</div><div class="v">{len(ODI)}</div><div class="small mut">{OD.get('total_unique_bytes',0)/1e9:.0f} GB backed up</div></div>
<div class="card"><div class="k">Last checked</div><div class="v">{last_checked}</div><div class="small mut">Mac scan {mac_scan}</div></div>
</div>
<p class="pipeline">{pipeline}</p>
<p class="pipeline"><span class="b measured">measured</span> <a href="benchmarks.html#measured">Our M5: {OURS_DECODE} tok/s Flash-Next decode, {OURS_PREFILL} prefill</a> · <a href="benchmarks.html">Bosgame M5 pair: 58.2 tok/s decode, 1,284 tok/s prefill (StrixFold)</a> · <a href="benchmarks.html#measured">44.0 tok/s Flash-Next on 8060S</a> · <a href="benchmarks.html#measured">18.3 tok/s GLM Maya-S</a>. Second M5 pending.</p>
<div class="start"><h2>Start here</h2><p>Three decisions cover most of the archive. The table below is the evidence; the catalog has every build and filter.</p>
<div class="picks">
<div class="pick"><span class="k">One M5</span><a href="models/qwen3-8-flash-next-gguf-ud-iq4-xs.html">Flash-Next IQ4_XS</a> or <a href="models/qwen3-8-flash-next-abliterated-gsq-rco-strata-gguf-gsq-rco.html">Strata IQ3_S</a><div class="small mut">~103 GB or ~93 GB; the fastest large model on one box.</div></div>
<div class="pick"><span class="k">Two M5s</span><a href="models/deepseek-v4-1-flash-1017-gsq-rco-gguf-gsq-rco.html">DeepSeek V4.1 IQ1_M</a> + <a href="models/huihui-qwen3-8-flash-next-abliterated-v2-gguf-ud-q4-k-xl.html">Flash-Next Q4_K_XL</a><div class="small mut">More capacity, not speed. Expect a 14-22% RPC token cost.</div></div>
<div class="pick"><span class="k">Sidecars</span><a href="models/mellum21-12b-a2.5b-thinking-q4km.html">Mellum2.1</a> for code, <a href="models/embeddinggemma-2.html">EmbeddingGemma 2</a> for RAG<div class="small mut">Small extras for the jobs the big model should not do.</div></div>
</div></div>
<h2>What matters</h2>
<ul>
<li><b>One M5 runs Qwen3.8 Flash-Next</b> (125B MoE, 6B active) at IQ4_XS or alesha's abliterated IQ3_S, and GLM-5.3-Flash (320B, 18B active) at 2-bit with little headroom.</li>
<li><b>Two M5s add capacity, not speed.</b> The Flash-Next Q4_K_XL abliterated build and DeepSeek V4.1 Flash IQ1_M fit; the 110 GB Engram table stays memory-mapped on SSD, and splitting a model over RPC costs roughly 14-22% in token generation.</li>
<li><b>Not even two M5s</b> hold the huihui DeepSeek IQ1_M build fully resident (~268 GB est.) or any original safetensors weights; those are archive copies to quantize from.</li>
<li><b>The MacBook Pro (36 GB)</b> runs Qwen3.8-27B at Q4, plus all speech and music models. The 27B BF16 row is a memory fit, not a speed recommendation.</li>
<li><b>Video</b>: Wan 2.2 A14B needs offload flags even on an M5; HunyuanVideo 1.5 (8.3B) is the lighter video option.</li>
<li><b>Extras</b>: EmbeddingGemma 2 or bge-small for private RAG, Kokoro and NeuTTS for speech, Z-Image Turbo and FLUX.1 schnell for images, SeedVR2 for upscaling, Mellum2.1 for a coding sidecar.</li>
</ul>
<h2>Bosgame M5: one box vs two</h2>
<p>One M5 is a Ryzen AI Max+ 395 with 128 GB of unified LPDDR5X at about 210-220 GB/s measured. On Linux about 108-110 GB is usable by the GPU (96 GB cap on Windows). Two boxes linked with llama.cpp RPC give roughly 200-225 GB, which adds <b>capacity, not speed</b>. Mixture-of-experts models are the sweet spot because only the active experts are read per token.</p>
<p class="small mut">Showing the {len(m5)} LLM builds that run on at least one target. The <a href="catalog.html">catalog</a> has all {len(MODELS)} builds and every filter.</p>
<div class="wrap"><table class="fit-table"><caption class="sr-only">LLM builds and their fit on one M5, two M5s, and the MacBook Pro</caption>
<thead><tr><th scope="col">Build</th><th scope="col">Est. memory (GB)</th><th scope="col">M5 ×1</th><th scope="col">M5 ×2</th><th scope="col">MacBook Pro M4 Max</th><th scope="col">Abliterated</th></tr></thead>
<tbody>{m5rows(['m5x1','m5x2','mbp'])}</tbody></table></div>
<p class="small mut">Token/s figures are theoretical ceilings (bandwidth ÷ bytes of active weights per token), not measurements. Real speed is usually well below. See <a href="fleet.html#method">method</a>; measured results are on the <a href="benchmarks.html">Benchmarks</a> page. Orange “Tight / offload” and purple “After 128 GB RAM” are not the same as green “Fits”.</p>
<p class="note">Two engines matter: alesha-pro's Mirai and Maya builds need their own forked engines (mainline llama.cpp, LM Studio and Ollama will not load them), and Maya/Strata builds can't be split across two boxes with llama.cpp RPC. Mirai is CUDA-only, so it is not a practical M5 model.</p>"""
page("index.html","Overview",body)

# ---------- catalog
def ondevice_section():
    if not ODI: return ""
    per = {}
    for i in ODI:
        for m in i['macs']: per.setdefault(m,[0,0]); per[m][0]+=1; per[m][1]+=i['size_bytes']
    cards = "".join(f'<div class="card"><div class="k">{E(m)}</div><div class="v">{n}</div><div class="small mut">models, {b/1e9:.0f} GB</div></div>' for m,(n,b) in per.items())
    st = {s: sum(1 for i in ODI if i['backup_status']==s) for s in BKP}
    stline = "; ".join(f"{BKP[s]}: {n}" for s,n in st.items() if n)
    if ODI and all(i['backup_status']=='verified' for i in ODI):
        copy_sentence = "Each one was copied once to the NAS's WD drive (a model on both Macs is stored a single time) and the copy has been verified."
    elif any(i.get('backup_status')=='copying' for i in ODI):
        copy_sentence = "Each one is being copied once to the NAS's WD drive, so a model on both Macs is backed up a single time."
    else:
        copy_sentence = "Each one is copied once to the NAS's WD drive, so a model on both Macs is backed up a single time."
    remote = "".join(f"<li><b>{E(r['name'])}</b> on the {E(r['machine'])}: {E(r['note'])}.</li>" for r in OD.get('remote_only',[]))
    nos = "".join(f"<li>{E(r['machine'])}: {E(r['why'])}.</li>" for r in OD.get('not_scanned',[]))
    nw = "".join(f"<li>{E(x)}</li>" for x in OD.get('no_weights',[]))
    return f"""<p class="lead">Models already sitting on the MacBook Pro and the Mac mini, scanned {E(OD['generated'])}. {len(ODI)} unique models, {OD['total_unique_bytes']/1e9:.0f} GB. {copy_sentence} Backup status: {stline}.</p>
<div class="cards">{cards}<div class="card"><div class="k">Unique total</div><div class="v">{OD['total_unique_bytes']/1e9:.0f} GB</div><div class="small mut">duplicates counted once</div></div></div>
<div class="wrap" tabindex="0" role="region" aria-label="On-device models table, scrollable"><table class="od-table"><caption class="sr-only">Models stored on the Macs and backed up to the NAS</caption><thead><tr><th scope="col">Model</th><th scope="col">Use</th><th scope="col">Format</th><th scope="col">Size (GB)</th><th scope="col">On</th><th scope="col">License</th><th scope="col">NAS backup</th></tr></thead><tbody>{odrows(ODI)}</tbody></table></div>
<p class="small mut">Sizes are measured on the Macs in decimal GB. Licenses come from the Hugging Face card metadata, the GGUF file's own metadata, or the Ollama license layer, as noted under each one; "unknown" means no source states it. Full local and NAS paths are kept in the private catalog, not on this site.</p>
<h3>Not local weights</h3><ul>{remote}</ul>
<h3>Not scanned yet</h3><ul>{nos}</ul>
<h3>Checked, nothing to back up</h3><ul>{nw}</ul>"""

def ondevice_details():
    if not ODI: return ""
    return f'<details class="ondevice" id="on-device"><summary><span>On-device (Mac) models</span><span>{len(ODI)} models · {OD["total_unique_bytes"]/1e9:.0f} GB · backup verified</span></summary><h2 class="sr-only">On-device (Mac) models</h2>{ondevice_section()}</details>'

rows=""
for m in MODELS:
    fitattr = " ".join(f"data-{i}='{m['fit'][i]['verdict']}'" for i in IDS)
    rows+=f"""<tr data-mod="{E(m['modality'])}" data-lic="{E(m['license'])}" data-abl="{'yes' if m['abliterated'] else 'no'}" data-status="{m['status']}" {fitattr} data-q="{E((m['repo']+' '+m['family']).lower())}">
<td><a href="models/{m['id']}.html">{E(m['family'])}</a>{tag(m)}<div class="small mut">{E(m['repo'])}</div><div class="fit-line">{E(fit_summary(m))}</div></td>
<td data-label="Modality">{E(m['modality'])}</td>
<td class="col-opt" data-label="Format">{E(m['quant_format'])}</td>
<td class="col-opt" data-label="Params">{params(m)}</td>
<td class="num" data-label="Size (GiB)">{m['size_gib']} GiB</td>
<td data-label="Est. memory">{mem(m)}</td>
<td data-label="License">{E(m['license'])}{' <span class="b nc">non-commercial</span>' if m['non_commercial'] else ''}</td>
<td class="col-opt" data-label="Abliterated">{'<span class="b abl">abliterated</span>' if m['abliterated'] else 'no'}</td>
<td class="col-opt" data-label="Status">{badge(m['status'])}</td>
<td data-label="M5 ×1">{badge(m['fit']['m5x1']['verdict'])}</td>
<td data-label="M5 ×2">{badge(m['fit']['m5x2']['verdict'])}</td></tr>"""
opts=lambda vals: "".join(f"<option>{E(v)}</option>" for v in sorted(set(vals)))
n_prog = sum(1 for m in MODELS if m['status']=='in-progress')
n_queue = sum(1 for m in MODELS if m['status']=='queued')
n_gated = sum(1 for m in MODELS if m['status']=='needs-Ian')
_bits = []
if n_prog: _bits.append(f"{n_prog} still downloading")
if n_queue: _bits.append(f"{n_queue} queued")
if n_gated: _bits.append(f"{n_gated} gated repo{'s' if n_gated!=1 else ''} waiting on a Hugging Face sign-in")
catalog_lead = ("Including " + ", and ".join(_bits) + ". ") if _bits else "Every listed build is on the NAS. "
body=f"""<h1>Full catalog</h1><p class="lead">All {len(MODELS)} builds. {catalog_lead}Filter by modality, license, abliteration, or which machine it fits.</p>
<h2>Archive builds</h2>
<div class="filters" role="search" aria-label="Filter the archive builds">
<label class="filter" for="q"><span>Search</span><input id="q" type="search" placeholder="Name, repo or family" autocomplete="off"></label>
<label class="filter" for="mod"><span>Modality</span><select id="mod"><option value="">All modalities</option>{opts(m['modality'] for m in MODELS)}</select></label>
<label class="filter" for="lic"><span>License</span><select id="lic"><option value="">All licenses</option>{opts(m['license'] for m in MODELS)}<option value="__nc">Non-commercial only</option></select></label>
<label class="filter" for="fit"><span>Fits on</span><select id="fit"><option value="">Any machine</option>{''.join(f'<option value="{f["id"]}">{E(f["name"])}</option>' for f in FLEET)}</select></label>
<label class="filter" for="abl"><span>Abliterated</span><select id="abl"><option value="">Any</option><option value="yes">Abliterated only</option><option value="no">Not abliterated</option></select></label>
<label class="filter" for="st"><span>Status</span><select id="st"><option value="">Any status</option><option>done</option><option>in-progress</option><option>queued</option><option>needs-Ian</option></select></label>
<div class="filter-actions"><button class="btn" id="clear" type="button">Clear filters</button><button class="btn" id="cols" type="button" aria-pressed="false">Show all columns</button><button class="btn" id="copy" type="button">Copy link</button></div>
</div>
<p class="small mut" id="count" role="status" aria-live="polite"></p>
<p class="scroll-hint" id="hint">Scroll inside the table to see all 39 rows.</p>
<div class="table-scroll" tabindex="0" role="region" aria-label="Archive builds table, scrollable"><table id="t" class="catalog-table"><caption class="sr-only">All archive builds, filterable by modality, license, abliteration, machine fit and status</caption>
<thead><tr><th scope="col">Model</th><th scope="col">Modality</th><th scope="col" class="col-opt">Format</th><th scope="col" class="col-opt">Params</th><th scope="col">Size (GiB)</th><th scope="col">Est. memory (GB)</th><th scope="col">License</th><th scope="col" class="col-opt">Abliterated</th><th scope="col" class="col-opt">Status</th><th scope="col">M5 ×1</th><th scope="col">M5 ×2</th></tr></thead>
<tbody>{rows}<tr id="empty" hidden><td colspan="11">No builds match those filters. <button class="btn" id="clear2" type="button">Clear filters</button></td></tr></tbody></table></div>
<p class="small mut">"needs-Ian" = gated repo; the owner has to accept the publisher's terms on Hugging Face first. Machine-readable: <a href="data/catalog.json">data/catalog.json</a>.</p>
{ondevice_details()}
<script>
const NC={json.dumps([m['license'] for m in MODELS if m['non_commercial']])};
const $=id=>document.getElementById(id);
const rows=[...document.querySelectorAll('#t tbody tr[data-mod]')];
const total=rows.length;
const params=new URLSearchParams(location.search);
const keys=['q','mod','lic','abl','fit','st'];
for(const k of keys){{const v=params.get(k);if(v!==null)$(k).value=v;}}
function apply(push){{
  let n=0;const q=$('q').value.toLowerCase(),mo=$('mod').value,li=$('lic').value,ab=$('abl').value,fm=$('fit').value,st=$('st').value;
  for(const r of rows){{
    let ok=(!q||r.dataset.q.includes(q))&&(!mo||r.dataset.mod==mo)&&(!ab||r.dataset.abl==ab)&&(!st||r.dataset.status==st);
    if(li==='__nc')ok=ok&&NC.includes(r.dataset.lic);else if(li)ok=ok&&r.dataset.lic==li;
    if(fm){{const v=r.getAttribute('data-'+fm);ok=ok&&(v==='fits'||v==='offload'||v==='after-RAM-upgrade');}}
    r.hidden=!ok;if(ok)n++;
  }}
  $('empty').hidden=n!==0;
  $('count').textContent=n+' of '+total+' builds shown'+(fm?' · machine filter includes fits, offload and after-RAM-upgrade':'');
  $('hint').hidden=n<=8;
  document.body.classList.toggle('filter-machine',!!fm);
  if(push){{
    const p=new URLSearchParams();
    if(q)p.set('q',q);if(mo)p.set('mod',mo);if(li)p.set('lic',li);if(ab)p.set('abl',ab);if(fm)p.set('fit',fm);if(st)p.set('st',st);
    const url=p.toString()?location.pathname+'?'+p.toString():location.pathname;
    history.replaceState(null,'',url);
  }}
}}
for(const k of ['q','mod','lic','abl','fit','st'])$(k).addEventListener('input',()=>apply(true));
$('clear').addEventListener('click',()=>{{for(const k of ['q','mod','lic','abl','fit','st'])$(k).value='';apply(true);}});
$('clear2').addEventListener('click',()=>{{for(const k of ['q','mod','lic','abl','fit','st'])$(k).value='';apply(true);}});
$('cols').addEventListener('click',()=>{{const on=document.body.classList.toggle('show-all');$('cols').setAttribute('aria-pressed',on);$('cols').textContent=on?'Show fewer columns':'Show all columns';}});
$('copy').addEventListener('click',async()=>{{try{{await navigator.clipboard.writeText(location.href);$('copy').textContent='Copied';setTimeout(()=>$('copy').textContent='Copy link',1400);}}catch(e){{$('copy').textContent='Copy failed';}}}});
if(location.hash==='#on-device'){{const d=$('on-device');if(d)d.open=true;}}
apply(false);
</script>"""
page("catalog.html","Catalog",body)
# ---------- model detail pages
RECIPE_HINT = {
 "llama.cpp": "recipes.html#llamacpp", "Strata":"recipes.html#forks", "ONLY":"recipes.html#forks", "Transformers":"recipes.html#convert",
 "vLLM":"recipes.html#convert", "Diffusers":"recipes.html#image", "ComfyUI":"recipes.html#comfyui","Wan2.2":"recipes.html#video",
 "HunyuanVideo":"recipes.html#video","qwen-tts":"recipes.html#voice","fish-speech":"recipes.html#voice","whisper":"recipes.html#voice","ACE-Step":"recipes.html#music"}
for m in MODELS:
    hint = next((v for k,v in RECIPE_HINT.items() if k.lower() in m['engine'].lower()), "recipes.html")
    fr = "".join(f"<tr><th scope='row'>{E(f['name'])}</th><td>{fitcell(m,f['id'])}</td><td class='small mut'>{E(f['budget_note'])}</td></tr>" for f in FLEET)
    bm = [b for b in BENCH['rows'] if b.get('model_id') == m['id']]
    bench_html = bench_table(bm, link_models=False) if bm else '<p class="note">No measured benchmark for this build yet. The token/s figures above are estimates; the <a href="../benchmarks.html">Benchmarks page</a> has measured results for the closest builds and hardware.</p>'
    body=f"""<p class="small"><a href="../catalog.html">← Catalog</a></p><h1>{E(m['family'])}</h1><p class="lead">{E(m['quant_format'])} · <a href="{m['hf_url']}">{E(m['repo'])}</a>{tag(m)}</p>
<p>{badge(m['status'])} {'<span class="b abl">abliterated</span>' if m['abliterated'] else ''} {'<span class="b nc">non-commercial</span>' if m['non_commercial'] else ''}</p>
<div class="wrap"><table>
<tr><th scope="row" style="width:220px">Publisher</th><td>{E(m['publisher'])}</td></tr><tr><th scope="row">Modality</th><td>{E(m['modality'])}</td></tr>
<tr><th scope="row">Parameters</th><td>{params(m)}<div class="small mut">{E(m['params_note'])} Source: <a href="{m['params_source']}">model card</a>.</div></td></tr>
<tr><th scope="row">Format</th><td>{E(m['quant_format'])}</td></tr><tr><th scope="row">Size on disk</th><td>{m['size_gib']} GiB ({m['size_bytes']:,} bytes)</td></tr>
<tr><th scope="row">Estimated memory to run</th><td>{mem(m)} <span class="small mut">(estimate; see method)</span>{'<div class="small mut">'+E(m['fit_note'])+'</div>' if m.get('fit_note') else ''}</td></tr>
<tr><th scope="row">Native context</th><td>{f"{m['context_native']:,} tokens (config/card)" if m['context_native'] else 'n/a'}</td></tr>
<tr><th scope="row">Engine</th><td>{E(m['engine'])} · <a href="../{hint}">recipe</a></td></tr>
<tr><th scope="row">License</th><td>{E(m['license'])}<div class="small mut">{E(m['license_note'])}</div></td></tr>
<tr><th scope="row">Archive folder</th><td><code>{E(m['public_folder'])}</code></td></tr>
<tr><th scope="row">Notes</th><td>{E(m['notes'])}</td></tr></table></div>
{'<p class="note danger">Abliterated model: refusal behaviour was removed or suppressed by a third party. Use it only for lawful research on systems you own or are authorised to test, keep it off public endpoints, and you own whatever it produces. See <a href="../licenses.html#abliterated">responsibility note</a>.</p>' if m['abliterated'] else ''}
<h2>Where it runs</h2><div class="wrap"><table><caption class="sr-only">Fit verdicts for this model on every machine</caption><thead><tr><th scope="col">Machine</th><th scope="col">Verdict</th><th scope="col">Budget used</th></tr></thead><tbody>{fr}</tbody></table></div>
<p class="small mut">Token/s = theoretical ceiling from memory bandwidth and active weight bytes; not a benchmark. Nothing on this page is a benchmark score.</p>
<h2>Benchmarks</h2>{bench_html}"""
    page(f"models/{m['id']}.html", m['family'], body, depth=1)

# ---------- fleet
fl="".join(f"<tr><td data-label=\"Machine\"><b>{E(f['name'])}</b><div class='small mut'>{E(f['status'])}</div></td><td data-label=\"CPU\">{E(f['cpu'])}</td><td data-label=\"GPU\">{E(f['gpu'])}</td><td data-label=\"Memory\">{E(f['ram'])}</td><td data-label=\"Bandwidth\">{E(f['bw_note'])}</td><td data-label=\"Fit budget\" class='small'>{E(f['budget_note'])}</td></tr>" for f in FLEET)
mx="".join(f"<tr><td><a href='models/{m['id']}.html'>{E(m['family'])}</a>{tag(m)}<div class='small mut'>{E(m['quant_format'][:48])}</div></td><td>{mem(m)}</td>"+"".join(f"<td>{fitcell(m,i)}</td>" for i in IDS)+"</tr>" for m in MODELS)
legend = ('<p class="small mut">'
 '<span class="b fits">Fits</span> fits the machine budget · '
 '<span class="b offload">Tight / offload</span> needs CPU/RAM offload or raised limits · '
 '<span class="b after-RAM-upgrade">After 128 GB RAM</span> omarchy only · '
 '<span class="b convert">Quantize first</span> original weights · '
 '<span class="b no">No</span> does not fit.</p>')
body=f"""<h1>Fleet and fit matrix</h1><p class="lead">Which model runs on which machine. This is the canonical matrix; the overview is a shortlist and the catalog is the filterable index.</p>
<div class="wrap" tabindex="0" role="region" aria-label="Machine specifications, scrollable"><table class="machine-table"><caption class="sr-only">Every archive build against every machine</caption><thead><tr><th scope="col">Machine</th><th scope="col">CPU</th><th scope="col">GPU</th><th scope="col">Memory</th><th scope="col">Bandwidth</th><th scope="col">Fit budget used</th></tr></thead><tbody>{fl}</tbody></table></div>
<p class="note">Unknown specs stay unknown: the MacBook Neo was unreachable, and omarchy's current RAM isn't recorded (a 4×32 GB upgrade is planned). Those columns will change once the specs are read.</p>
<h2 id="holds">What each machine already holds</h2>{{holds_html}}
<h2>Matrix</h2>
{legend}
<p class="scroll-hint">Swipe sideways for the remaining machines; scroll down for more models. →</p>
<div class="table-scroll" tabindex="0" role="region" aria-label="Fleet fit matrix, scrollable"><table class="fleet-table"><caption class="sr-only">Fit verdicts for every model on every machine</caption><thead><tr><th scope="col">Model</th><th scope="col">Est. memory (GB)</th>{''.join(f'<th scope="col">{E(f["name"])}</th>' for f in FLEET)}</tr></thead><tbody>{mx}</tbody></table></div>
<h2 id="method">Method</h2><ul>{''.join(f'<li><b>{E(k)}</b>: {E(v)}</li>' for k,v in C['method'].items())}</ul>
<p class="small mut">Diffusion, TTS and embedding models don't split across two boxes, so the M5 ×2 column for them means "on either box". Maya, Mirai and Strata builds use forked engines without llama.cpp RPC, so they get "No" on M5 ×2 unless they already fit one box.</p>"""
def holds():
    rows=""
    rows+=f"<tr><td><b>Ugreen DXP2800 NAS</b></td><td>The {len(MODELS)}-build archive plus a backup of the Mac models</td><td class='small'>See the <a href='catalog.html'>catalog</a>. Storage only; it doesn't run these.</td></tr>"
    for mac in OD.get('scanned',[]):
        its=[i for i in ODI if mac in i['macs']]
        if not its: continue
        names=", ".join(E(i['name']) for i in sorted(its,key=lambda x:-x['size_bytes']))
        rows+=f"<tr><td><b>{E(mac)}</b></td><td>{len(its)} models, {sum(i['size_bytes'] for i in its)/1e9:.0f} GB</td><td class='small'>{names}. <a href='catalog.html#on-device'>Details</a></td></tr>"
    for r in OD.get('not_scanned',[]):
        rows+=f"<tr><td><b>{E(r['machine'])}</b></td><td>not scanned</td><td class='small mut'>{E(r['why'])}.</td></tr>"
    rows+="<tr><td><b>Bosgame M5 (x1 / x2)</b></td><td>planned</td><td class='small mut'>Would load from the NAS archive.</td></tr>"
    return f"<div class='wrap'><table><caption class='sr-only'>Machines and what they hold</caption><thead><tr><th scope='col'>Machine</th><th scope='col'>Holds</th><th scope='col'>What</th></tr></thead><tbody>{rows}</tbody></table></div>"
page("fleet.html","Fleet & fit",body.replace("{holds_html}", holds()))

# ---------- benchmarks
measured = BENCH['rows']
pending = BENCH['pending']
pending_html = "".join(f'<div class="pick"><span class="k">{E(p["machine"])}</span>{E(p["reason"])}</div>' for p in pending)
body=f"""<h1>Benchmarks</h1><p class="lead">Measured prefill and decode speed, with the hardware and the source. The first rows are ours: our own Bosgame M5 (strix1), measured on 23 Nov 2026, with the raw run linked as the source. The rest are the best published measurements on M5-class hardware, plus Windows, Linux and CUDA references.</p>
<div class="cards stats">
<div class="card"><div class="k">Measured rows</div><div class="v">{len(measured)}</div><div class="small mut">ours plus published sources</div></div>
<div class="card"><div class="k">Bosgame M5 pair</div><div class="v">58.2</div><div class="small mut">decode tok/s; 1,284 prefill</div></div>
<div class="card"><div class="k">Our M5 (strix1)</div><div class="v">{OURS_DECODE}</div><div class="small mut">decode tok/s, Flash-Next IQ4_XS; {OURS_PREFILL} prefill</div></div>
</div>
<p class="note"><b>StrixFold</b> measured two Bosgame M5 pairs and a pair of Ryzen AI Halo boxes over USB4. <b>TensorFold</b> measured a single Strix Halo on ROCm. Neither is our hardware; our first M5 is measured in the rows marked ours. The site's token/s figures are theoretical ceilings; this page is the measured counterpart.</p>
<h2 id="measured">Measured</h2>
<p><b>StrixFold</b> is the two-box HIP fork of TensorFold; the M5 pair rows are third-party measurements on actual Bosgame M5s. <b>TensorFold</b> rows are its ROCm benchmark receipts on a single Strix Halo.</p>
<p class="small mut">Updated {E(BENCH['generated'])}. Prefill is prompt processing speed; decode is token generation speed; TTFT is time to first token. Context matters, so the context column is part of the result.</p>
{bench_table(measured)}
<p class="small mut">Method: {E(BENCH['method'])} Machine-readable: <a href="data/benchmarks.json">data/benchmarks.json</a>.</p>
<h2 id="prefill-decode">Prefill and decode</h2>
<p><b>Prefill</b> is how fast the model reads the prompt; it sets the time to first token and the cost of a long context. <b>Decode</b> is how fast it writes the answer; it sets sustained output. They are separate measurements, and a single “tokens per second” number without a label is ambiguous.</p>
<p>StrixFold reports both, so its M5 rows have both columns. TensorFold’s issue #1001 reports stream-delivery decode only; its prefill cells are <b>n/a</b> because the source did not measure them. That is a missing measurement, not a zero. The same applies to the coding and 8K rows from Strata.</p>
<h2 id="estimates">Measured vs estimated</h2>
<p>A green <span class="b fits">Fits</span> on the fleet matrix is a memory-fit verdict, not a speed claim. The <code>≈ tok/s ceiling</code> under it is bandwidth divided by active weight bytes. A model can fit and still be unpleasant at 4 tok/s; the 27B BF16 row is the obvious example. The measured table above is what happened on real hardware.</p>
<h2 id="pending">What is still missing</h2>
<div class="picks">{pending_html}</div>
<h2 id="plan">The benchmark plan</h2>
<p>Run the same commands on both boxes, at the same context, with the same build. Record the command, the model revision, the driver or ROCm version and the room temperature; a number without those is not a benchmark. The one-M5 commands below produced the strix1 rows; <a href="data/runs/strix1-2026-11-23.md">the receipt</a> records the build, ROCm and kernel, and says what was not recorded (room temperature, power).</p>
<pre><code># One M5, after the one-box set is copied
llama-bench -m /models/official/unsloth-Qwen3.8-Flash-Next-UD-IQ4_XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00004.gguf -p 512 -n 128 -ngl 99 -r 3

# Same build, longer prompt; this is where KV cache and prefill show up
llama-bench -m /models/.../Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00004.gguf -p 8192 -n 128 -ngl 99 -r 3

# Two boxes, after rpc-server is running on box B
rpc-server -H 192.168.12.72 -p 50052
llama-bench -m /models/.../DeepSeek-V4.1-Flash-1017-GSQ-RCO-IQ1_M-00001-of-00006.gguf --rpc 192.168.12.72:50052 -p 512 -n 128 -ngl 99 -r 2</code></pre>
<p class="small mut">Measure load time separately. The first token after a 16K prompt is not the same as steady-state decode, and a two-box result should report the link and the split.</p>
<h2 id="not">What this page is not</h2>
<ul><li>Not only ours: rows marked ours link our raw run; every other row links to the person or project that measured it.</li><li>Not a quality score. Speed says nothing about answer quality.</li><li>Not a comparison across different prompts. The context column is part of the number.</li><li>Not final. One M5 is measured; the second box, the pair over RPC and longer contexts come next.</li></ul>"""
page("benchmarks.html","Benchmarks",body)

# ---------- recipes
body = render_recipes()
page("recipes.html","Recipes",body)

# ---------- use cases
body="<h1>Use cases</h1><p class='lead'>What this archive is for, and which machine to use.</p><h2>What the archive is for</h2>"+"".join(f"<div class='card' style='margin:14px 0'><h3 style='margin-top:0'>{E(a)}</h3><p>{E(b)}</p><p><b>Where:</b> {E(c)}</p><p class='small mut'>{E(d)}</p></div>" for a,b,c,d in UC)
page("use-cases.html","Use cases",body)

# ---------- licenses
lr="".join(f"<tr><td><a href='models/{m['id']}.html'>{E(m['family'])}</a>{tag(m)}<div class='small mut'>{E(m['repo'])}</div></td><td>{E(m['license'])}</td><td>{'<span class=\"b nc\">non-commercial</span> ' if m['non_commercial'] else ''}{E(m['license_note'])}</td></tr>" for m in MODELS)
body=f"""<h1>Licenses and responsibility</h1><p class="lead">License names come from each repo's Hugging Face card metadata. This is a summary, not legal advice: read the actual license before shipping anything.</p>
<p class="note danger"><b>Non-commercial:</b> Qwen-Image 2.1 (Qwen Research License), YuE2 (CC BY-NC 4.0) and Fish Audio S2 Pro (Fish Audio Research License) can't be used in anything sold without a separate license. HunyuanVideo 1.5's license doesn't apply in the EU, UK or South Korea.</p>
<h2 id="abliterated">Abliterated models</h2><p>Abliterated builds (huihui-ai, alesha-pro) have had refusal behaviour removed or suppressed by third parties, either baked into the weights or applied with a control vector at run time. They inherit the base model's license. They will answer requests that the original would refuse, so:</p>
<ul><li>Use them for lawful, authorised work only: defensive research, testing your own systems, red-team prep with written scope.</li><li>Don't expose them on a public endpoint or share access.</li><li>Review outputs before acting on them; you are responsible for what you do with them.</li><li>They are community conversions, not official releases, and their quality can differ from the original.</li></ul>
<h2>Every model</h2><div class="wrap"><table><caption class="sr-only">Every build and its license summary</caption><thead><tr><th scope="col">Model</th><th scope="col">License</th><th scope="col">Summary</th></tr></thead><tbody>{lr}</tbody></table></div>"""
page("licenses.html","Licenses",body)

# Do not rewrite CNAME or README on each build: CNAME is the custom domain
# file (leave the existing bytes alone) and README is hand-maintained
# (it documents scripts/sync-catalog).
if not os.path.exists(OUT+'/CNAME'):
    open(OUT+'/CNAME','w').write("aimodels.remnantsecurity.com\n")
open(OUT+'/robots.txt','w').write("User-agent: *\nAllow: /\n")
if not os.path.exists(OUT+'/.nojekyll'):
    open(OUT+'/.nojekyll','w').write("")

print("pages:", sum(len(f) for _,_,f in os.walk(OUT)))
