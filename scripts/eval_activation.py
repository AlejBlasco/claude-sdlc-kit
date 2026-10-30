#!/usr/bin/env python3
"""Level 2 validation: does an agent pick the right skills for a prompt?

Simulates the agent's skill-selection step: the model sees the agent's own
"load relevant skills" instruction, a catalog built from each skill's title and
opening paragraph, and one task prompt, and answers with the files it would
load. Answers are scored against tests/activation/<agent>.json.

  python scripts/eval_activation.py --agent software-developer --dry-run
  python scripts/eval_activation.py --agent software-developer --backend cli
  python scripts/eval_activation.py --agent software-developer --backend api
  python scripts/eval_activation.py --catalog names    # file names only
  python scripts/eval_activation.py --agent delegation # does the main assistant pick the right subagent?
  python scripts/eval_activation.py --agent software-developer --write-baseline
  python scripts/eval_activation.py --agent software-developer --strict

--dry-run validates the case file and estimates the cost; it calls no model.
--write-baseline records, per case, the share of clean runs in
tests/activation/baseline.json. --strict exits 1 only if a case that held in
that baseline (at least two thirds of its runs clean) no longer holds; misses
already in the baseline do not fail it.
Backends: `cli` runs `claude -p` with your Claude account; `api` calls the
Messages API with ANTHROPIC_API_KEY. Standard library only.
"""
import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "claude-haiku-5-5"
INTRO_MAX_CHARS = 900  # long enough to keep "Load this skill" after a Source: paragraph
CHARS_PER_TOKEN = 3.5  # rough; only used for the dry-run estimate
ASSUMED_OUTPUT_TOKENS = 80  # a short JSON array, thinking off

# Provisional pass marks per skill; to be confirmed once the cases are reviewed.
RECALL_MIN = 0.90
FALSE_POSITIVE_MAX = 0.05

# USD per million tokens (input, output), from the Claude API model table.
PRICES = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
}

FALLBACK_STEP = "Load any relevant skill files under `{dir}` using the Read tool."

HOLD_RATE = 2 / 3  # a case holds when at least this share of its runs is clean
BASELINE = ROOT / "tests/activation/baseline.json"


def read(path):
    return Path(path).read_text(encoding="utf-8")


def catalog(skills_dir):
    """One entry per skill: file name, title and opening paragraph."""
    entries = []
    for path in sorted(skills_dir.glob("*.md")):
        if path.name == "README.md":
            continue
        lines = read(path).splitlines()
        title = re.sub(r"^#\s*Skill:\s*", "", lines[0]) if lines else path.stem
        intro = []
        for line in lines[1:]:
            if line.startswith("## "):
                break
            intro.append(line.strip())
        text = re.sub(r"\s+", " ", " ".join(intro)).strip()
        entries.append((path.name, title, text[:INTRO_MAX_CHARS]))
    return entries


def agent_step(agent, skills_dir):
    """The agent's own skill-loading instructions, so the test mirrors them.

    That is the numbered step that says to load relevant skills, plus any other
    paragraph of the agent file that points at its skills folder.
    """
    text = read(ROOT / ".claude/agents" / f"{agent}.md")
    folder = f".claude/skills/{agent}/"
    m = re.search(r"\n\s*\d+\.\s+(Load any (?:relevant )?skill files.*?)(?=\n\s*\d+\.\s|\n\n)", text, re.S)
    parts = []
    if m:
        step = m.group(1)
        parts.append(re.sub(r"\s+", " ", step).strip())
    else:
        step = ""
        parts.append(FALLBACK_STEP.format(dir=folder))
    for block in text.split("\n\n"):
        if folder in block and (not step or step not in block) and not block.lstrip().startswith("#"):
            parts.append(re.sub(r"\s+", " ", block).strip())
    return "\n\n".join(parts)


DELEGATION = "delegation"  # pseudo-agent: the main assistant choosing a subagent, not a skill


def agents_catalog():
    """One entry per subagent: name, name and description, read from the agent file's frontmatter."""
    entries = []
    for path in sorted((ROOT / ".claude/agents").glob("*.md")):
        match = re.match(r"---\n(.*?)\n---", read(path).replace("\r\n", "\n"), re.S)
        fields = dict(re.findall(r"^([\w-]+):\s*(.*)$", match.group(1), re.M)) if match else {}
        name = fields.get("name", path.stem)
        entries.append((name, name, fields.get("description", "")))
    return entries


