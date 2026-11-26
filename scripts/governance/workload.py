"""Compute unassigned weekly roadmap estimates; allocation follows accepted rotation, not fixed roles."""
import argparse
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def report(plan):
    """Task scheduling totals are NOT personal assignments or actual hours."""
    start = date(2026, 10, 21)
    cutoff = min(date(2026, 12, 27), date.fromisoformat(plan["deadline"]) - timedelta(days=1))
    lines = ["# Weekly unassigned roadmap effort / Haftalık atanmamış iş yükü", "",
             "Estimates below are task-window distributions, not commitments or permanent member allocation.",
             "Only one implementation owner is authorized at a time in the Genesis rotation.",
             "Actual effort, PR reviews and blocked dependencies must be reviewed at every handoff.", "",
             "| Week | Estimated work-package effort (person-hours) | Open task IDs in window |",
             "|---|---:|---|"]
    while start <= cutoff:
        end = min(start + timedelta(days=6 - start.weekday()), cutoff)
        value = 0.0
        active = []
        for task in plan["tasks"]:
            first, last = date.fromisoformat(task["start"]), date.fromisoformat(task["target"])
            overlap = max(0, (min(end, last) - max(start, first)).days + 1)
            if not overlap:
                continue
            days = (last - first).days + 1
            value += task["estimated_effort"] * overlap / days
            active.append(task["plan_id"])
        lines.append(f"| {start} – {end} | {value:.1f} | {', '.join(active) or 'None'} |")
        start = end + timedelta(days=1)
    lines.extend(["", "## Decision and limitations", "",
      "- The original 70/30 owner/support split and reviewer allocations are historical and not a workload forecast under sequential ownership.",
      "- All 31 technical tasks and six work packages remain in the registry.",
      "- Prerequisite completion, verification, handoff publication and available people constrain real scheduling.",
      "- Owner-approved P0 now includes the local Qwen3-Coder security LLM and Python/JS/TS. Do not defer mandatory items silently.",
      "- The 2027-01-01 due date is a target; this table does not imply that the work fits available capacity.",
      "- Update task windows only after evidence-based replanning and owner acceptance where consequential.",
      ""])
    return "\n".join(lines)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--output")
    args = p.parse_args()
    plan = json.loads((ROOT / ".github/task-plan.json").read_text(encoding="utf-8"))
    result = report(plan)
    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
    else:
        print(result)
