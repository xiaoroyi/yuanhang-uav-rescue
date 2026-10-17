"""Rasterize the actual exported deck PDF; geometry/text checks precede visual review."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]


def main():
    pdf = ROOT / "deliverables/yuanhang-demo.pdf"
    manifest = json.loads(
        (ROOT / "evidence/demo/manifest.json").read_text(encoding="utf-8")
    )
    folder = ROOT / "evidence/demo/pdf"
    folder.mkdir(parents=True, exist_ok=True)
    pages = []
    with pymupdf.open(pdf) as document:
        if len(document) != manifest["slide_count"]:
            raise ValueError("PDF page count differs from the authored slide count.")
        for index, page in enumerate(document):
            if abs(page.rect.width - 960) > 0.1 or abs(page.rect.height - 540) > 0.1:
                raise ValueError("Unexpected PDF page geometry.")
            text = "".join(page.get_text().split())
            title = manifest["slides"][index]["title"]
            if "".join(title.split()) not in text:
                raise ValueError(f"Missing native title on PDF page {index+1}.")
            output = folder / f"page-{index+1:02}.png"
            page.get_pixmap(matrix=pymupdf.Matrix(1.25, 1.25), alpha=False).save(output)
            pages.append(
                dict(
                    page=index + 1,
                    title=title,
                    native_text_characters=len(text),
                    image=str(output.relative_to(ROOT)).replace("\\", "/"),
                )
            )
    report = dict(
        rendered_at_utc=datetime.now(timezone.utc).isoformat(),
        pdf_sha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
        page_count=len(pages),
        pages=pages,
        visual_review="pending; raster images must be inspected individually",
    )
    (ROOT / "evidence/demo/pdf-qa.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {"pages": len(pages), "geometry": "960 x 540 pt", "titles_present": True}
        )
    )


if __name__ == "__main__":
    main()
