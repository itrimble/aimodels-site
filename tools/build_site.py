import json, html, os, shutil
C = json.load(open('data/catalog.json'))
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

CSS = """
:root{--bg:#0b0d10;--panel:#12161b;--line:#222a33;--txt:#e6e9ee;--mut:#9aa4b1;--acc:#e5484d;--ok:#30a46c;--warn:#f5a524;--no:#6b7280;--blue:#3e9bff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
header{border-bottom:1px solid var(--line);background:#0e1115;position:sticky;top:0;z-index:5}
.nav{max-width:1200px;margin:auto;display:flex;gap:22px;align-items:center;padding:14px 20px;flex-wrap:wrap}
.brand{font-weight:700;color:var(--txt);letter-spacing:.2px}.brand span{color:var(--acc)}
.nav a.l{color:var(--mut)}.nav a.l.on,.nav a.l:hover{color:var(--txt);text-decoration:none}
main{max-width:1200px;margin:auto;padding:28px 20px 60px}
h1{font-size:34px;line-height:1.2;margin:8px 0 10px}h2{margin-top:38px;font-size:22px}h3{margin-top:26px}
.lead{color:var(--mut);font-size:17px;max-width:820px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin:18px 0}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
.card .k{color:var(--mut);font-size:13px}.card .v{font-size:26px;font-weight:700}
table{width:100%;border-collapse:collapse;font-size:14px;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}th{color:var(--mut);font-weight:600;background:#0f1318;position:sticky;top:0}
.wrap{overflow-x:auto;border-radius:10px}
.b{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.fits{background:#12301f;color:#5be39b}.offload{background:#33280f;color:var(--warn)}.no{background:#1c1f24;color:var(--no)}.unknown{background:#1c1f24;color:#a3a3a3;border:1px dashed #3a3f46}
.convert{background:#122335;color:#7cc0ff}.after-RAM-upgrade{background:#2a1f35;color:#c79bff}
.done{background:#12301f;color:#5be39b}.in-progress{background:#122335;color:#7cc0ff}.queued{background:#1c1f24;color:#c7cdd4}.needs-Ian{background:#3a1416;color:#ff8b8f}
.nc{background:#3a1416;color:#ff8b8f}.abl{background:#2a1f35;color:#c79bff}
pre{background:#07090b;border:1px solid var(--line);border-radius:10px;padding:14px;overflow-x:auto;font-size:13px;line-height:1.5}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}
.filters{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0}.filters select,.filters input{background:var(--panel);color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:7px 10px}
.note{border-left:3px solid var(--warn);background:#16130b;padding:10px 14px;border-radius:6px;color:#e9dcc0}
.danger{border-left-color:var(--acc);background:#170c0d;color:#f2d0d1}
footer{border-top:1px solid var(--line);color:var(--mut);font-size:13px;padding:20px;text-align:center}
.mut{color:var(--mut)}.small{font-size:13px}
"""
open(OUT+'/style.css','w').write(CSS)

NAV = [("index.html","Overview"),("catalog.html","Catalog"),("fleet.html","Fleet & fit"),("recipes.html","Recipes"),("use-cases.html","Use cases"),("licenses.html","Licenses")]
def page(fn, title, body, depth=0):
    pre = "../"*depth
    nav = "".join(f'<a class="l{" on" if fn.endswith(h) else ""}" href="{pre}{h}">{t}</a>' for h,t in NAV)
    open(OUT+'/'+fn,'w').write(f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)} · Remnant AI Models</title><meta name="description" content="Remnant Security's local AI model archive: what we keep, what runs on which machine, and how to run it.">
<link rel="stylesheet" href="{pre}style.css"></head><body><header><div class="nav"><a class="brand" href="{pre}index.html">Remnant <span>AI Models</span></a>{nav}</div></header>
<main>{body}</main><footer>Remnant Security · Local model archive notes. Facts come from each model's Hugging Face card; speed and memory figures are estimates and are labelled as such. Nothing here is a benchmark.</footer></body></html>""")

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
m5 = [m for m in MODELS if 'LLM' in m['modality'] and m['kind']!='official']
def m5rows(ids):
    r=""
    for m in sorted(m5, key=lambda x:(x['family'],x['size_gib'])):
        r+=f"<tr><td><a href='models/{m['id']}.html'>{E(m['family'])}</a><div class='small mut'>{E(m['quant_format'])}</div></td><td>{'yes' if m['abliterated'] else 'no'}</td><td>{mem(m)}</td>"+"".join(f"<td>{fitcell(m,i)}</td>" for i in ids)+"</tr>"
    return r
