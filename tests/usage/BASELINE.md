# Usage baseline (level 3)

Measured with `python scripts/eval_usage.py --backend cli --runs 5`
(model `claude-haiku-5-5`, 5 runs per case and condition, 4 parallel calls,
about 5.5 minutes for 100 calls). Each case runs once with the skill file in
the system prompt and once without it; a case holds in a condition when at
least two thirds of the runs pass every check. See the script's docstring for
the verdicts.

Date: 2026-10-30.

| Skill | Verdict | With skill | Without skill |
|---|---|---|---|
| given-when-then-format | passes | gwt-001 5/5, gwt-002 5/5 | gwt-001 3/5, gwt-002 2/5 |
| mermaid-diagramming | passes | mer-001 5/5, mer-002 5/5, mer-003 5/5 | 5/5, 5/5, 2/5 |
| unit-testing-strategy | passes | ut-001 5/5, ut-002 4/5, ut-003 4/5 | 5/5, 4/5, 0/5 |
| adr-writing | **fails** | adr-001 1/5, adr-002 5/5 | 0/5, 5/5 |

Where the skill makes the difference:

- given-when-then-format: one WHEN per scenario (5/5 with, 3/5 and 2/5 without).
- mermaid-diagramming: node labels up to 40 characters in a flowchart (5/5 with, 2/5 without).
- unit-testing-strategy: no test that only verifies a mock call (4/5 with, 0/5 without).
- adr-writing: the decision is one sentence (5/5 with, 2/5 without).

No effect measured (the model does it unaided): `two-or-more-scenarios`,
`tagged-mermaid-block`, the diagram type in `mer-001` and `mer-002`,
`descriptive-names`, and the three Context, Decision, Consequences sections.

## Known misses (open)

- `adr-writing.md`: the rule of 3 to 6 sentences in total is met in 1 of 5
  runs with the skill (0 of 5 without). Across all runs after the closing
  paragraph was reworded to give a limit per section, it holds in 6 of 11
  runs; before the rewording it held in 0 of 12 (nine Haiku and three Sonnet runs).
  The skill helps but does not make the model reliably stay in range.

## Limits of this measurement

- The checks look at the shape of the reply, not at whether it is good. Mermaid
  syntax is not validated (there is no renderer here) and the coverage of a
  happy, edge and negative case in acceptance criteria is not checked.
- Checks marked heuristic (sentence counts, label length, test names, mock-only
  tests) can be wrong in both directions.
- Variance is high. With 3 runs per case the verdicts of `mermaid-diagramming`
  and `unit-testing-strategy` flipped between two executions of the same
  code. Use 5 runs or more for a baseline; treat a single-case change between
  runs as noise.
- One model (Haiku) and a handful of cases per skill. This detects regressions
  in a skill's effect; it does not certify a skill.
