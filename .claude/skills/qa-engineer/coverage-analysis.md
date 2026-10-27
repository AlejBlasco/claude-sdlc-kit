# Skill: Coverage Analysis Approach

Load this skill when you need to measure and improve coverage against the
configured `testingCoverage` threshold.

## Steps

1. Detect the coverage tool already configured in the repo (e.g. `jest
   --coverage`, `pytest --cov`, `dotnet test /p:CollectCoverage=true`,
   `nyc`, `jacoco`). Do not introduce a new one if one already exists.
2. Run it and read the report for the specific files/functions touched by
   the current task — total repo-wide coverage is not the target, the
   touched code's coverage is.
3. If below threshold, identify the specific uncovered branches/lines and
   write targeted tests for them — don't add generic tests hoping numbers
   go up. Prefer closing the gap with unit tests; only reach for another
   integration test if the missing coverage genuinely can't be exercised
   any other way (see `dotnet-testing.md`).
4. Re-run and confirm — but re-run cheaply: measure coverage against the
   filtered unit-test subset while iterating, and only fold the
   integration subset back in for the final confirmation, not on every
   loop. Report the final number honestly, even if it's below target after
   reasonable effort.

## When coverage comes from more than one run

Unit and integration subsets usually produce separate reports. Never
combine them by taking the highest per-assembly figure and presenting it
as a single total — that overstates coverage.

- If the repo already has a tool that merges reports (e.g.
  ReportGenerator, Coverlet's merge support), produce one merged report
  and quote that number.
- Otherwise, report each run's figure separately, or state explicitly in
  the Coverage Result's `Method` line that the number is the highest
  per-assembly value across runs and not a merged total.

## If no coverage tool exists in the repo

State this clearly in the testing summary instead of guessing a percentage.
Optionally suggest (but do not install without being asked) the idiomatic
coverage tool for the stack.