body = f"""<h1>Every model we keep, and where it runs.</h1>
<p class="lead">Remnant Security's local AI archive: {len(MODELS)} model builds across text, vision, speech, music, image, video and embeddings, about {tot_gib/1024:.1f} TiB on disk. For each one: what it is, its license, how much memory it needs, and whether it runs on our machines, including the planned Bosgame M5 boxes, one or two of them.</p>
<div class="cards">
<div class="card"><div class="k">Downloaded</div><div class="v">{cnt['done']}</div></div>
<div class="card"><div class="k">Downloading now</div><div class="v">{cnt['in-progress']}</div></div>
<div class="card"><div class="k">Queued</div><div class="v">{cnt['queued']}</div></div>
<div class="card"><div class="k">Gated, waiting on sign-in</div><div class="v">{cnt['needs-Ian']}</div></div>
<div class="card"><div class="k">Already on the Macs (<a href="catalog.html#on-device">on-device</a>)</div><div class="v">{len(ODI)}</div></div></div>
<h2>Bosgame M5: one box vs two</h2>
<p>One M5 is a Ryzen AI Max+ 395 with 128 GB of unified LPDDR5X at about 210-220 GB/s measured. On Linux about 108-110 GB is usable by the GPU (96 GB cap on Windows). Two boxes linked with llama.cpp RPC give roughly 200-225 GB, which adds <b>capacity, not speed</b>. Mixture-of-experts models are the sweet spot because only the active experts are read per token.</p>
<div class="wrap"><table><tr><th>Ready-to-run build</th><th>Abliterated</th><th>Est. memory</th><th>M5 ×1</th><th>M5 ×2</th><th>MacBook Pro M4 Max</th></tr>{m5rows(['m5x1','m5x2','mbp'])}</table></div>
<p class="small mut">Token/s figures are theoretical ceilings (bandwidth ÷ bytes of active weights per token), not measurements. Real speed is usually well below. See <a href="fleet.html#method">method</a>.</p>
<h2>Headlines</h2><ul>
<li><b>One M5 runs Qwen3.8 Flash-Next</b> (125B MoE, 6B active) at IQ4_XS or alesha's abliterated IQ3_S, and GLM-5.3-Flash (320B, 18B active) at 2-bit with little headroom.</li>
<li><b>Two M5s add</b> the Flash-Next Q4_K_XL abliterated build and DeepSeek V4.1 Flash at IQ1_M (ISTA-DASLab build; the 110 GB Engram table stays memory-mapped on SSD).</li>
<li><b>Not even two M5s</b> hold the huihui DeepSeek IQ1_M build fully resident (~268 GB est.) or any original safetensors weights; those are archive copies to quantize from.</li>
<li><b>The MacBook Pro (36 GB)</b> runs Qwen3.8-27B at Q4 or the 2.4-bit Mirai build, plus all speech and music models.</li>
<li><b>Video</b>: Wan 2.2 A14B needs the card's offload flags even on an M5; HunyuanVideo 1.5 (8.3B) is the lighter video option.</li>
<li><b>Extras</b>: EmbeddingGemma 2 or bge-small for private RAG, Kokoro and NeuTTS for speech, Z-Image Turbo and FLUX.1 schnell for images, SeedVR2 for upscaling, Mellum2.1 for a fast coding sidecar.</li></ul>
<p class="note">Two engines matter: alesha-pro's Mirai and Maya builds need their own forked engines (mainline llama.cpp, LM Studio and Ollama will not load them), and Maya/Strata builds can't be split across two boxes with llama.cpp RPC.</p>"""
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
    return f"""<h2 id="on-device">On-device (Mac) models</h2>
<p class="lead">Models already sitting on the MacBook Pro and the Mac mini, scanned {E(OD['generated'])}. {len(ODI)} unique models, {OD['total_unique_bytes']/1e9:.0f} GB. {copy_sentence} Backup status: {stline}.</p>
<div class="cards">{cards}<div class="card"><div class="k">Unique total</div><div class="v">{OD['total_unique_bytes']/1e9:.0f} GB</div><div class="small mut">duplicates counted once</div></div></div>
<div class="wrap"><table><tr><th>Model</th><th>Use</th><th>Format</th><th>Size</th><th>On</th><th>License</th><th>NAS backup</th></tr>{odrows(ODI)}</table></div>
<p class="small mut">Sizes are measured on the Macs in decimal GB. Licenses come from the Hugging Face card metadata, the GGUF file's own metadata, or the Ollama license layer, as noted under each one; "unknown" means no source states it. Full local and NAS paths are kept in the private catalog, not on this site.</p>
<h3>Not local weights</h3><ul>{remote}</ul>
<h3>Not scanned yet</h3><ul>{nos}</ul>
<h3>Checked, nothing to back up</h3><ul>{nw}</ul>"""

