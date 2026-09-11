# GraphTheory-VL project homepage

Static English research homepage for the prepared v1.0 release. `docs/` contains the complete site; it can be served directly or copied into a GitHub Pages publishing directory.

## Preview locally

From the repository root, run:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory docs
```

Then open http://127.0.0.1:8765/. A web connection is not required for the page assets or mathematical typesetting. The four example PNGs retain their original bytes; the downloadable example JSONL contains original fields with local image paths.

The site uses plain HTML, CSS and JavaScript. This repository hosts the portable static output under `docs/`. The local preview command serves the same files that can later be used by GitHub Pages.

## Release links

The intended repositories are `limxiong/GraphTheory-VL` on GitHub and Hugging Face. Both entries in `docs/resources.js` currently have `available: false`. The page therefore displays a release preparation state; it does not link visitors to unverified destinations.

After the repositories are uploaded and publicly accessible, verify both addresses, set their `available` fields to true, and update the release-status paragraph and badge in `docs/index.html`. Replace the draft PDF and citation when the paper's permanent identifier is available. Preserve the 62/20 nested relationship and the distinction between 984 scoring positions and 983 complete answers.

The `docs/` folder includes `.nojekyll`. At public release, GitHub Pages can serve the main branch's `/docs` folder. Configure that setting only when proceeding to publication; the current folder alone does not enable hosting.

## Third-party software

KaTeX 0.18.7 is vendored under `docs/assets/katex/`, including its MIT license and required fonts, so formulas do not depend on a CDN. Official documentation: [browser integration](https://katex.org/docs/browser), [auto-render extension](https://katex.org/docs/autorender). Team-owned site code is covered by the accompanying MIT code notice; the question texts and diagrams use the accompanying CC BY 4.0 notice.
