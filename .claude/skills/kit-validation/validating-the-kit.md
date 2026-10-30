# Skill: Validating the Kit (three levels)

Load this skill when the maintainer asks you to validate the kit, or after a
change to a skill, an agent or a command, before it ships. No agent loads it:
it is invoked by the maintainer ("validate the kit, follow
`.claude/skills/kit-validation/validating-the-kit.md`") and needs a checkout of
this repository, because it runs the scripts in `scripts/` and the cases in
`tests/`. It is not copied to users' repositories.

## Scope

- Applies to skills (`.claude/skills/`) and agents (`.claude/agents/`).
  Commands are covered by level 1 only.
- Origin and licence of skills derived from third-party material are not
  checked here; they belong to `THIRD_PARTY_NOTICES.md`.
- Level 1 is the same check CI runs on every pull request. Do not
  re-implement it here.

## The three levels

| Level | Question | How to run | Model | CI |
|---|---|---|---|---|
| 1. Static | Is the kit consistent? Frontmatter, `.claude/` paths, skill structure and references, README install trees, version badge. | `python scripts/check_kit.py` | none | required check `validate` |
| 2. Activation | Does the right skill get loaded, and the right agent chosen? | `python scripts/eval_activation.py --agent <agent>` for the skills an agent picks; `--agent delegation` for the subagent the main assistant picks | yes | manual only |
| 3. Usage | With the skill loaded, does the output follow its rules, and better than without it? | `python scripts/eval_usage.py --runs 5` | yes | manual only |

Levels 2 and 3 call a model (`claude-haiku-5-5` by default) through the
maintainer's Claude account (`--backend cli`, no per-token charge) or the API
(`--backend api`, needs `ANTHROPIC_API_KEY`). They are never a required check:
they are slower, cost something and vary between runs.

What each one measures, and what it cannot:

- Level 2 simulates the selection step with each skill's title and opening
  paragraph (up to the first `##` heading). It does not run the real agent.
- Level 3 checks the shape of the reply with regular expressions and structure
  rules (sections, counts, names). It does not judge quality, and it cannot
  tell whether a Mermaid diagram renders.
- Checks marked `heuristic` in the cases can be wrong in both directions.

## Which levels to run

| You changed | Run |
|---|---|
| Any skill, agent or command | Level 1 |
| A skill's title or opening paragraph | Level 2 for its agent |
| An agent's `description` | `--agent delegation`, and level 2 for that agent |
| The rules in a skill's body | Level 3 for that skill, if it has cases in `tests/usage/` |
| A new skill | Add cases (level 2 reports a skill that no case expects), then run its agent |
| Before a release | All three levels |

Expect about 3 seconds per call: a level 2 agent takes 1 to 7 minutes
depending on its cases, `--agent delegation` about 2.5 minutes, and level 3
with `--runs 5` about 5.5 minutes with 4 parallel calls.

## Reading the results

- Both scripts keep a recorded baseline, `tests/activation/baseline.json` and
  `tests/usage/baseline.json`: per case, the share of clean runs. A case
  holds when at least two thirds of its runs are clean.
- `--strict` exits 1 only when a case that held in the baseline no longer
  holds. Misses already in the baseline are listed in
  `tests/activation/BASELINE.md` and `tests/usage/BASELINE.md`, and do not
  fail it.
- Run-to-run noise is real: a drop of one or two runs in a single case can
  happen with unchanged code. Before acting on a regression, re-run only that
  case with `--case <id>`. A regression that repeats is real.
- Level 3 gives each skill a verdict: passes (it holds and beats the run
  without the skill), no effect (it holds, but so does the run without it) or
  fails. No effect often means the case is too easy, not that the skill is
  useless.

## Adding or changing cases

- Level 2: `tests/activation/<agent>.json`, with `kind` (`positive`,
  `negative` or `confusable`), `expect`, `forbid` and optionally `allow` or
  `expect_any`. `--dry-run` validates the file without calling a model.
- Level 3: `tests/usage/<skill>.json`, with a `prompt` and `checks`. The check
  types are listed in `scripts/eval_usage.py`. Prefer a check that targets a
  rule the model would not follow unaided; a rule it already follows shows as
  no effect.
- Do not edit a case to make a failing run pass. Change a case only when the
  case is wrong, and say so when you report it.

## Recording a baseline

`--write-baseline` overwrites the entry of the agent or skill you ran, so run
the full case set (not `--case`) and only after the maintainer has read the
results. Never record a baseline to hide a regression. Commit the JSON together
with the write-up beside it (`tests/activation/BASELINE.md` or
`tests/usage/BASELINE.md`).

## When asked to validate the kit

1. Run level 1 and report every problem.
2. Ask before running levels 2 and 3: they use the maintainer's account and
   take minutes.
3. For each run, report regressions against the baseline first, then new
   misses, then improvements.
4. Do not write a baseline, edit a case or change a skill without the
   maintainer's approval, and never run `git commit` or `git push`.