def delegation_prompt(entries):
    listing = "\n".join(f"- {name}: {intro}" for name, _, intro in entries)
    return (
        "You are the main assistant of a software project that has these specialised subagents. "
        "For each request you decide whether to delegate it to one or more of them, or to answer it "
        "yourself. Delegate only when a subagent's description clearly fits the request.\n\n"
        f"Subagents available (name: description):\n{listing}\n\n"
        "Reply with ONLY a JSON array of the subagent names you would delegate to, for example "
        "[\"name-a\"]; [] if you would answer yourself."
    )


def system_prompt(agent, step, entries, mode="full"):
    if mode == "names":
        label = "Skill files available (file names only):"
        listing = "\n".join(f"- {name}" for name, _, _ in entries)
    else:
        label = "Skill files available (file name - title. opening paragraph):"
        listing = "\n".join(f"- {name} - {title}. {intro}" for name, title, intro in entries)
    return (
        f"You are the {agent} subagent of an SDLC kit. Before starting a task you decide "
        f"which skill files to read. Your instruction for this step:\n\n{step}\n\n"
        f"{label}\n{listing}\n\n"
        "Reply with ONLY a JSON array of the file names you would load for the task, "
        "for example [\"a.md\", \"b.md\"]. Load only what the task needs; [] if none."
    )


def load_cases(agent, entries):
    path = ROOT / "tests/activation" / f"{agent}.json"
    data = json.loads(read(path))
    known = {name for name, _, _ in entries}
    errors, seen = [], set()
    for case in data["cases"]:
        cid = case.get("id", "?")
        if cid in seen:
            errors.append(f"{cid}: duplicate id")
        seen.add(cid)
        if case.get("kind") not in ("positive", "negative", "confusable"):
            errors.append(f"{cid}: kind must be positive, negative or confusable")
        for key in ("expect", "forbid", "allow", "expect_any"):
            for skill in case.get(key, []):
                if skill not in known:
                    errors.append(f"{cid}: {key} lists unknown skill '{skill}'")
        listed = [set(case.get(k, [])) for k in ("expect", "forbid", "allow", "expect_any")]
        if any(a & b for i, a in enumerate(listed) for b in listed[i + 1:]):
            errors.append(f"{cid}: a skill is in more than one of expect, forbid, allow and expect_any")
    by_tag = data.get("allow_by_tag", {})
    for skill in data.get("allow", []) + [s for v in by_tag.values() for s in v]:
        if skill not in known:
            errors.append(f"allow lists unknown skill '{skill}'")
    for case in data["cases"]:
        for tag in case.get("tags", []):
            if tag not in by_tag:
                errors.append(f"{case['id']}: tag '{tag}' is not defined in allow_by_tag")
        extra = set(data.get("allow", []))
        for tag in case.get("tags", []):
            extra |= set(by_tag.get(tag, []))
        extra -= set(case.get("expect", [])) | set(case.get("forbid", [])) | set(case.get("expect_any", []))
        case["allow"] = sorted(set(case.get("allow", [])) | extra)
    covered = {s for c in data["cases"] for s in c.get("expect", []) + c.get("expect_any", [])}
    for name in sorted(known - covered):
        errors.append(f"skill '{name}' is expected by no case")
    return data["cases"], errors


def call_cli(model, system, task):
    cmd = [
        "claude", "-p", "--model", model, "--output-format", "json",
        "--system-prompt", system, "--tools", "", "--no-session-persistence",
        "--disable-slash-commands", "--strict-mcp-config", "--setting-sources", "",
    ]
    out = subprocess.run(cmd, input=task, capture_output=True, text=True, encoding="utf-8")
    if out.returncode != 0:
        raise RuntimeError(f"claude -p failed: {out.stderr.strip()[:300]}")
    return json.loads(out.stdout).get("result", "")