rows=""
for m in MODELS:
    fitattr = " ".join(f"data-{i}='{m['fit'][i]['verdict']}'" for i in IDS)
    rows+=f"""<tr data-mod="{E(m['modality'])}" data-lic="{E(m['license'])}" data-abl="{'yes' if m['abliterated'] else 'no'}" data-status="{m['status']}" {fitattr} data-q="{E((m['repo']+' '+m['family']).lower())}">
<td><a href="models/{m['id']}.html">{E(m['family'])}</a><div class="small mut">{E(m['repo'])}</div></td><td>{E(m['modality'])}</td><td>{E(m['quant_format'])}</td><td>{params(m)}</td><td>{m['size_gib']} GiB</td><td>{mem(m)}</td>
<td>{E(m['license'])}{' <span class="b nc">non-commercial</span>' if m['non_commercial'] else ''}</td><td>{'<span class="b abl">abliterated</span>' if m['abliterated'] else 'no'}</td><td>{badge(m['status'])}</td><td>{badge(m['fit']['m5x1']['verdict'])}</td><td>{badge(m['fit']['m5x2']['verdict'])}</td></tr>"""
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
<div class="filters"><input id="q" placeholder="Search"><select id="mod"><option value="">All modalities</option>{opts(m['modality'] for m in MODELS)}</select>
<select id="lic"><option value="">All licenses</option>{opts(m['license'] for m in MODELS)}<option value="__nc">Non-commercial only</option></select>
<select id="abl"><option value="">Abliterated: any</option><option value="yes">Abliterated only</option><option value="no">Not abliterated</option></select>
<select id="fitm"><option value="">Fits on: any machine</option>{''.join(f'<option value="{f["id"]}">{E(f["name"])}</option>' for f in FLEET)}</select>
<select id="st"><option value="">Any status</option><option>done</option><option>in-progress</option><option>queued</option><option>needs-Ian</option></select></div>
<p class="small mut" id="count"></p>
<div class="wrap"><table id="t"><tr><th>Model</th><th>Modality</th><th>Format</th><th>Params</th><th>Size</th><th>Est. memory</th><th>License</th><th>Abliterated</th><th>Status</th><th>M5 ×1</th><th>M5 ×2</th></tr>{rows}</table></div>
<p class="small mut">"needs-Ian" = gated repo; the owner has to accept the publisher's terms on Hugging Face first. Machine-readable: <a href="data/catalog.json">data/catalog.json</a>.</p>
{{ondevice_html}}
<script>
const NC={json.dumps([m['license'] for m in MODELS if m['non_commercial']])};
const $=id=>document.getElementById(id);
function f(){{let n=0;const q=$('q').value.toLowerCase(),mo=$('mod').value,li=$('lic').value,ab=$('abl').value,fm=$('fitm').value,st=$('st').value;
document.querySelectorAll('#t tr[data-mod]').forEach(r=>{{let ok=(!q||r.dataset.q.includes(q))&&(!mo||r.dataset.mod==mo)&&(!ab||r.dataset.abl==ab)&&(!st||r.dataset.status==st);
if(li==='__nc')ok=ok&&NC.includes(r.dataset.lic);else if(li)ok=ok&&r.dataset.lic==li;
if(fm){{const v=r.getAttribute('data-'+fm);ok=ok&&(v==='fits'||v==='offload');}}
r.style.display=ok?'':'none';if(ok)n++;}});$('count').textContent=n+' shown (fits filter includes tight/offload)';}}
['q','mod','lic','abl','fitm','st'].forEach(i=>$(i).addEventListener('input',f));f();
</script>"""
page("catalog.html","Catalog",body.replace("{ondevice_html}", ondevice_section()))

# ---------- model detail pages
RECIPE_HINT = {
 "llama.cpp": "recipes.html#llamacpp", "Strata":"recipes.html#forks", "ONLY":"recipes.html#forks", "Transformers":"recipes.html#convert",
 "vLLM":"recipes.html#convert", "Diffusers":"recipes.html#image", "ComfyUI":"recipes.html#comfyui","Wan2.2":"recipes.html#video",
 "HunyuanVideo":"recipes.html#video","qwen-tts":"recipes.html#voice","fish-speech":"recipes.html#voice","whisper":"recipes.html#voice","ACE-Step":"recipes.html#music"}
for m in MODELS:
    hint = next((v for k,v in RECIPE_HINT.items() if k.lower() in m['engine'].lower()), "recipes.html")
    fr = "".join(f"<tr><td>{E(f['name'])}</td><td>{fitcell(m,f['id'])}</td><td class='small mut'>{E(f['budget_note'])}</td></tr>" for f in FLEET)
    body=f"""<p class="small"><a href="../catalog.html">← Catalog</a></p><h1>{E(m['family'])}</h1><p class="lead">{E(m['quant_format'])} · <a href="{m['hf_url']}">{E(m['repo'])}</a></p>
