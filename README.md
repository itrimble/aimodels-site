# aimodels-site

Static site for aimodels.remnantsecurity.com: Remnant Security's local AI model archive, fleet fit matrix, recipes and use cases.

- Plain HTML/CSS/JS, no build step needed to serve. `CNAME` follows the other Remnant `*-site` repos (GitHub Pages).
- Generated from `data/catalog.json` by `tools/build_site.py`; styles live in `tools/site_css.py`, use-case copy in `tools/use_cases.py`. Facts come from Hugging Face model cards; memory and token/s figures are labelled estimates unless marked measured. Measured benchmarks and sources live in data/benchmarks.json.
- Preview locally: `python3 -m http.server 8000` and open http://localhost:8000/

Live at https://aimodels.remnantsecurity.com (GitHub Pages from `main`).

To refresh the catalog from the NAS (run on the MacBook Pro, which can SSH to the NAS):

    scripts/sync-catalog --ssh ian@192.168.12.66 --private-catalog /path/to/private/catalog.json --repo .

That updates statuses and sizes, rebuilds the pages, and prints a diff. It does not commit or merge. See `scripts/README.md`.

