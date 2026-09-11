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

The public homepage is https://limxiong.github.io/GraphTheory-VL/ and the code repository is https://github.com/limxiong/GraphTheory-VL. The core dataset and full response archive are published as assets of the v1.0 GitHub release. The matching Hugging Face dataset remains in preparation.

Maintain links in `docs/resources.js` and the visible resource text in `docs/index.html`. Replace the draft PDF and citation when the paper's permanent identifier is available. Preserve the 62/20 nested relationship and the distinction between 984 scoring positions and 983 complete answers.

GitHub Pages serves the main branch's `/docs` folder, which includes `.nojekyll`. Changes pushed to the branch trigger a Pages deployment.

## Third-party software

KaTeX 0.18.7 is vendored under `docs/assets/katex/`, including its MIT license and required fonts, so formulas do not depend on a CDN. Official documentation: [browser integration](https://katex.org/docs/browser), [auto-render extension](https://katex.org/docs/autorender). Team-owned site code is covered by the accompanying MIT code notice; the question texts and diagrams use the accompanying CC BY 4.0 notice.