<p>{badge(m['status'])} {'<span class="b abl">abliterated</span>' if m['abliterated'] else ''} {'<span class="b nc">non-commercial</span>' if m['non_commercial'] else ''}</p>
<div class="wrap"><table>
<tr><th style="width:220px">Publisher</th><td>{E(m['publisher'])}</td></tr><tr><th>Modality</th><td>{E(m['modality'])}</td></tr>
<tr><th>Parameters</th><td>{params(m)}<div class="small mut">{E(m['params_note'])} Source: <a href="{m['params_source']}">model card</a>.</div></td></tr>
<tr><th>Format</th><td>{E(m['quant_format'])}</td></tr><tr><th>Size on disk</th><td>{m['size_gib']} GiB ({m['size_bytes']:,} bytes)</td></tr>
<tr><th>Estimated memory to run</th><td>{mem(m)} <span class="small mut">(estimate; see method)</span>{'<div class="small mut">'+E(m['fit_note'])+'</div>' if m.get('fit_note') else ''}</td></tr>
<tr><th>Native context</th><td>{f"{m['context_native']:,} tokens (config/card)" if m['context_native'] else 'n/a'}</td></tr>
<tr><th>Engine</th><td>{E(m['engine'])} · <a href="../{hint}">recipe</a></td></tr>
<tr><th>License</th><td>{E(m['license'])}<div class="small mut">{E(m['license_note'])}</div></td></tr>
<tr><th>Archive folder</th><td><code>{E(m['public_folder'])}</code></td></tr>
<tr><th>Notes</th><td>{E(m['notes'])}</td></tr></table></div>
{'<p class="note danger">Abliterated model: refusal behaviour was removed or suppressed by a third party. Use it only for lawful research on systems you own or are authorised to test, keep it off public endpoints, and you own whatever it produces. See <a href="../licenses.html#abliterated">responsibility note</a>.</p>' if m['abliterated'] else ''}
<h2>Where it runs</h2><div class="wrap"><table><tr><th>Machine</th><th>Verdict</th><th>Budget used</th></tr>{fr}</table></div>
<p class="small mut">Token/s = theoretical ceiling from memory bandwidth and active weight bytes; not a benchmark. Nothing on this page is a benchmark score.</p>"""
    page(f"models/{m['id']}.html", m['family'], body, depth=1)

# ---------- fleet
fl="".join(f"<tr><td><b>{E(f['name'])}</b><div class='small mut'>{E(f['status'])}</div></td><td>{E(f['cpu'])}</td><td>{E(f['gpu'])}</td><td>{E(f['ram'])}</td><td>{E(f['bw_note'])}</td><td class='small'>{E(f['budget_note'])}</td></tr>" for f in FLEET)
mx="".join(f"<tr><td><a href='models/{m['id']}.html'>{E(m['family'])}</a><div class='small mut'>{E(m['quant_format'][:48])}</div></td><td>{mem(m)}</td>"+"".join(f"<td>{fitcell(m,i)}</td>" for i in IDS)+"</tr>" for m in MODELS)
body=f"""<h1>Fleet and fit matrix</h1><p class="lead">Which model runs on which machine. The Bosgame M5 columns come first because that is the box being planned around.</p>
<div class="wrap"><table><tr><th>Machine</th><th>CPU</th><th>GPU</th><th>Memory</th><th>Bandwidth</th><th>Fit budget used</th></tr>{fl}</table></div>
<p class="note">Unknown specs stay unknown: the MacBook Neo was unreachable, and omarchy's current RAM isn't recorded (a 4×32 GB upgrade is planned). Those columns will change once the specs are read.</p>
<h2 id="holds">What each machine already holds</h2>{{holds_html}}
<h2>Matrix</h2><div class="wrap"><table><tr><th>Model</th><th>Est. memory</th>{''.join(f'<th>{E(f["name"])}</th>' for f in FLEET)}</tr>{mx}</table></div>
<h2 id="method">Method</h2><ul>{''.join(f'<li><b>{E(k)}</b>: {E(v)}</li>' for k,v in C['method'].items())}</ul>
<p class="small mut">Diffusion and speech models don't split across two boxes, so the M5 ×2 column for them means "on either box". Maya, Mirai and Strata builds use forked engines without llama.cpp RPC, so they get "No" on M5 ×2 unless they already fit one box.</p>"""
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
    rows+="<tr><td><b>Bosgame M5 (x1 / x2)</b></td><td>not bought yet</td><td class='small mut'>Would load from the NAS archive.</td></tr>"
    return f"<div class='wrap'><table><tr><th>Machine</th><th>Holds</th><th>What</th></tr>{rows}</table></div>"
page("fleet.html","Fleet & fit",body.replace("{holds_html}", holds()))

