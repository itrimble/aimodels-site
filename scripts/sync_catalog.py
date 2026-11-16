#!/usr/bin/env python3
"""Regenerate the aimodels catalog from a NAS inventory and emit a site data diff.

This updates a *private* catalog (NAS paths included) from a JSON inventory,
writes a public data/catalog.json (paths stripped), rebuilds the static site,
and prints a human-readable diff. It does not commit, push, merge, or install
a scheduler.

Typical run, from a checkout of itrimble/aimodels-site, on the MacBook Pro
(the machine that can SSH to the NAS):

    scripts/sync-catalog --ssh ian@192.168.12.66 \\
        --private-catalog ~/aimodels-private/catalog.json \\
        --repo .

See scripts/README.md for the recommended schedule and how to push private
catalog copies back to the NAS.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from copy import deepcopy
from pathlib import Path

GiB = 2**30
GB = 1e9

# When a previously gated pack lands on disk, fill in card facts we already
# confirmed from the README sitting next to the weights (not from a token).
ENRICH_ON_DONE = {
    "black-forest-labs/flux-3-image-klein-comfy": {
        "quant_format": "safetensors (ComfyUI pack: BF16, int8, NVFP4)",
        "params_total_b": 5.6,
        "params_note": (
            "Card: 5.6B image transformer; Qwen3-VL-4B text encoder is separate. "
            "Repo ships distilled and base checkpoints in several quants plus a "
            "prompt upsampler. One pipeline is loaded at a time, so peak memory "
            "is well below the pack size."
        ),
        "notes": (
            "On the WD media drive after the gated terms were accepted. "
            "ComfyUI pack of FLUX 3 Image Klein (distilled and base)."
        ),
        "engine": "ComfyUI",
        "fit_note": (
            "Repo ships several quants and components; one pipeline is loaded "
            "at a time. Peak memory is not stated as a single figure on the card."
        ),
        "license_note": (
            "FLUX Kommunity License: non-commercial use, with a commercial-output "
            "exception for Qualifying Users; read LICENSE.md before any commercial use."
        ),
        "public_folder": "usb-media/image",
        "clear_est_memory": True,
    },
    "Lightricks/LTX-2.5": {
        "quant_format": "safetensors (ComfyUI pack: BF16, int8, NVFP4)",
        "params_total_b": 22.0,
        "params_note": (
            "File names identify a 22B transformer plus a Gemma 4 12B text encoder. "
            "Repo ships dev and distilled checkpoints in several quants, VAEs and "
            "upscalers. One pipeline is loaded at a time, so peak memory is well "
            "below the pack size."
        ),
        "notes": (
            "On the WD media drive after the gated terms were accepted. "
            "ComfyUI pack of LTX-2.5."
        ),
        "engine": "ComfyUI",
        "fit_note": (
            "Repo ships several quants and components; one pipeline is loaded "
            "at a time. Peak memory is not stated as a single figure on the card."
        ),
        "license_note": (
            "Custom Lightricks LTX 2.x community license; read before commercial use."
        ),
        "public_folder": "usb-media/video",
        "clear_est_memory": True,
    },
}


def load_json(path: Path):
    return json.loads(path.read_text())


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1) + "\n")


def folder_status(rec: dict) -> str:
    if rec.get("incomplete_files"):
        return "in-progress"
    if rec.get("has_weights") or rec.get("download_complete"):
        return "done"
    if rec.get("exists") and rec.get("files", 0) > 0:
        return "in-progress"
    return "queued"


def index_inventory(inv: dict) -> dict:
    by_path = {}
    by_key = {}
    by_name = {}
    for rec in inv.get("folders") or []:
        by_path[rec["path"].rstrip("/")] = rec
        by_key[rec["key"]] = rec
        by_name.setdefault(rec["name"], []).append(rec)
    return {"by_path": by_path, "by_key": by_key, "by_name": by_name}


def match_folder(model: dict, idx: dict):
    nas = (model.get("nas_path") or "").rstrip("/")
    if nas and nas in idx["by_path"]:
        return idx["by_path"][nas]
    # public_folder + hyphenated repo, then hyphenated repo alone
    repo_name = (model.get("repo") or "").replace("/", "-")
    pub = model.get("public_folder") or ""
    if pub and pub != "not downloaded":
        key = f"{pub}/{repo_name}"
        if key in idx["by_key"]:
            return idx["by_key"][key]
    hits = idx["by_name"].get(repo_name) or []
    if len(hits) == 1:
        return hits[0]
    return None


def public_folder_for(rec: dict) -> str:
    return rec["area"]


def fit_one(e: dict, m: dict):
    need = (e.get("resident_bytes") or 0) / GB
    est = need * 1.05 + 4 if "LLM" in (e.get("modality") or "") else need + 4
    ov = e.get("override") or {}
    if m["id"] in ov:
        return ov[m["id"]], (e.get("est_override") if e.get("est_override") is not None else est)
    if e.get("est_override"):
        est = e["est_override"]
    if e.get("kind") == "media" and m["id"] == "m5x2":
        # media is not split across two boxes
        pass
    if m["id"] == "m5x2" and ("ONLY" in (e.get("engine") or "") or "Strata" in (e.get("engine") or "")):
        # use one-box verdict; caller still asks for m5x2
        pass
    if e.get("clear_est_memory") or e.get("status") == "needs-Ian" or m.get("budget_gb") is None:
        return "unknown", est
    if e.get("kind") == "official" and "LLM" in (e.get("modality") or ""):
        return "convert", est
    if est <= (m["budget_gb"] or 0):
        return "fits", est
    if m.get("offload_gb") and est <= m["offload_gb"]:
        return "offload", est
    if m["id"] == "omarchy" and e.get("kind") == "media":
        return "no", est
    if m["id"] == "omarchy":
        return ("after-RAM-upgrade" if est <= 118 else "no"), est
    return "no", est


def tps(e: dict, m: dict, verdict: str, fit_so_far: dict):
    if verdict not in ("fits", "offload") or not m.get("bw_gbs") or "LLM" not in (e.get("modality") or ""):
        return None
    act = e.get("params_active_b")
    if act is None:
        return None
    tot = e.get("gguf_params_b")
    bpw = e["resident_bytes"] * 8 / (tot * 1e9) if tot else None
    if not bpw:
        return None
    bytes_tok = act * 1e9 * bpw / 8
    v = m["bw_gbs"] * 1e9 / bytes_tok
    if m["id"] == "m5x2" and (fit_so_far.get("m5x1") or {}).get("verdict") != "fits":
        v *= 0.82
    return round(v, 1)


def recompute_fit(e: dict, fleet: list) -> None:
    # special case: Maya/Strata one-box-only already encoded in original fit()
    e.setdefault("fit", {})
    # two-pass so m5x2 RPC penalty can see m5x1
    first = {}
    last_est = None
    for m in fleet:
        # Maya/Strata and media-on-m5x2: reuse one-box machine for the second box
        machine = m
        if m["id"] == "m5x2" and e.get("kind") == "media":
            machine = next(x for x in fleet if x["id"] == "m5x1")
        if m["id"] == "m5x2" and ("ONLY" in (e.get("engine") or "") or "Strata" in (e.get("engine") or "")):
            machine = next(x for x in fleet if x["id"] == "m5x1")
        v, est = fit_one(e, machine)
        first[m["id"]] = (v, est)
        last_est = est
    e["fit"] = {}
    for m in fleet:
        v, est = first[m["id"]]
        e["fit"][m["id"]] = dict(verdict=v, est_tok_s=tps(e, m, v, {k: {"verdict": val[0]} for k, val in first.items()}))
    if e.get("clear_est_memory") or e.get("status") == "needs-Ian" or e.get("repo") == "tencent/HunyuanVideo-1.5":
        e["est_memory_gb"] = None
    elif last_est is not None:
        e["est_memory_gb"] = round(last_est, 1)


def apply_enrichment(model: dict, enrichment: dict) -> list:
    changes = []
    for k, v in enrichment.items():
        if k == "clear_est_memory":
            if v and model.get("est_memory_gb") is not None:
                changes.append(("est_memory_gb", model.get("est_memory_gb"), None))
            model["clear_est_memory"] = v
            continue
        if model.get(k) != v:
            changes.append((k, model.get(k), v))
            model[k] = v
    return changes


def sync(catalog: dict, inv: dict) -> dict:
    """Return {catalog, report} after applying inventory."""
    report = {
        "status_changes": [],
        "size_changes": [],
        "path_changes": [],
        "field_changes": [],
        "backup_changes": [],
        "missing_on_disk": [],
        "untracked": [],
        "pending": [],
        "removed_candidates": [],
    }
    idx = index_inventory(inv)
    matched_keys = set()
    fleet = catalog["fleet"]

    for model in catalog["models"]:
        rec = match_folder(model, idx)
        old_status = model.get("status")
        old_size = model.get("size_bytes")
        old_path = model.get("nas_path")
        old_folder = model.get("public_folder")

        if rec is None:
            if old_status in ("done", "in-progress", "queued") and old_path:
                report["missing_on_disk"].append({
                    "repo": model["repo"],
                    "id": model.get("id"),
                    "status": old_status,
                    "nas_path": old_path,
                })
                report["removed_candidates"].append(model["repo"] + " (" + str(model.get("quant_format")) + ")")
            elif old_status == "needs-Ian":
                report["pending"].append({
                    "repo": model["repo"],
                    "reason": "still marked needs-Ian and no folder on disk",
                })
            continue

        matched_keys.add(rec["key"])
        new_status = folder_status(rec)
        # Never invent a needs-Ian once the files are here.
        if new_status == "done" and old_status != "done":
            model["status"] = "done"
            report["status_changes"].append((model["repo"], old_status, "done", rec["path"]))
            if model["repo"] in ENRICH_ON_DONE:
                report["field_changes"].extend(
                    (model["repo"], k, a, b) for k, a, b in apply_enrichment(model, ENRICH_ON_DONE[model["repo"]])
                )
        elif new_status == "in-progress" and old_status != "in-progress":
            model["status"] = "in-progress"
            report["status_changes"].append((model["repo"], old_status, "in-progress", rec["path"]))
        elif new_status == "done":
            model["status"] = "done"

        if rec["path"] != old_path:
            model["nas_path"] = rec["path"]
            report["path_changes"].append((model["repo"], old_path, rec["path"]))
        pub = public_folder_for(rec)
        if model.get("public_folder") != pub:
            report["field_changes"].append((model["repo"], "public_folder", old_folder, pub))
            model["public_folder"] = pub

        new_size = rec["size_bytes"]
        # ISTA (and any model with a separate resident set) keeps resident_bytes.
        if new_size != old_size:
            report["size_changes"].append((model["repo"], old_size, new_size, model.get("id")))
            model["size_bytes"] = new_size
            model["size_gib"] = round(new_size / GiB, 2)
            # Only bump resident_bytes when it was tracking the full file set.
            if model.get("resident_bytes") == old_size or model.get("resident_bytes") is None:
                model["resident_bytes"] = new_size

        recompute_fit(model, fleet)
        # clear helper flag so it does not leak into the private catalog as a surprise,
        # but we need it during recompute. Keep it only if enrichment set it; strip later
        # if we want. Leaving clear_est_memory on flux/LTX is useful for the next sync.

    for rec in inv.get("folders") or []:
        if rec["key"] in matched_keys:
            continue
        st = folder_status(rec)
        item = {
            "key": rec["key"],
            "path": rec["path"],
            "status": st,
            "size_bytes": rec["size_bytes"],
            "files": rec["files"],
            "incomplete_files": rec["incomplete_files"],
        }
        if st == "done":
            report["untracked"].append(item)
        else:
            report["pending"].append(item)

    dev = inv.get("device") or {}
    if dev.get("verify_done") and dev.get("verify_mismatches", 0) == 0 and catalog.get("on_device"):
        for item in catalog["on_device"].get("items") or []:
            old = item.get("backup_status")
            if old != "verified":
                item["backup_status"] = "verified"
                report["backup_changes"].append((item.get("name") or item.get("id"), old, "verified"))
    elif catalog.get("on_device"):
        report["backup_changes"].append((
            "(device copy)",
            "unchanged",
            f"verify_done={dev.get('verify_done')} mismatches={dev.get('verify_mismatches')}",
        ))

    catalog["generated"] = inv.get("generated") or catalog.get("generated")
    catalog["inventory_generated"] = inv.get("generated")
    return {"catalog": catalog, "report": report}


def public_copy(catalog: dict) -> dict:
    pub = json.loads(json.dumps(catalog))
    pub.pop("inventory_generated", None)
    for m in pub.get("models") or []:
        m.pop("nas_path", None)
        m.pop("override", None)
        m.pop("est_override", None)
        m.pop("clear_est_memory", None)
    if "on_device" in pub:
        pub["on_device"].pop("nas_root", None)
        for i in pub["on_device"].get("items") or []:
            i.pop("nas_path", None)
            i["locations"] = [{"machine": l["machine"]} for l in i.get("locations") or []]
    return pub


def write_markdown(catalog: dict, dest: Path) -> None:
    c = catalog
    L = [
        "# AI model catalog (private, NAS paths included)",
        "",
        f"Generated {c['generated']}. Machine-readable twin: catalog.json.",
        "",
        "## Method",
        "",
        *[f"- **{k}**: {v}" for k, v in c["method"].items()],
        "",
        "## Counts by status",
        "",
    ]
    for k, v in Counter(m["status"] for m in c["models"]).items():
        L.append(f"- {k}: {v}")
    L += [
        "",
        "## Models",
        "",
        "| Status | Family | Repo | Kind | Quant/format | GiB | Params (total/active B) | License | Abl. | Est. mem GB | NAS path |",
        "|---|---|---|---|---|---:|---|---|---|---:|---|",
    ]
    for m in c["models"]:
        p = f"{m['params_total_b'] or 'unknown'}/{m['params_active_b'] or ('n/a' if not m['moe'] else 'unknown')}"
        L.append(
            f"| {m['status']} | {m['family']} | [{m['repo']}]({m['hf_url']}) | {m['kind']} | {m['quant_format']} | "
            f"{m['size_gib']} | {p} | {m['license']}{' (NC)' if m['non_commercial'] else ''} | "
            f"{'yes' if m['abliterated'] else 'no'} | {m['est_memory_gb'] or 'unknown'} | `{m.get('nas_path') or 'not downloaded'}` |"
        )
    ids = [f["id"] for f in c["fleet"]]
    L += [
        "",
        "## Fleet",
        "",
        "| Machine | Status | CPU | GPU | Memory | Bandwidth | Budget used | Source |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for f in c["fleet"]:
        L.append(
            f"| {f['name']} | {f['status']} | {f['cpu']} | {f['gpu']} | {f['ram']} | "
            f"{f['bw_note']} | {f['budget_note']} | {f['src']} |"
        )
    L += [
        "",
        "## Fit matrix (verdict / est. ceiling tok/s)",
        "",
        "| Model | " + " | ".join(f["name"] for f in c["fleet"]) + " |",
        "|---|" + "---|" * len(ids),
    ]
    for m in c["models"]:
        cells = []
        for i in ids:
            cell = m["fit"][i]["verdict"]
            if m["fit"][i]["est_tok_s"]:
                cell += f" / ~{m['fit'][i]['est_tok_s']}"
            cells.append(cell)
        L.append(f"| {m['family']} {m['quant_format'].split()[0]} | " + " | ".join(cells) + " |")
    od = c.get("on_device")
    if od:
        tot = od["total_unique_bytes"]
        L += [
            "",
            "## On-device (Mac) models",
            "",
            f"Scanned {od['generated']} on: {', '.join(od['scanned'])}. {len(od['items'])} unique models, "
            f"{tot/1e9:.1f} GB (duplicates across Macs counted and backed up once). NAS backup root: "
            f"`{od.get('nas_root','')}` (WD USB drive).",
            "",
            "| Model | Repo | Use | Format | Size (GB) | Mac(s) and path | NAS backup path | Backup | License (source) | Notes |",
            "|---|---|---|---|---:|---|---|---|---|---|",
        ]
        for i in sorted(od["items"], key=lambda x: -x["size_bytes"]):
            repo = f"[{i['repo']}]({i['hf_url']})" if i.get("repo") else "local"
            locs = "<br>".join(f"{l['machine']}: `{l['path']}`" for l in i["locations"])
            L.append(
                f"| {i['name']} | {repo} | {i['use']} | {i['format']} | {i['size_bytes']/1e9:.2f} | {locs} | "
                f"`{i.get('nas_path','')}` | {i['backup_status']} | {i['license']} ({i['license_source']}) | {i['notes']} |"
            )
        L += ["", "Not local weights:", ""] + [f"- {r['name']} ({r['machine']}): {r['note']}" for r in od.get("remote_only") or []]
        L += ["", "Not scanned:", ""] + [f"- {r['machine']}: {r['why']}" for r in od.get("not_scanned") or []]
        L += ["", "Checked, nothing to back up:", ""] + [f"- {x}" for x in od.get("no_weights") or []]
    dest.write_text("\n".join(L) + "\n")


def fmt_bytes(n) -> str:
    if n is None:
        return "none"
    return f"{n:,} B ({n/GiB:.2f} GiB)"


def print_report(report: dict, before: dict, after: dict) -> None:
    def counts(cat):
        return dict(Counter(m["status"] for m in cat["models"]))

    print("=== Catalog sync report ===")
    print(f"generated: {after.get('generated')}")
    print(f"status counts before: {counts(before)}")
    print(f"status counts after:  {counts(after)}")
    tot_before = sum(m["size_gib"] for m in before["models"] if m["status"] != "needs-Ian")
    tot_after = sum(m["size_gib"] for m in after["models"] if m["status"] != "needs-Ian")
    print(f"on-disk total (excl. gated): {tot_before/1024:.2f} TiB -> {tot_after/1024:.2f} TiB")
    print()
    if report["status_changes"]:
        print("Status changes:")
        for repo, a, b, path in report["status_changes"]:
            print(f"  - {repo}: {a} -> {b}")
            print(f"      {path}")
        print()
    if report["size_changes"]:
        print("Size changes:")
        for repo, a, b, mid in report["size_changes"]:
            delta = (b or 0) - (a or 0)
            print(f"  - {repo} [{mid}]: {fmt_bytes(a)} -> {fmt_bytes(b)}  ({delta/GiB:+.2f} GiB)")
        print()
    if report["path_changes"]:
        print("Path changes:")
        for repo, a, b in report["path_changes"]:
            print(f"  - {repo}: {a} -> {b}")
        print()
    if report["field_changes"]:
        print("Field changes:")
        for row in report["field_changes"]:
            print(f"  - {row[0]}.{row[1]}: {row[2]!r} -> {row[3]!r}")
        print()
    if report["backup_changes"]:
        n = len(report["backup_changes"])
        print(f"On-device NAS backup status: {n} item(s) updated")
        # collapse if all the same
        kinds = Counter((a, b) for _, a, b in report["backup_changes"])
        for (a, b), k in kinds.items():
            print(f"  - {k}: {a} -> {b}")
        print()
    if report["missing_on_disk"]:
        print("On the site / catalog but no longer on disk:")
        for item in report["missing_on_disk"]:
            print(f"  - {item['repo']} ({item['status']}) {item.get('nas_path')}")
        print("  (not removed automatically; delete from the private catalog after review)")
        print()
    else:
        print("On the site but no longer on disk: none")
        print()
    if report["untracked"]:
        print("On disk, complete, but not yet in the catalog (add metadata, then re-run):")
        for item in report["untracked"]:
            print(f"  - {item['key']}: {fmt_bytes(item['size_bytes'])}  {item['path']}")
        print()
    if report["pending"]:
        print("Pending / in-progress / untracked incomplete:")
        for item in report["pending"]:
            if "key" in item:
                print(
                    f"  - {item['key']}: {item['status']} "
                    f"{fmt_bytes(item['size_bytes'])} "
                    f"incomplete={item.get('incomplete_files')}  {item['path']}"
                )
            else:
                print(f"  - {item.get('repo')}: {item.get('reason')}")
        print()


def run_inventory_ssh(ssh: str, script: Path) -> dict:
    proc = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=20", ssh, "python3", "-s", "-"],
        input=script.read_text(),
        text=True,
        capture_output=True,
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        # some NAS ssh banners go to stderr; try to parse stdout anyway
    text = proc.stdout
    # skip any SSH warning lines before the first {
    start = text.find("{")
    if start < 0:
        raise SystemExit(f"inventory failed (exit {proc.returncode}): no JSON in stdout\n{proc.stderr}")
    return json.loads(text[start:])


def build_site(repo: Path, public_catalog: dict) -> None:
    dest = repo / "data" / "catalog.json"
    dump_json(dest, public_catalog)
    builder = repo / "tools" / "build_site.py"
    if not builder.is_file():
        print(f"note: {builder} not found; wrote {dest} only", file=sys.stderr)
        return
    subprocess.run([sys.executable, str(builder)], cwd=str(repo), check=True)


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--inventory", type=Path, help="Existing inventory JSON from inventory-nas.py")
    src.add_argument("--ssh", help="SSH target that can see the NAS, e.g. ian@192.168.12.66")
    p.add_argument("--private-catalog", type=Path, required=True, help="Private catalog.json to update (NAS paths kept)")
    p.add_argument("--repo", type=Path, default=Path("."), help="aimodels-site checkout (default: .)")
    p.add_argument("--write-inventory", type=Path, help="Optional path to save the inventory JSON")
    p.add_argument("--dry-run", action="store_true", help="Print the diff; do not write files")
    p.add_argument("--skip-site", action="store_true", help="Update catalogs only, do not run tools/build_site.py")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    repo = args.repo.resolve()
    private_path = args.private_catalog.expanduser().resolve()
    script_dir = Path(__file__).resolve().parent
    if args.inventory:
        inv = load_json(args.inventory)
    else:
        inv = run_inventory_ssh(args.ssh, script_dir / "inventory-nas.py")
    if args.write_inventory:
        dump_json(args.write_inventory, inv)
    before = load_json(private_path)
    result = sync(deepcopy(before), inv)
    after = result["catalog"]
    print_report(result["report"], before, after)
    if args.dry_run:
        print("dry-run: no files written")
        return
    dump_json(private_path, after)
    write_markdown(after, private_path.with_name("CATALOG.md"))
    print(f"wrote {private_path}")
    print(f"wrote {private_path.with_name('CATALOG.md')}")
    if not args.skip_site:
        build_site(repo, public_copy(after))
        print(f"rebuilt site in {repo}")


if __name__ == "__main__":
    main()
