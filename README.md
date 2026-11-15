# aimodels-site

Static site for aimodels.remnantsecurity.com: Remnant Security's local AI model archive, fleet fit matrix, recipes and use cases.

- Plain HTML/CSS/JS, no build step needed to serve. `CNAME` follows the other Remnant `*-site` repos (GitHub Pages).
- Generated from `data/catalog.json` by `tools/build_site.py`. Facts come from Hugging Face model cards; memory and token/s figures are labelled estimates.
- Preview locally: `python3 -m http.server 8000` and open http://localhost:8000/

Live at https://aimodels.remnantsecurity.com (GitHub Pages from `main`).