# ---------- recipes
body = """<h1>Recipes</h1><p class="lead">Copy-paste starting points. Paths are placeholders (<code>/models/...</code>); swap in your own. Check each tool's <code>--help</code> on your build, because flags change between releases.</p>
<h2 id="m5setup">Bosgame M5: Linux memory setup</h2>
<p>On Linux, keep the BIOS dedicated VRAM small (for example 512 MB) and let the GPU borrow system memory through GTT. A commonly used kernel setting for Strix Halo raises the TTM page limit (4 KiB pages; 27,648,000 pages ≈ 105 GiB):</p>
<pre><code># /etc/default/grub  (then: sudo update-grub && reboot)
GRUB_CMDLINE_LINUX_DEFAULT="quiet ttm.pages_limit=27648000 ttm.page_pool_size=27648000"

# confirm after reboot
cat /sys/module/ttm/parameters/pages_limit</code></pre>
<p class="note">Reported practical ceiling is about 108 GB; going to ~110 GB caused errors for at least one reviewer. On Windows the GPU share is capped at 96 GB (AMD Variable Graphics Memory).</p>
<h2 id="llamacpp">llama.cpp on the M5 (Vulkan or ROCm)</h2>
<pre><code>git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp
# Vulkan (simplest on Strix Halo)
cmake -B build -DGGML_VULKAN=ON -DGGML_RPC=ON -DCMAKE_BUILD_TYPE=Release
# or ROCm/HIP (Radeon 8060S is gfx1151)
# cmake -B build -DGGML_HIP=ON -DAMDGPU_TARGETS=gfx1151 -DGGML_RPC=ON -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j</code></pre>
<h3>One box: Qwen3.8 Flash-Next IQ4_XS as an OpenAI-compatible server</h3>
<pre><code>./build/bin/llama-server \\
  -m /models/unsloth-Qwen3.8-Flash-Next-UD-IQ4_XS/UD-IQ4_XS/Qwen3.8-Flash-Next-UD-IQ4_XS-00001-of-00004.gguf \\
  --mmproj /models/unsloth-Qwen3.8-Flash-Next-UD-IQ4_XS/mmproj-BF16.gguf \\
  -ngl 99 -c 32768 --jinja \\
  --host 127.0.0.1 --port 8080
# point any OpenAI client at http://127.0.0.1:8080/v1</code></pre>
<p>Split GGUFs load from the first shard; llama.cpp finds the rest. Same pattern for GLM-5.3-Flash UD-IQ2_XXS (leave context modest: it is the tightest one-box fit).</p>
<h3 id="rpc">Two boxes: llama.cpp RPC</h3>
<pre><code># on box B (worker): expose its GPU over the link (USB4 or 10GbE)
./build/bin/rpc-server -H 0.0.0.0 -p 50052

# on box A (main): load the model across both
./build/bin/llama-server \\
  -m /models/ISTA-DASLab-DeepSeek-V4.1-Flash-1017-GSQ-RCO-IQ1_M/DeepSeek-V4.1-Flash-1017-GSQ-RCO-IQ1_M-00001-of-00006.gguf \\
  --mmproj /models/ISTA-DASLab-DeepSeek-V4.1-Flash-1017-GSQ-RCO-IQ1_M/mmproj-DeepSeek-V4.1-Flash-1017-BF16.gguf \\
  --rpc 10.10.10.2:50052 -ngl 99 -c 16384 --jinja --host 127.0.0.1 --port 8080</code></pre>
<p class="note danger">rpc-server has no authentication. Only run it on a direct cable or an isolated network segment, never on a LAN you share or the internet.</p>
<p>For the ISTA DeepSeek build, the shared Engram file must be linked as shard 6 before loading (from the ISTA card): <code>ln -s DeepSeek-V4.1-Flash-Engram-IQ4_NL.gguf DeepSeek-V4.1-Flash-1017-GSQ-RCO-IQ1_M-00006-of-00006.gguf</code>. Files fetched before Oct 27 2026 need the card's <code>convert_ds41_upstream.py</code>. Keep the Engram file on fast NVMe; it is paged, not held in memory.</p>
<h3>Smaller machines: MoE expert offload</h3>
<pre><code># keep attention on the GPU, push MoE expert tensors to system RAM
./build/bin/llama-server -m model-00001-of-0000N.gguf -ngl 99 \\
  -ot ".ffn_.*_exps.=CPU" -c 16384 --host 127.0.0.1 --port 8080</code></pre>
<p>This is what makes Flash-Next or GLM usable on omarchy after its 128 GB RAM upgrade (8 GB RX 6600 XT + system RAM). Expect it to be slow: expert reads come over DDR4.</p>
<h2 id="mac">MacBook Pro / Mac mini</h2>
<pre><code>brew install llama.cpp
# optional: let the GPU wire more unified memory (resets on reboot; leave headroom for macOS)
sudo sysctl iogpu.wired_limit_mb=30720
llama-server -m /models/huihui-ai-Qwen3.8-27B-Q4_K/Huihui-Qwen3.8-27B-abliterated-Q4_K.gguf \\
  --mmproj /models/huihui-ai-Qwen3.8-27B-Q4_K/mmproj-model-bf16.gguf -ngl 99 -c 32768 --jinja --port 8080</code></pre>
<h2 id="ollama">Ollama and LM Studio</h2>
<pre><code># Ollama: wrap a single-file GGUF
cat > Modelfile &lt;&lt;'EOF'
FROM /models/unsloth-Qwen3.8-27B-UD-Q8_K_XL/Qwen3.8-27B-UD-Q8_K_XL.gguf
PARAMETER num_ctx 32768
EOF
ollama create qwen38-27b-q8 -f Modelfile
ollama run qwen38-27b-q8

# split GGUFs: merge first if your Ollama version won't import shards
llama-gguf-split --merge first-00001-of-00004.gguf merged.gguf

# LM Studio CLI
lms import /models/unsloth-Qwen3.8-27B-UD-Q8_K_XL/Qwen3.8-27B-UD-Q8_K_XL.gguf
lms server start</code></pre>
<p class="small mut">New architectures (Qwen3.8 Flash-Next, GLM-5.3, DeepSeek V4.1) need a recent llama.cpp; Ollama and LM Studio pick up support later. Mirai, Maya and Strata builds won't load in either.</p>
<h2 id="forks">Builds that need their own engine</h2><ul>
<li><b>Qwen3.8-27B Mirai S</b> (alesha-pro): use <a href="https://github.com/professorpalmer/mirai-s-ada">mirai-s-ada</a> (recommended on the card) or the <a href="https://github.com/alesha-pro/llama.cpp-mirai-s">llama.cpp-mirai-s</a> fork.</li>
<li><b>GLM-5.3-Flash Maya-M</b> (alesha-pro): Project Maya engine plus alesha-pro's <a href="https://github.com/alesha-pro/project-maya/blob/glm-ablate/docs/GLM-ABLATE.md">GLM ablate patch</a>.</li>
<li><b>Flash-Next GSQ-RCO Strata</b> (alesha-pro): Strata engine; the card's setup script writes the engine flags.</li></ul>
<h2 id="convert">Original safetensors: serve or quantize</h2>
<pre><code># quantize your own GGUF from the BF16 archive copy (example: Qwen3.8-27B)
python llama.cpp/convert_hf_to_gguf.py /models/Qwen-Qwen3.8-27B --outtype bf16 --outfile qwen38-27b-bf16.gguf
./build/bin/llama-quantize qwen38-27b-bf16.gguf qwen38-27b-Q5_K_M.gguf Q5_K_M</code></pre>
<p>The Flash-Next, GLM and DeepSeek originals are 300-500 GB; they're kept as the source of truth, not for running on this fleet.</p>
<h2 id="comfyui">ComfyUI (image, video, YuE2)</h2>
<pre><code>git clone https://github.com/comfyanonymous/ComfyUI && cd ComfyUI
python -m venv .venv && . .venv/bin/activate
# AMD on Linux: install the ROCm build of PyTorch first (see pytorch.org), then:
pip install -r requirements.txt
python main.py --listen 127.0.0.1 --port 8188</code></pre>
<p>YuE2 (ComfyUI repack): put <code>sheetsage2_bf16.safetensors</code> in <code>models/audio_encoders/</code> and <code>yue2_3b_bf16.safetensors</code> in <code>models/checkpoints/</code>, then load the official "YuE2: Text to Music" workflow template. MOSS-Image: install the MOSS-Image node from ComfyUI Manager. Wan 2.2 and HunyuanVideo 1.5 have ComfyUI integrations listed on their cards.</p>
<h2 id="image">Image with Diffusers</h2>
<pre><code>pip install "torch>=2.4.0" "transformers>=5.17" git+https://github.com/huggingface/diffusers accelerate pillow</code></pre>
<pre><code>import torch
from diffusers import QwenImage21Pipeline
pipe = QwenImage21Pipeline.from_pretrained("/models/Qwen-Qwen-Image-2.1", torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()   # memory optimisation from the model card
img = pipe(prompt="isometric illustration of a home lab rack, clean flat style").images[0]
img.save("out.png")</code></pre>
<p class="note danger">Qwen-Image 2.1 is under the Qwen Research License: non-commercial use only.</p>
<h2 id="video">Video: Wan 2.2 A14B and HunyuanVideo 1.5</h2>
<pre><code>git clone https://github.com/Wan-Video/Wan2.2.git && cd Wan2.2
pip install -r requirements.txt
# single-device command from the model card, with offload
python generate.py --task t2v-A14B --size 1280*720 --ckpt_dir /models/Wan-AI-Wan2.2-T2V-A14B \\
  --offload_model True --convert_model_dtype --prompt "slow dolly shot across a dark server room, red status LEDs"</code></pre>
<p>Image-to-video uses <code>--task i2v-A14B</code> with the I2V checkpoint and an input image (see the card). HunyuanVideo 1.5: clone <a href="https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5">Tencent-Hunyuan/HunyuanVideo-1.5</a>, <code>pip install -r requirements.txt</code>, and follow its README or ComfyUI guide. Its license excludes the EU, UK and South Korea.</p>
<h2 id="voice">Speech: Whisper, Qwen3-TTS, Fish S2 Pro</h2>
<pre><code># Whisper large-v3-turbo via Transformers (card's route)
pip install --upgrade transformers "datasets[audio]" accelerate
python - &lt;&lt;'EOF'
import torch
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", model="/models/openai-whisper-large-v3-turbo",
               torch_dtype=torch.float16, device_map="auto")
print(asr("meeting.wav", return_timestamps=True)["text"])
EOF

# or whisper.cpp (Metal on Mac, Vulkan on the M5), using its own ggml file
git clone https://github.com/ggml-org/whisper.cpp && cd whisper.cpp
sh ./models/download-ggml-model.sh large-v3-turbo
cmake -B build && cmake --build build -j --config Release
./build/bin/whisper-cli -m models/ggml-large-v3-turbo.bin -f meeting.wav</code></pre>
<pre><code># Qwen3-TTS voice clone (Base model needs a short reference clip + its transcript)
pip install -U qwen-tts
python - &lt;&lt;'EOF'
import torch, soundfile as sf
from qwen_tts import Qwen3TTSModel
model = Qwen3TTSModel.from_pretrained("/models/Qwen-Qwen3-TTS-12Hz-1.7B-Base",
                                      device_map="cuda:0", dtype=torch.bfloat16)
wavs, sr = model.generate_voice_clone(text="Your weekly security digest is ready.",
    language="English", ref_audio="my_voice.wav", ref_text="Transcript of my_voice.wav")
sf.write("out.wav", wavs[0], sr)
EOF</code></pre>
<p class="small mut">On Apple silicon use <code>device_map="mps"</code>; on the M5 with ROCm PyTorch, AMD GPUs still appear as <code>cuda</code>. Only clone voices you have permission to use. Fish Audio S2 Pro runs with <a href="https://github.com/fishaudio/fish-speech">fish-speech</a>; it is research/non-commercial unless you buy a license.</p>
<h2 id="music">Music: ACE-Step 1.5 and YuE2</h2>
<p>ACE-Step 1.5 runs from <a href="https://github.com/ace-step/ACE-Step-1.5">ace-step/ACE-Step-1.5</a>; its card says it runs locally in under 4 GB of VRAM, so even the Mac mini can host it. YuE2 runs inside ComfyUI (above) and is CC BY-NC 4.0, so no commercial use.</p>
<h2 id="openwebui">Front end: Open WebUI on any llama-server</h2>
<pre><code>docker run -d --name open-webui -p 127.0.0.1:3000:8080 \\
  -e OPENAI_API_BASE_URL=http://host.docker.internal:8080/v1 -e OPENAI_API_KEY=none \\
  --add-host=host.docker.internal:host-gateway \\
  -v open-webui:/app/backend/data ghcr.io/open-webui/open-webui:main</code></pre>"""
