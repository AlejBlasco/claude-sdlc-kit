#!/usr/bin/env python3
"""Level 3 validation: does a skill change the output the way it says it should?

Each case is a task with deterministic checks (regular expressions and
structure rules) on the reply. The task runs twice, with the skill file in the
system prompt and without it. A skill PASSES when its checks hold and it beats
the run without the skill; it has NO EFFECT when they hold but it does not
help; it FAILS when the checks do not hold with the skill loaded.

  python scripts/eval_usage.py --dry-run             # budget, no model calls
  python scripts/eval_usage.py --skill adr-writing
  python scripts/eval_usage.py --backend api --workers 4
  python scripts/eval_usage.py --runs 5 --write-baseline
  python scripts/eval_usage.py --runs 5 --strict

--write-baseline records, per case, the share of runs that pass every check
with the skill loaded (tests/usage/baseline.json). --strict exits 1 only if a
case that held in that baseline (at least two thirds of its runs) no longer
does; a skill that fails or has no effect in the baseline does not fail it.

Cases live in tests/usage/<skill>.json. The checks look at the shape of the
reply (sections, structure, names); they do not judge whether it is good.
Standard library only; backends as in eval_activation.py.
"""
import argparse
import json
import math
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from eval_activation import (DEFAULT_MODEL, PRICES, CHARS_PER_TOKEN, call_api, call_cli, read,
                             regressions, write_baseline)

ROOT = Path(__file__).resolve().parent.parent
USAGE_DIR = ROOT / "tests/usage"
BASELINE = USAGE_DIR / "baseline.json"
PASS_RATE = 2 / 3  # a case holds in a condition when at least this share of runs pass every check
ASSUMED_OUTPUT_TOKENS = 600  # only used by --dry-run; real replies range from about 250 to 900
SECONDS_OVERHEAD = 3.0  # measured on `claude -p` calls in level 2
TOKENS_PER_SECOND = 150  # rough output speed assumed for the dry run
MAX_TOKENS = 1500


# ---- helpers ---------------------------------------------------------------

def blocks(text, start):
    """Split text into chunks that begin at each line matching `start`."""
    lines, chunks, cur = text.splitlines(), [], None
    for line in lines:
        if re.search(start, line):
            cur = [line]
            chunks.append(cur)
        elif cur is not None:
            cur.append(line)
    return ["\n".join(c) for c in chunks]


def mermaid_blocks(text):
    return re.findall(r"```mermaid[ \t]*\n(.*?)```", text, re.S)


def sections(text, labels):
    """Text under each label (Context, Decision, ...): from the label line to the
    next label line or markdown heading. Heuristic; reports None when a label is missing."""
    lines = text.splitlines()
    label_re = {lab: re.compile(rf"^[#*_\s\-\d.]*{lab}\b[*_]*\s*:?[*_]*\s*", re.I) for lab in labels}
    marks = []
    for i, line in enumerate(lines):
        for lab, rx in label_re.items():
            if rx.match(line):
                marks.append((i, lab, rx.sub("", line, count=1)))
                break
    out = {lab: None for lab in labels}
    for n, (i, lab, rest) in enumerate(marks):
        end = len(lines)
        for j in range(i + 1, len(lines)):
            if re.match(r"^#{1,6}\s", lines[j]) or any(m[0] == j for m in marks):
                end = j
                break
        if out[lab] is None:
            out[lab] = "\n".join([rest] + lines[i + 1:end]).strip()
    return out


