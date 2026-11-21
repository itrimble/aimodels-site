# Catalog sync

Keeps https://aimodels.remnantsecurity.com in line with the models actually on the NAS.

The site itself is generated, public HTML. The private catalog (with NAS paths) lives next to the weights, not in this repository.

## What the script does

The inventory walker also scans `extras/` under the cold archive for the nine curated cross-platform extras (embeddings, TTS, image, upscaling and a coding sidecar).

`scripts/sync-catalog` walks the NAS model folders, updates a private `catalog.json` (status, sizes, paths, on-device backup flag), writes a public `data/catalog.json` with paths stripped, rebuilds the static pages, and prints a diff.

It does not commit, push, merge, open a pull request, install a scheduler, or store any credentials on the NAS.

New folders that are not yet in the catalog are reported as untracked or pending. Incomplete downloads (for example a GGUF still arriving) stay off the public site until the files are complete and someone adds the metadata. Models that vanish from disk are reported, not deleted automatically.

## How to run it (from the MacBook Pro)

The MacBook Pro is the machine that can SSH to `ian@192.168.12.66`. Keep a writable copy of the private catalog on the Mac (or fetch it from the NAS before you start).

```bash
# in a checkout of itrimble/aimodels-site, on a branch
ssh ian@192.168.12.66 python3 -s - < scripts/inventory-nas.py > /tmp/nas-inventory.json

scripts/sync-catalog \
  --inventory /tmp/nas-inventory.json \
  --private-catalog ~/aimodels-private/catalog.json \
  --repo .

# or in one step, letting the script SSH for you:
scripts/sync-catalog \
  --ssh ian@192.168.12.66 \
  --private-catalog ~/aimodels-private/catalog.json \
  --repo .
```

Review the printed diff. If it looks right, copy the private `catalog.json` and `CATALOG.md` back to the four catalog locations:

- `/volume3/cold-archive/models/2026-11-hf-archive/`
- `/volume1/nas/models/2026-11-hf-archive/`
- `/mnt/@usb/sdd1/2026-11-hf-media/`
- `/mnt/@usb/sdd1/2026-11-device-models/`

Then commit the public site files, push a branch, and open a pull request. Merge only after a check of the diff.

Add `--dry-run` to print the diff without writing files.

## Recommended schedule

Run it from the MacBook Pro after a download finishes, or once a day if you want a regular catch-up. A `launchd` agent on the MacBook Pro is the right place for a schedule if you want one later: it can SSH to the NAS, write a diff, and stop. Do not put a cron job or any Hugging Face token on the NAS. Do not auto-merge the site.

`inventory-nas.py` only looks at folder names, file sizes, and the copy/verify logs. It does not read tokens or environment files.