extras_recipe = """<h2 id="extras">Extras: embeddings, TTS, image and a coding sidecar</h2>
<p>The nine extras live under <code>/models/extras/</code> on the M5. They are small sidecars, not replacements for the main LLMs.</p>
<h3 id="embeddings">EmbeddingGemma 2 / bge-small</h3>
<pre><code>pip install -U sentence-transformers
python - &lt;&lt;'EOF'
from sentence_transformers import SentenceTransformer
m = SentenceTransformer("/models/extras/embeddinggemma-2")
print(m.encode(["local models stay local"]).shape)
EOF</code></pre>
<p><code>bge-small-en-v1.5-f16.gguf</code> is the tiny llama.cpp embedding alternative: <code>llama-server -m /models/extras/bge-small-en-v1.5-gguf/bge-small-en-v1.5-f16.gguf --embedding --port 8082</code>.</p>
<h3 id="extras-tts">Kokoro 82M / NeuTTS Air</h3>
<p>Kokoro is the fast TTS model; use the <code>Kokoro-TTS-Local</code> project against <code>/models/extras/kokoro-82m</code>. NeuTTS Air is a single 0.5 GB GGUF fallback.</p>
<h3 id="extras-image">Z-Image Turbo / FLUX.1 schnell</h3>
<pre><code>import torch
from diffusers import AutoPipelineForText2Image
pipe = AutoPipelineForText2Image.from_pretrained("/models/extras/z-image-turbo", torch_dtype=torch.bfloat16)
pipe.enable_model_cpu_offload()
img = pipe("isometric illustration of a home lab rack").images[0]</code></pre>
<p>FLUX.1 schnell uses <code>FluxPipeline.from_pretrained("/models/extras/flux1-schnell")</code> and four steps. SeedVR2 is a ComfyUI upscaler; the Qwen-Image Q4_K_M GGUF is a ComfyUI-GGUF asset.</p>
<h3 id="extras-code">Mellum2.1 12B-A2.5B</h3>
<pre><code>llama-server -m /models/extras/mellum21-12b-a2.5b-thinking-q4km/Mellum2.1-12B-A2.5B-Thinking-Q4_K_M.gguf \
  -ngl 99 -c 32768 --jinja --port 8081</code></pre>
<p class="small mut">The extras are staged files, not benchmarks. Check each tool's <code>--help</code>; Z-Image and FLUX need a recent Diffusers or ComfyUI, SeedVR2 needs its ComfyUI node, and the GGUF extras use the same llama.cpp build as the main models.</p>"""
body += extras_recipe
page("recipes.html","Recipes",body)