def call_api(model, system, task, max_tokens=300):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": task}],
    }
    if model.startswith("claude-haiku"):
        body["thinking"] = {"type": "disabled"}
    else:
        body["output_config"] = {"effort": "low"}
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={"x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"API {e.code}: {e.read().decode('utf-8')[:300]}")
    return "".join(b.get("text", "") for b in data["content"] if b.get("type") == "text")


def parse_selection(text):
    m = re.search(r"\[.*?\]", text, re.S)
    if not m:
        return None
    try:
        value = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return {Path(v).name for v in value if isinstance(v, str)}  # tolerate full paths


def estimate(system, cases, runs):
    calls = len(cases) * runs
    in_tokens = sum((len(system) + len(c["prompt"])) / CHARS_PER_TOKEN for c in cases) * runs
    out_tokens = calls * ASSUMED_OUTPUT_TOKENS
    print(f"\nDry run: {len(cases)} cases x {runs} runs = {calls} calls")
    print(f"System prompt: {len(system)} chars, about {int(len(system) / CHARS_PER_TOKEN)} tokens")
    print(f"Estimated total: {int(in_tokens)} input + {out_tokens} output tokens (thinking off)")
    print("Estimated API cost (rough; chars/3.5 for input, 80 output tokens per call):")
    for model, (pin, pout) in PRICES.items():
        print(f"  {model:<20} ${in_tokens / 1e6 * pin + out_tokens / 1e6 * pout:.3f}")


def report(results):
    per_skill = defaultdict(lambda: {"exp": 0, "hit": 0, "forb": 0, "fp": 0})
    extras, loaded, bad = defaultdict(int), 0, 0
    groups = [0, 0]  # any-of cases, and how many loaded at least one of the listed skills
    for r in results:
        selected = r["selected"] or set()
        if r.get("expect_any"):
            groups[0] += 1
            groups[1] += bool(selected & set(r["expect_any"]))
        for s in r["expect"]:
            per_skill[s]["exp"] += 1
            per_skill[s]["hit"] += s in selected
        for s in r["forbid"]:
            per_skill[s]["forb"] += 1
            per_skill[s]["fp"] += s in selected
        bad += r["selected"] is None
        for name in selected - set(r["expect"]) - set(r["forbid"]) - set(r["allow"]) - set(r.get("expect_any", [])):
            extras[name] += 1
        loaded += len(selected)
    print()
    print(f"Provisional marks: recall >= {RECALL_MIN:.0%}, false positives <= {FALSE_POSITIVE_MAX:.0%} per skill")
    print(f"{'skill':<40}{'recall':>10}{'false pos.':>12}  status")
    failing = []
    for name in sorted(per_skill):
        d = per_skill[name]
        recall = f"{d['hit']}/{d['exp']}" if d["exp"] else "-"
        fp = f"{d['fp']}/{d['forb']}" if d["forb"] else "-"
        status = []
        if d["exp"] and d["hit"] / d["exp"] < RECALL_MIN:
            status.append("LOW RECALL")
        if d["forb"] and d["fp"] / d["forb"] > FALSE_POSITIVE_MAX:
            status.append("HIGH FALSE POSITIVES")
        if status:
            failing.append(name)
        print(f"{name:<40}{recall:>10}{fp:>12}  {', '.join(status) or 'ok'}")
    exp = sum(d["exp"] for d in per_skill.values())
    hit = sum(d["hit"] for d in per_skill.values())
    forb = sum(d["forb"] for d in per_skill.values())
    fp = sum(d["fp"] for d in per_skill.values())
    print(f"\nOverall recall {hit}/{exp}, false positives {fp}/{forb}, unparseable answers {bad}")
    if groups[0]:
        print(f"Any-of groups (one of several skills is enough): {groups[1]}/{groups[0]}")
        if groups[1] / groups[0] < RECALL_MIN:
            failing.append("any-of groups")
    print(f"Mean skills loaded per call: {loaded / max(len(results), 1):.1f}")
    if extras:
        print("Loaded without being expected, forbidden or allowed (wrong, or a case that is too narrow?):")
        for name, n in sorted(extras.items(), key=lambda kv: -kv[1]):
            print(f"  {name:<40}{n}x")
    swaps = defaultdict(int)
    for r in results:
        for s in r["forbid"]:
            if r["selected"] and s in r["selected"]:
                swaps[(r["id"], s)] += 1
    for (cid, s), n in sorted(swaps.items()):
        print(f"  {cid}: loaded forbidden {s} ({n}x)")
    return failing


def clean_run(r):
    """A run is clean when every expected skill was loaded and no forbidden one was."""
    s = r["selected"]
    if s is None or not set(r["expect"]) <= s or set(r["forbid"]) & s:
        return False
    return not r.get("expect_any") or bool(s & set(r["expect_any"]))


def case_rates(results):
    runs = defaultdict(list)
    for r in results:
        runs[r["id"]].append(clean_run(r))
    return {cid: sum(v) / len(v) for cid, v in runs.items()}


def write_baseline(path, key, rates, meta):
    data = json.loads(read(path)) if path.is_file() else {}
    data[key] = {**meta, "recorded": datetime.date.today().isoformat(),
                 "cases": {cid: round(r, 3) for cid, r in sorted(rates.items())}}
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"\nBaseline for {key} written to {path.relative_to(ROOT)}")


