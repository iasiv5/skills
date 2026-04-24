#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "scripts" / "yao.py"


def run(*args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    payload = json.loads(proc.stdout)
    return {
        "ok": proc.returncode == 0,
        "returncode": proc.returncode,
        "payload": payload,
        "stderr": proc.stderr,
    }


def main() -> None:
    tmp_root = ROOT / "tests" / "tmp_skill_overview"
    if tmp_root.exists():
        subprocess.run(["rm", "-rf", str(tmp_root)], check=True)
    tmp_root.mkdir(parents=True, exist_ok=True)

    init_result = run(
        "init",
        "skill-overview-demo",
        "--description",
        "Turn rough requests into a compact reusable demo skill.",
        "--output-dir",
        str(tmp_root),
    )
    assert init_result["ok"], init_result

    created = tmp_root / "skill-overview-demo"
    assert (created / "README.md").exists(), created
    assert (created / "manifest.json").exists(), created
    assert (created / "reports" / "intent-dialogue.md").exists(), created
    assert (created / "reports" / "intent-dialogue.json").exists(), created
    assert (created / "reports" / "intent-confidence.md").exists(), created
    assert (created / "reports" / "intent-confidence.json").exists(), created
    assert (created / "reports" / "skill-overview.html").exists(), created
    assert (created / "reports" / "skill-overview.json").exists(), created
    assert (created / "reports" / "reference-synthesis.md").exists(), created
    assert (created / "reports" / "reference-synthesis.json").exists(), created
    assert (created / "reports" / "iteration-directions.md").exists(), created
    assert (created / "reports" / "iteration-directions.json").exists(), created

    rerender_result = run("skill-report", str(created))
    assert rerender_result["ok"], rerender_result
    assert rerender_result["payload"]["artifacts"]["html"].endswith("reports/skill-overview.html"), rerender_result

    report_html = (created / "reports" / "skill-overview.html").read_text(encoding="utf-8")
    assert "Skill Overview" in report_html, report_html[:200]
    assert "Architecture" in report_html, report_html[:400]
    assert "Why It Works" in report_html, report_html[:600]
    assert "How to introduce this skill" in report_html, report_html[:900]
    assert "Patterns worth borrowing now" in report_html, report_html[:1200]
    assert "Reference synthesis" in report_html, report_html[:1500]

    intent_text = (created / "reports" / "intent-dialogue.md").read_text(encoding="utf-8")
    assert "Questions To Ask" in intent_text, intent_text[:400]

    directions_text = (created / "reports" / "iteration-directions.md").read_text(encoding="utf-8")
    assert "Top 3 Next Moves" in directions_text, directions_text[:400]

    print(json.dumps({"ok": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
