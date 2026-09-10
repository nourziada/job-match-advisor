import sys
sys.stdout.reconfigure(encoding="utf-8")

from eval.dataset_loader import load_all_datasets
from eval.evaluator import run_eval
from eval.report import render_report


def main():
    # بيدمج حالاتك اليدوية (dataset.json) مع المولّدة (dataset_generated.json)
    dataset = load_all_datasets()
    results = run_eval(dataset)
    with open("eval_report.html", "w", encoding="utf-8") as f:
        f.write(render_report(results))
    print("تم إنشاء eval_report.html — افتحه في المتصفح")


if __name__ == "__main__":
    main()