def regressions(path, key, rates):
    """Cases that held in the recorded baseline and no longer do; None if there is no baseline."""
    data = json.loads(read(path)) if path.is_file() else {}
    base = data.get(key, {}).get("cases")
    if base is None:
        print(f"\nNo baseline recorded for {key} in {path.relative_to(ROOT)}; run with --write-baseline first.")
        return None
    lost = sorted(c for c, r in rates.items() if c in base and base[c] >= HOLD_RATE and r < HOLD_RATE)
    gained = sorted(c for c, r in rates.items() if c in base and base[c] < HOLD_RATE and r >= HOLD_RATE)
    new = sorted(c for c in rates if c not in base)
    print(f"\nAgainst the baseline of {data[key].get('recorded', '?')}: "
          f"{len(lost)} regression(s), {len(gained)} case(s) now holding, {len(new)} not in the baseline.")
    for c in lost:
        print(f"  REGRESSION {c}: {base[c]:.0%} of runs clean in the baseline, {rates[c]:.0%} now")
    if lost:
        print("  A drop of one or two runs is within run-to-run noise. Confirm by re-running only these "
              "cases (" + " ".join(f"--case {c}" for c in lost) + ") before acting on it.")
    for c in gained:
        print(f"  improved   {c}: {base[c]:.0%} -> {rates[c]:.0%}")
    for c in new:
        print(f"  new        {c}: not in the baseline (run --write-baseline to record it)")
    return lost


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--agent", default="software-developer")
    ap.add_argument("--backend", choices=("cli", "api"), default="cli")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--runs", type=int, default=3, help="repetitions per case")
    ap.add_argument("--case", action="append", help="only this case id (repeatable)")
    ap.add_argument("--catalog", choices=("full", "names"), default="full",
                    help="what the model sees per skill: title + opening paragraph, or file name only")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if a case that held in the recorded baseline no longer does")
    ap.add_argument("--write-baseline", action="store_true", help="record this run in tests/activation/baseline.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", help="write raw results as JSON to this file")
    args = ap.parse_args()

    delegation = args.agent == DELEGATION
    skills_dir = ROOT / ".claude/skills" / args.agent
    entries = agents_catalog() if delegation else catalog(skills_dir)
    cases, errors = load_cases(args.agent, entries)
    for e in errors:
        print(f"CASES {e}")
    if errors:
        return 1
    if args.case:
        cases = [c for c in cases if c["id"] in args.case]
    if delegation:
        system = delegation_prompt(entries)
    else:
        system = system_prompt(args.agent, agent_step(args.agent, skills_dir), entries, args.catalog)

    if args.dry_run:
        print(f"Case file OK: {len(cases)} cases, {len(entries)} skills in the catalog.")
        estimate(system, cases, args.runs)
        return 0

    call = call_cli if args.backend == "cli" else call_api
    results = []
    for case in cases:
        for run in range(args.runs):
            answer = call(args.model, system, f"Task: {case['prompt']}")
            selected = parse_selection(answer)
            if delegation and selected is not None:
                selected = {s[:-3] if s.endswith(".md") else s for s in selected}
            results.append({
                "id": case["id"], "run": run, "expect": case.get("expect", []),
                "forbid": case.get("forbid", []), "allow": case.get("allow", []), "expect_any": case.get("expect_any", []), "selected": selected, "raw": answer,
            })
            print(f"{case['id']} run {run + 1}/{args.runs}: {sorted(selected) if selected is not None else 'UNPARSEABLE'}")
    report(results)
    if args.out:
        Path(args.out).write_text(
            json.dumps([{**r, "selected": sorted(r["selected"]) if r["selected"] is not None else None} for r in results], indent=2),
            encoding="utf-8",
        )
    rates = case_rates(results)
    if args.write_baseline:
        if args.case:
            print("\n--write-baseline needs the full case set; drop --case.")
            return 1
        write_baseline(BASELINE, args.agent, rates, {"model": args.model, "runs": args.runs, "catalog": args.catalog})
    if args.strict:
        lost = regressions(BASELINE, args.agent, rates)
        return 1 if lost is None or lost else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
