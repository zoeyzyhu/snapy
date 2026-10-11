# snapy Technical Report: rendered PDFs

Renders of `doc/tech-report/book` on UCzhangxi/snapy `tech-report`, kept here for reading only. This branch is not
part of tech-report and has no PR.

| file | source commit (UCzhangxi/snapy) | pages | bytes | sha256 |
|---|---|---|---|---|
| `snapy-tech-report-before-750c1806169ed3c3176301e7a1e55d8a7c2dd494.pdf` | `750c1806169ed3c3176301e7a1e55d8a7c2dd494` | 746 | 3087599 | `ae709a17427622881e0fc56cb05f06effc13103b2023eef87a6ac70b235d7400` |
| `snapy-tech-report-after-fb6bfff0b84958585f42a619babdbdca471f92f8.pdf` | `fb6bfff0b84958585f42a619babdbdca471f92f8` | 345 | 2714783 | `0b0ebd2cf1fe6cad7871c301d0583c4f231f74e51cfae768f14198712b9b4d69` |
| `snapy-tech-report-after-3d57c52cdbd7e301e41bb29ad946d4b7679c696e.pdf` | `3d57c52cdbd7e301e41bb29ad946d4b7679c696e` | 331 | 2671839 | `e3312e456965ef63410bba405c8c485c0554acbb400084ea322bd7f5134ab1bc` |

Notes:

- `snapy-tech-report-before-750c1806169ed3c3176301e7a1e55d8a7c2dd494.pdf`: tech-report before UCzhangxi/snapy#24, with render-only wrapper chapters (render not made here; copied unchanged).
- `snapy-tech-report-after-fb6bfff0b84958585f42a619babdbdca471f92f8.pdf`: tech-report after UCzhangxi/snapy#24 (its merge), with render-only wrapper chapters (render not made here; copied unchanged).
- `snapy-tech-report-after-3d57c52cdbd7e301e41bb29ad946d4b7679c696e.pdf`: tech-report head, fresh render with no wrappers and no source edits (`python tools/render_gate.py book/`, Quarto 1.10.19, LuaLaTeX).
- Fresh render on `3d57c52cdbd7e301e41bb29ad946d4b7679c696e`: 29 overfull hboxes in the LaTeX log, 2 of them wider than
  10 pt (11.5 pt and 23.2 pt), 0 missing characters. The render gate reports 15 passed, 1 pending (4 figure
  functions not written yet) and 3 failed (freeze caches not committed for 11 of 12 chapters, the 2 overfull lines,
  and unresolved `@sec-ch15-ch01` warnings on stdout).
