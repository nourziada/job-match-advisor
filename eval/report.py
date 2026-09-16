from html import escape


def _score_color(s: int) -> str:
    if s >= 8: return "#16a34a"
    if s >= 5: return "#d97706"
    return "#dc2626"


def render_report(results: list) -> str:
    total = len(results)
    avg = sum(r["score"] for r in results) / total if total else 0
    passed = sum(1 for r in results if r["score"] >= 7)
    rate = (passed / total * 100) if total else 0

    rows = ""
    for r in results:
        strengths = "".join(f"<li>{escape(s)}</li>" for s in r["strengths"]) or "<li>-</li>"
        weaknesses = "".join(f"<li>{escape(w)}</li>" for w in r["weaknesses"]) or "<li>-</li>"
        color = _score_color(r["score"])
        source = r.get("source", "-")

        # The criteria the grader scored against - without them the score is
        # impossible to interpret.
        criteria = "".join(
            f"<li>{escape(c)}</li>" for c in r.get("solution_criteria", [])
        ) or "<li>-</li>"

        rows += f'''
        <tr>
          <td>{escape(r["scenario"])}</td>
          <td><span class="src">{escape(source)}</span></td>
          <td><span class="score" style="background:{color}">{r["score"]}/10</span></td>
          <td><ul>{strengths}</ul></td>
          <td><ul>{weaknesses}</ul></td>
          <td>{escape(r["reasoning"])}</td>
        </tr>
        <tr class="detail">
          <td colspan="6">
            <details>
              <summary>&#129489;&#8205;&#128187; CV used for this case</summary>
              <pre>{escape(r.get("cv", "-"))}</pre>
            </details>
            <details>
              <summary>&#128196; Job posting (prompt input)</summary>
              <pre>{escape(r.get("job_posting", "-"))}</pre>
            </details>
            <details>
              <summary>&#129302; Tool output (from analyze_job)</summary>
              <pre>{escape(r.get("output", "-"))}</pre>
            </details>
            <details>
              <summary>&#128208; Solution criteria</summary>
              <ul class="crit">{criteria}</ul>
            </details>
          </td>
        </tr>'''

    return f'''<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><title>Evaluation Report</title>
<style>
  body {{ font-family: system-ui, sans-serif; background:#f8fafc; padding:32px; }}
  .cards {{ display:flex; gap:16px; margin-bottom:24px; }}
  .card {{ background:#fff; border:1px solid #e2e8f0; border-radius:12px;
          padding:20px; flex:1; }}
  .label {{ font-size:13px; color:#64748b; }}
  .value {{ font-size:32px; font-weight:700; }}
  table {{ width:100%; border-collapse:collapse; background:#fff;
          border:1px solid #e2e8f0; border-radius:12px; overflow:hidden; }}
  th {{ background:#f1f5f9; padding:12px; text-align:left; font-size:13px; }}
  td {{ padding:14px; border-top:1px solid #e2e8f0; font-size:14px; vertical-align:top; }}
  .score {{ color:#fff; padding:4px 10px; border-radius:999px; font-weight:700; }}
  .src {{ background:#e2e8f0; color:#334155; padding:3px 9px; border-radius:999px;
         font-size:12px; white-space:nowrap; }}
  ul {{ margin:0; padding-inline-start:18px; }}

  tr.detail td {{ background:#f8fafc; padding:8px 14px 14px; border-top:none; }}
  details {{ margin-top:6px; border:1px solid #e2e8f0; border-radius:8px;
            background:#fff; }}
  summary {{ cursor:pointer; padding:9px 12px; font-size:13px; font-weight:600;
            color:#334155; user-select:none; }}
  summary:hover {{ background:#f1f5f9; }}
  details[open] summary {{ border-bottom:1px solid #e2e8f0; }}
  details pre {{ margin:0; padding:12px; max-height:340px; overflow:auto;
                white-space:pre-wrap; word-break:break-word;
                font-family:ui-monospace, Consolas, monospace; font-size:12.5px;
                line-height:1.55; color:#1e293b; }}
  ul.crit {{ margin:0; padding:12px 30px; font-size:13px; line-height:1.9; }}
</style></head>
<body>
  <h1>&#128202; Evaluation Report</h1>
  <div class="cards">
    <div class="card"><div class="label">Total Test Cases</div>
      <div class="value">{total}</div></div>
    <div class="card"><div class="label">Average Score</div>
      <div class="value">{avg:.1f}/10</div></div>
    <div class="card"><div class="label">Pass Rate (&#8805;7)</div>
      <div class="value">{rate:.0f}%</div></div>
  </div>
  <table>
    <thead><tr><th>Scenario</th><th>Source</th><th>Score</th><th>Strengths</th>
      <th>Weaknesses</th><th>Reasoning</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</body></html>'''
