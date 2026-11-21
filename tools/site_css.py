CSS = r"""
:root{--bg:#0b0d10;--panel:#12161b;--panel2:#0f1318;--line:#222a33;--line2:#56616f;--txt:#e6e9ee;--mut:#9aa4b1;--acc:#e5484d;--ok:#30a46c;--warn:#f5a524;--no:#a7b0bd;--blue:#79b8ff;--focus:#8ec5ff;--nav-h:56px}
*{box-sizing:border-box}html{scroll-padding-top:76px}
body{margin:0;background:var(--bg);color:var(--txt);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,sans-serif}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:2px solid var(--focus);outline-offset:2px}
.skip{position:absolute;left:-9999px;top:0;padding:10px 14px;background:var(--panel);border:1px solid var(--line2);border-radius:8px;z-index:30}.skip:focus{left:16px;top:10px}
header{border-bottom:1px solid var(--line);background:#0e1115;position:sticky;top:0;z-index:5}
.nav{max-width:1200px;margin:auto;display:flex;gap:18px;align-items:center;padding:12px 20px;flex-wrap:wrap}
.brand{font-weight:700;color:var(--txt);letter-spacing:.2px}.brand span{color:var(--acc)}
.nav a.l{color:var(--mut);font-size:14px}.nav a.l.on,.nav a.l:hover,.nav a.l[aria-current="page"]{color:var(--txt);text-decoration:none}
main{max-width:1200px;margin:auto;padding:28px 20px 60px}
h1{font-size:clamp(30px,4vw,40px);line-height:1.15;margin:8px 0 10px;letter-spacing:-.02em}
h2{margin-top:38px;font-size:clamp(20px,2.5vw,24px);line-height:1.25;letter-spacing:-.01em}
h3{margin-top:26px;font-size:18px;line-height:1.3}
.lead{color:var(--mut);font-size:17px;max-width:820px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;margin:18px 0}
.stats{grid-template-columns:repeat(3,minmax(0,1fr))}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px}
.card .k{color:var(--mut);font-size:13px}.card .v{font-size:26px;font-weight:700;line-height:1.2}
.card a{color:inherit}
.pipeline{color:var(--mut);font-size:13px;margin:6px 0 0}
.start{background:linear-gradient(120deg,#151014,#12161b 60%);border:1px solid #3a2a2c;background-color:#151014;border-radius:12px;padding:18px 20px;margin:22px 0}
.start h2{margin:0 0 4px;font-size:20px;color:#ffb3b6}.start p{margin:0 0 12px;color:var(--mut)}
.picks{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.pick{background:rgba(255,255,255,.02);border:1px solid var(--line);border-radius:10px;padding:12px 14px}
.pick .k{display:block;color:var(--mut);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;margin-bottom:3px}
.pick a{font-weight:600}
.tag{display:inline-block;margin-left:6px;padding:1px 7px;border-radius:999px;background:#1b2230;color:#9cc4ff;font-size:11px;font-weight:600;vertical-align:1px;white-space:nowrap}
table{width:100%;border-collapse:collapse;font-size:14px;background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow:hidden}
caption{text-align:left}
th,td{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;vertical-align:top}
th{color:var(--mut);font-weight:600;background:var(--panel2);font-size:13px;white-space:nowrap}
td.num{font-variant-numeric:tabular-nums;white-space:nowrap}
.wrap{overflow-x:auto;border-radius:10px}
.table-scroll{max-height:72vh;overflow:auto;border:0;border-radius:10px;background:transparent;padding:0}
.table-scroll table{border:1px solid var(--line);border-radius:10px}
.table-scroll thead th{position:sticky;top:0;z-index:2}
.fleet-table th:first-child,.fleet-table td:first-child{position:sticky;left:0;background:var(--panel);z-index:1}
.fleet-table thead th:first-child{z-index:3}
.fit-table td:first-child{min-width:250px}.catalog-table td:first-child{min-width:220px}.od-table td:first-child{min-width:230px}
h2[id],h3[id],details[id]{scroll-margin-top:76px}
.scroll-hint{color:var(--mut);font-size:12px;margin:6px 2px 0}
.b{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.fits{background:#12301f;color:#6ff0aa}.offload{background:#33280f;color:var(--warn)}.no{background:#1c1f24;color:var(--no)}
.unknown{background:#1c1f24;color:#c7cdd4;border:1px dashed #4a5563}
.convert{background:#122335;color:#8ec5ff}.after-RAM-upgrade{background:#2a1f35;color:#d2aaff}
.done{background:#12301f;color:#6ff0aa}.in-progress{background:#122335;color:#8ec5ff}.queued{background:#1c1f24;color:#c7cdd4}.needs-Ian{background:#3a1416;color:#ff8b8f}
.nc{background:#3a1416;color:#ffb3b6}.abl{background:#2a1f35;color:#d2aaff}
pre{background:#07090b;border:1px solid var(--line);border-radius:10px;padding:14px;overflow-x:auto;font-size:13px;line-height:1.5}
code{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px}
.filters{display:grid;grid-template-columns:minmax(200px,1.4fr) repeat(4,minmax(150px,1fr)) auto;gap:10px;align-items:end;margin:14px 0}
.filter{display:flex;flex-direction:column;gap:4px;color:var(--mut);font-size:12px;font-weight:600}
.filter input,.filter select{width:100%;background:var(--panel);color:var(--txt);border:1px solid var(--line2);border-radius:8px;padding:7px 10px;font:inherit;font-size:14px;font-weight:400}
.filter input::placeholder{color:#8d97a5}
.filter-actions{display:flex;gap:8px;flex-wrap:wrap;grid-column:1/-1}
.btn{background:var(--panel);color:var(--txt);border:1px solid var(--line2);border-radius:8px;padding:8px 12px;font:inherit;font-size:13px;cursor:pointer}
.btn:hover{background:#1a2028}
.btn[aria-pressed="true"]{border-color:var(--blue);color:var(--blue)}
.note{border:1px solid #4a3d1c;background:#16130b;padding:10px 14px;border-radius:8px;color:#f0e2c4}
.danger{border-color:#4a2024;background:#170c0d;color:#f2d0d1}
details.ondevice{margin:28px 0;border:1px solid var(--line);border-radius:12px;background:rgba(255,255,255,.01)}
details.ondevice summary{cursor:pointer;list-style:none;padding:16px 18px;font-size:18px;font-weight:650;display:flex;justify-content:space-between;gap:12px;align-items:baseline;flex-wrap:wrap}
details.ondevice summary::-webkit-details-marker{display:none}
details.ondevice summary::before{content:"▸";color:var(--acc);font-size:14px;margin-right:2px}
details.ondevice[open] summary::before{content:"▾"}
details.ondevice summary span:first-of-type{flex:1;text-align:left}
details.ondevice summary span:last-child{font-size:13px;color:var(--mut);font-weight:400}
details.ondevice > div,details.ondevice > p,details.ondevice > h2,details.ondevice > h3,details.ondevice > .cards,details.ondevice > .wrap{padding-left:18px;padding-right:18px}
details.ondevice > .cards{padding-top:0}details.ondevice > .wrap{margin-bottom:18px}
.fit-line{display:none;color:var(--mut);font-size:12px;margin-top:2px}
.filter-machine .fit-line{display:block}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
footer{border-top:1px solid var(--line);color:var(--mut);font-size:13px;padding:20px;text-align:center}
.mut{color:var(--mut)}.small{font-size:13px}
[hidden]{display:none !important}
body:not(.show-all) .col-opt{display:none}
body.show-all .col-opt{display:table-cell}
@media(max-width:900px){.filters{grid-template-columns:1fr 1fr}.filter-actions{grid-column:1/-1}}
@media(max-width:760px){
 .nav{gap:10px 14px;padding:11px 16px}.nav a.l{font-size:13px}
 main{padding:22px 16px 50px}.lead{font-size:16px}
 .stats{grid-template-columns:1fr}.picks{grid-template-columns:1fr}
 .start{padding:16px}.start h2{font-size:19px}
 .filters{grid-template-columns:1fr;gap:9px}.filter input{width:100%}
 .fit-table thead,.catalog-table thead,.machine-table thead{display:none}
 .fit-table,.fit-table tbody,.fit-table tr,.fit-table td,
 .catalog-table,.catalog-table tbody,.catalog-table tr,.catalog-table td,
 .machine-table,.machine-table tbody,.machine-table tr,.machine-table td{display:block;width:auto}
 .fit-table tr,.catalog-table tr,.machine-table tr{margin:0 0 10px;padding:12px 14px;background:var(--panel);border:1px solid var(--line);border-radius:10px}
 .fit-table td,.catalog-table td,.machine-table td{border:0;padding:3px 0}
 .fit-table td[data-label]::before,.catalog-table td[data-label]::before,.machine-table td[data-label]::before{content:attr(data-label) ": ";color:var(--mut);font-size:12px;font-weight:600}
 .fit-table td:first-child,.catalog-table td:first-child,.machine-table td:first-child{font-size:16px;margin-bottom:3px}
 #hint{display:none}
 .table-scroll{max-height:none;overflow:auto;border:0;background:transparent;padding:0}
 .table-scroll table{border:0}
 .table-scroll table{border:0}
 body.show-all .catalog-table td.col-opt{display:block}
}
"""