def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", re.sub(r"[*_`]", "", text))
    return [p for p in (re.sub(r"^\s*(?:[-+]|\d+[.)])\s+", "", p).strip() for p in parts) if re.search(r"\w", p)]


def words(name):
    return [w for chunk in name.split("_") for w in re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?![a-z])", chunk)]


# ---- checks: each returns (passed, detail) -----------------------------------

def c_present(text, s):
    n = len(re.findall(s["pattern"], text))
    return n >= s.get("min", 1), f"{n} match(es), need >= {s.get('min', 1)}"


def c_absent(text, s):
    n = len(re.findall(s["pattern"], text))
    return n == 0, f"{n} match(es), need 0"


def c_blocks_exactly(text, s):
    chunks = blocks(text, s["start"])
    counts = [len(re.findall(s["pattern"], c)) for c in chunks]
    ok = bool(chunks) and all(n == s["exactly"] for n in counts)
    return ok, f"{len(chunks)} block(s), matches per block {counts}, need exactly {s['exactly']}"


def c_block_rule(text, s):
    chunks = blocks(text, s["start"])
    bad = [c for c in chunks if re.search(s["if_has"], c) and not re.search(s["unless_has"], c)]
    return bool(chunks) and not bad, f"{len(chunks)} block(s), {len(bad)} break the rule"


def c_names_min_words(text, s):
    names = re.findall(s["extract"], text)
    short = [n for n in names if len(words(n)) < s["min_words"]]
    return bool(names) and not short, f"{len(names)} name(s), too short: {short[:3]}"


def c_mermaid_type(text, s):
    bs = mermaid_blocks(text)
    types = [(re.match(r"\s*([\w-]+)", b) or [None, ""])[1] for b in bs]
    return any(t in s["allowed"] for t in types), f"types {types}, need at least one of {s['allowed']}"


def c_mermaid_labels(text, s):
    labels = []
    for b in mermaid_blocks(text):
        if re.match(r"\s*(flowchart|graph)\b", b):
            for m in re.findall(r"\[([^\]]*)\]|\{([^}]*)\}|\(\(?([^()]*)\)?\)", b):
                labels += [x.strip('"\' ') for x in m if x]
    longest = max((len(x) for x in labels), default=0)
    return bool(labels) and longest <= s["max"], f"{len(labels)} label(s), longest {longest}, max {s['max']}"


def c_sections_present(text, s):
    found = sections(text, s["labels"])
    missing = [k for k, v in found.items() if v is None]
    return not missing, f"missing: {missing}"


def c_section_sentences(text, s):
    body = sections(text, s["labels"]).get(s["section"])
    if body is None:
        return False, f"section {s['section']} not found"
    n = len(sentences(body))
    return s["min"] <= n <= s["max"], f"{n} sentence(s), need {s['min']}-{s['max']}"


def c_sections_total(text, s):
    found = sections(text, s["labels"])
    if any(v is None for v in found.values()):
        return False, "a section is missing"
    n = sum(len(sentences(v)) for v in found.values())
    return s["min"] <= n <= s["max"], f"{n} sentence(s) in total, need {s['min']}-{s['max']}"


CHECKS = {
    "present": c_present, "absent": c_absent, "blocks_exactly": c_blocks_exactly,
    "block_rule": c_block_rule, "names_min_words": c_names_min_words,
    "mermaid_type": c_mermaid_type, "mermaid_labels": c_mermaid_labels,
    "sections_present": c_sections_present, "section_sentences": c_section_sentences,
    "sections_total": c_sections_total,
}


# ---- cases and prompts -------------------------------------------------------

def load_case_file(path):
    data = json.loads(read(path))
    errors = []
    skill_path = ROOT / ".claude/skills" / data.get("agent", "?") / f"{data.get('skill', '?')}.md"
    if not skill_path.is_file():
        errors.append(f"{path.name}: skill file {skill_path.relative_to(ROOT)} not found")
    seen = set()
    for case in data.get("cases", []):
        cid = case.get("id", "?")
        if cid in seen:
            errors.append(f"{cid}: duplicate id")
        seen.add(cid)
        if not case.get("prompt") or not case.get("checks"):
            errors.append(f"{cid}: needs a prompt and at least one check")
        ids = set()
        for chk in case.get("checks", []):
            if chk.get("type") not in CHECKS:
                errors.append(f"{cid}: unknown check type '{chk.get('type')}'")
            if chk.get("id") in ids or not chk.get("id"):
                errors.append(f"{cid}: check ids must be present and unique")
            ids.add(chk.get("id"))
            for key in ("pattern", "start", "if_has", "unless_has", "extract"):
                if key in chk:
                    try:
                        re.compile(chk[key])
                    except re.error as e:
                        errors.append(f"{cid}/{chk['id']}: bad regex in {key}: {e}")
    return data, skill_path, errors


def system_prompt(agent, skill_text, skill_name):
    base = (f"You are the {agent} subagent of an SDLC kit. Answer the task in a single reply, "
            "writing the deliverable in full. Do not ask questions and do not use tools.")
    if skill_text is None:
        return base
    return f"{base}\n\nThe skill file `{skill_name}.md` applies to this task:\n\n{skill_text}"


def run_one(call, model, system, case, run):
    reply = call(model, system, f"Task: {case['prompt']}")
    results = {}
    for chk in case["checks"]:
        ok, detail = CHECKS[chk["type"]](reply, chk)
        results[chk["id"]] = {"ok": bool(ok), "detail": detail, "heuristic": bool(chk.get("heuristic"))}
    return {"run": run, "reply": reply, "checks": results, "ok": all(r["ok"] for r in results.values())}


# ---- reporting ---------------------------------------------------------------

def verdict(per_case):
    """per_case: {case_id: {"with": [bool], "without": [bool]}} -> (verdict, with_total, without_total)."""
    with_rate = {c: sum(v["with"]) / len(v["with"]) for c, v in per_case.items()}
    wo_rate = {c: sum(v["without"]) / len(v["without"]) for c, v in per_case.items()}
    if any(r < PASS_RATE for r in with_rate.values()):
        return "FAILS", sum(with_rate.values()), sum(wo_rate.values())
    if sum(with_rate.values()) > sum(wo_rate.values()):
        return "PASSES", sum(with_rate.values()), sum(wo_rate.values())
    return "NO EFFECT", sum(with_rate.values()), sum(wo_rate.values())


def report(skill, cases, runs_by_cond):
    print(f"\n== {skill}")
    per_case = {}
    for case in cases:
        w = [r["ok"] for r in runs_by_cond[(case["id"], "with")]]
        wo = [r["ok"] for r in runs_by_cond[(case["id"], "without")]]
        per_case[case["id"]] = {"with": w, "without": wo}
        print(f"  {case['id']:<10} with skill {sum(w)}/{len(w)}   without {sum(wo)}/{len(wo)}")
        for chk in case["checks"]:
            cw = sum(r["checks"][chk["id"]]["ok"] for r in runs_by_cond[(case["id"], "with")])
            cwo = sum(r["checks"][chk["id"]]["ok"] for r in runs_by_cond[(case["id"], "without")])
            tag = " (heuristic)" if chk.get("heuristic") else ""
            print(f"      {chk['id']:<28} with {cw}/{len(w)}  without {cwo}/{len(wo)}{tag}")
    v, tw, two = verdict(per_case)
    print(f"  verdict: {v}  (case pass rate with skill {tw:.1f}, without {two:.1f}, of {len(cases)})")
    return v


def estimate(jobs, runs, model_list, workers):
    calls = len(jobs) * runs
    in_tok = sum(len(system) + len(case["prompt"]) for _, case, system in jobs) / CHARS_PER_TOKEN * runs
    out_tok = calls * ASSUMED_OUTPUT_TOKENS
    secs = calls * (SECONDS_OVERHEAD + ASSUMED_OUTPUT_TOKENS / TOKENS_PER_SECOND)
    print(f"\nDry run: {len(jobs)} case-conditions x {runs} runs = {calls} calls")
    print(f"Estimated tokens: about {int(in_tok):,} input + {out_tok:,} output")
    print(f"Estimated time: about {secs / 60:.1f} min sequential, {secs / 60 / workers:.1f} min with {workers} workers")
    print("Estimated API cost (rough; assumes 600 output tokens per call):")
    for model in model_list:
        pin, pout = PRICES[model]
        print(f"  {model:<20} ${in_tok / 1e6 * pin + out_tok / 1e6 * pout:.3f}")
    print("With --backend cli there is no per-token charge; the calls count against your account usage.")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--skill", action="append", help="only this skill (repeatable); default all in tests/usage")
    ap.add_argument("--backend", choices=("cli", "api"), default="cli")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--runs", type=int, default=3, help="repetitions per case and condition")
    ap.add_argument("--workers", type=int, default=4, help="parallel calls")
    ap.add_argument("--case", action="append", help="only this case id (repeatable)")
    ap.add_argument("--strict", action="store_true",
                    help="exit 1 if a case that held in the recorded baseline no longer does")
    ap.add_argument("--write-baseline", action="store_true", help="record this run in tests/usage/baseline.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", help="write raw results as JSON to this file")
    args = ap.parse_args()

    files = sorted(USAGE_DIR.glob("*.json"))
    if args.skill:
        files = [f for f in files if f.stem in args.skill]
    if not files:
        print("No case files found.")
        return 1

    loaded, errors = [], []
    for f in files:
        data, skill_path, errs = load_case_file(f)
        errors += errs
        loaded.append((data, skill_path))
    for e in errors:
        print(f"CASES {e}")
    if errors:
        return 1

    jobs = []  # (skill, case, system) with the condition folded into the system prompt
    for data, skill_path in loaded:
        skill_text = read(skill_path)
        for case in data["cases"]:
            if args.case and case["id"] not in args.case:
                continue
            for cond, text in (("with", skill_text), ("without", None)):
                case_c = {**case, "_cond": cond, "_skill": data["skill"]}
                jobs.append((data["skill"], case_c, system_prompt(data["agent"], text, data["skill"])))

    if args.dry_run:
        print(f"Case files OK: {len(loaded)} skill(s), {len(jobs) // 2} case(s).")
        estimate(jobs, args.runs, list(PRICES), args.workers)
        return 0

    if args.backend == "cli":
        call = call_cli
    else:
        def call(model, system, task):
            return call_api(model, system, task, MAX_TOKENS)

    work = [(skill, case, system, run) for skill, case, system in jobs for run in range(args.runs)]
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        done = list(pool.map(lambda w: (w, run_one(call, args.model, w[2], w[1], w[3])), work))

    by_skill = defaultdict(lambda: defaultdict(list))
    for (skill, case, _, _), result in done:
        by_skill[skill][(case["id"], case["_cond"])].append(result)

    verdicts = {}
    for data, _ in loaded:
        cases = [c for c in data["cases"] if not args.case or c["id"] in args.case]
        verdicts[data["skill"]] = report(data["skill"], cases, by_skill[data["skill"]])
    print("\nChecks marked heuristic can be wrong in both directions; read them as signals.")

    if args.out:
        raw = [{"skill": s, "case": c["id"], "condition": c["_cond"], **r} for (s, c, _, _), r in done]
        Path(args.out).write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    exit_code = 0
    for data, _ in loaded:
        skill = data["skill"]
        rates = {c["id"]: sum(r["ok"] for r in by_skill[skill][(c["id"], "with")]) / len(by_skill[skill][(c["id"], "with")])
                 for c in data["cases"] if not args.case or c["id"] in args.case}
        if args.write_baseline:
            if args.case:
                print("\n--write-baseline needs the full case set; drop --case.")
                return 1
            write_baseline(BASELINE, skill, rates, {"model": args.model, "runs": args.runs, "verdict": verdicts[skill]})
        if args.strict:
            lost = regressions(BASELINE, skill, rates)
            exit_code |= 1 if lost is None or lost else 0
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
