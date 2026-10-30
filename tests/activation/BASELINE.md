# Activation baseline (level 2)

Measured with `python scripts/eval_activation.py --agent <agent> --backend cli`
(model `claude-haiku-5-5`, 3 runs per case, catalog = title + opening paragraph).
Recall is over the skills a case expects; false positives are over the skills a
case forbids. Provisional marks: recall >= 90%, false positives <= 5% per skill.

Date: 2026-10-30.

| Agent | Cases | Recall | False positives | Unparseable |
|---|---|---|---|---|
| business-analyst | 13 | 30/30 | 0/36 | 0 |
| software-architect | 13 | 27/27 | 3/51 | 0 |
| qa-engineer | 15 | 51/51 | 0/93 | 0 |
| technical-writer | 11 | 36/36 | 3/33 | 0 |
| software-developer | 43 | 108/108 | 2/219 | 0 |

## Known misses (open)

- `dotnet-azure-architecture.md` is loaded for `arch-007` (static site on
  GitHub Pages) in 3 of 3 runs, although its opening says not to.
- `docs-as-product.md` is loaded for `tw-009` (fix a typo in the README) in
  3 of 3 runs.
- `blazor-ui-system.md` is loaded for `sd-037` in 2 of 3 runs.

Results vary a little between runs: the first `software-developer` run gave
109/111 and 1/219, this one 108/108 and 2/219. The recall denominator differs
because the three any-of groups are now reported on their own line (108 + 3 =
111); the false-positive change is run-to-run noise.
