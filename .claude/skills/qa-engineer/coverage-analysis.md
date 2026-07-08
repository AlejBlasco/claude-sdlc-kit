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
   go up.
4. Re-run and confirm. Report the final number honestly, even if it's below
   target after reasonable effort.

## If no coverage tool exists in the repo

State this clearly in the testing summary instead of guessing a percentage.
Optionally suggest (but do not install without being asked) the idiomatic
coverage tool for the stack.