# ---------- use cases
UC = [
 ("Security research and red-team prep","GLM-5.3-Flash or Flash-Next on one M5; abliterated builds when a stock model refuses legitimate defensive questions (malware triage, exploit write-ups for patched CVEs, phishing-awareness samples).","M5 ×1 (Flash-Next IQ4_XS / alesha IQ3_S), M5 ×2 for DeepSeek V4.1 IQ1_M","Keep abliterated models offline and off public endpoints. Authorised targets only."),
 ("Local coding agent","Serve Flash-Next IQ4_XS with llama-server and point an OpenAI-compatible coding agent at it. Only 6B params are active per token, so it is the fastest large model here (theoretical ceiling ≈67 tok/s on one M5). Mellum2.1 12B-A2.5B is the small, fast sidecar; Qwen3.8-27B Q4 is the MacBook Pro travel model.","M5 ×1, MacBook Pro","Code never leaves the LAN. Qwen Community License allows internal commercial use."),
 ("Private document Q&A","Open WebUI + llama-server + your own documents, with EmbeddingGemma 2 or bge-small building the local index. Long native context (262K on Qwen3.8, 1M advertised on GLM-5.3/DeepSeek V4.1) helps, but KV cache grows with context; start at 32K.","M5 ×1, MacBook Pro","Client documents and embeddings stay on hardware you own."),
 ("Local RAG and search","EmbeddingGemma 2 (1.5 GB) or bge-small (0.07 GB) builds a private index; pair it with Flash-Next or Qwen3.8-27B for answers. No text leaves the LAN.","M5 ×1, MacBook Pro","Embeddings and prompts stay local. No third-party embedding API."),
 ("Content for Remnant apps","Z-Image Turbo or FLUX.1 schnell for fast concept art, Qwen-Image 2.1 / MOSS-Image for heavier work, SeedVR2 for upscaling, Wan 2.2 or HunyuanVideo for clips, ACE-Step for background music.","M5 ×1 (image/music), M5 with offload (Wan)","Check licenses: Qwen-Image 2.1, the Qwen-Image Q4_K_M GGUF and YuE2 are non-commercial; Z-Image, FLUX.1 schnell, MOSS-Image, Wan 2.2 and ACE-Step are commercial-OK."),
 ("Voice: transcripts, narration, voice notes","Whisper turbo for meeting/podcast transcripts; Kokoro 82M or NeuTTS Air for fast lightweight speech; Qwen3-TTS (Apache 2.0) for narration with your own cloned voice; Fish S2 Pro for research comparisons only.","Every machine except the NAS for TTS; Whisper even runs on the Mac mini","Only clone voices with consent."),
 ("Vision: screenshot and UI review","All four LLM families are image-text-to-text; load the mmproj file with llama-server to ask about App Store screenshots, error dialogs or diagrams.","M5 ×1, MacBook Pro (27B)","Use the mmproj that ships beside each GGUF."),
 ("Quantization lab","Original safetensors are archived so you can make your own GGUFs or try new quant methods (GSQ-RCO, Mirai) without re-downloading 1.2 TB.","Any box with disk; M5 to test results","Originals are the source of truth; keep the archive offline-safe."),
]
body="<h1>Use cases</h1><p class='lead'>What this archive is for, and which machine to use.</p>"+"".join(f"<div class='card' style='margin:14px 0'><h3 style='margin-top:0'>{E(a)}</h3><p>{E(b)}</p><p><b>Where:</b> {E(c)}</p><p class='small mut'>{E(d)}</p></div>" for a,b,c,d in UC)
page("use-cases.html","Use cases",body)

