import os
import sys
sys.stdout.reconfigure(encoding="utf-8")

from config import BASE_DIR
from eval.dataset_loader import load_all_datasets
from eval.evaluator import run_eval
from eval.report import render_report

# Resolved from the project root, like the other evaluation paths.
REPORT_PATH = os.path.join(BASE_DIR, "eval_report.html")


def main():
    dataset = load_all_datasets()
    results = run_eval(dataset)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(render_report(results))
    print(f"Wrote {REPORT_PATH} - open it in a browser")


if __name__ == "__main__":
    main()