"""Render every page of the browser-generated report PDF and record inspectable metadata."""

from pathlib import Path
import json
import re

import pymupdf

ROOT = Path(__file__).resolve().parents[1]


def main():
    folder = ROOT / "evidence/browser/verified"
    document = pymupdf.open(folder / "print-report.pdf")
    for old in folder.glob('print-report-final-page-*.png'):
        number=re.fullmatch(r'print-report-final-page-(\d+)\.png',old.name)
        if number and int(number.group(1))>len(document) and old.resolve().is_relative_to(ROOT.resolve()):old.unlink()
    match = re.search(r"PLAN-[A-Z0-9-]+", document[0].get_text())
    plan_id = match.group(0) if match else None
    records = []
    for index, page in enumerate(document):
        file = folder / f"print-report-final-page-{index+1}.png"
        page.get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3), alpha=False).save(file)
        content = page.get_text()
        records.append(
            {
                "page": index + 1,
                "text_characters": len(content),
                "plan_id_present": bool(plan_id and plan_id in content),
                "image": str(file.relative_to(ROOT)).replace("\\", "/"),
            }
        )
    report = {
        "plan_id": plan_id,
        "page_count": len(document),
        "pages": records,
        "scope": "Rasterized for manual visual inspection; text metrics alone are not layout approval.",
    }
    (ROOT / "evidence/browser/print-report-qa.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