# ---------- licenses
lr="".join(f"<tr><td><a href='models/{m['id']}.html'>{E(m['family'])}</a><div class='small mut'>{E(m['repo'])}</div></td><td>{E(m['license'])}</td><td>{'<span class=\"b nc\">non-commercial</span> ' if m['non_commercial'] else ''}{E(m['license_note'])}</td></tr>" for m in MODELS)
body=f"""<h1>Licenses and responsibility</h1><p class="lead">License names come from each repo's Hugging Face card metadata. This is a summary, not legal advice: read the actual license before shipping anything.</p>
<p class="note danger"><b>Non-commercial:</b> Qwen-Image 2.1 (Qwen Research License), YuE2 (CC BY-NC 4.0) and Fish Audio S2 Pro (Fish Audio Research License) can't be used in anything sold without a separate license. HunyuanVideo 1.5's license doesn't apply in the EU, UK or South Korea.</p>
<h2 id="abliterated">Abliterated models</h2><p>Abliterated builds (huihui-ai, alesha-pro) have had refusal behaviour removed or suppressed by third parties, either baked into the weights or applied with a control vector at run time. They inherit the base model's license. They will answer requests that the original would refuse, so:</p>
<ul><li>Use them for lawful, authorised work only: defensive research, testing your own systems, red-team prep with written scope.</li><li>Don't expose them on a public endpoint or share access.</li><li>Review outputs before acting on them; you are responsible for what you do with them.</li><li>They are community conversions, not official releases, and their quality can differ from the original.</li></ul>
<h2>Every model</h2><div class="wrap"><table><tr><th>Model</th><th>License</th><th>Summary</th></tr>{lr}</table></div>"""
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
