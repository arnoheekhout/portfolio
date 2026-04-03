"""
Convert PDF pages to WebP images for the portfolio viewer.

Requirements:
    pip install pdf2image Pillow
    Poppler must be installed and on PATH (Windows: https://github.com/oschwartz10612/poppler-windows)

Output:
    images/{DocName}/page_001.webp
    images/{DocName}/page_002.webp
    ...
    images/{DocName}/manifest.json
"""

import os
import json
from pdf2image import convert_from_path, pdfinfo_from_path

DPI = 300
WEBP_QUALITY = 92

DOCS = {
    "MilenaMarcowka_Portfolio":   "Portfolio",
    "MilenaMarcowka_CV":          "Curriculum Vitae",
    "MilenaMarcowka_Masterproef": "Masterproef",
}

def convert_doc(stem, title):
    pdf_path = os.path.join("pdfs", f"{stem}.pdf")
    out_dir  = os.path.join("images", stem)
    os.makedirs(out_dir, exist_ok=True)

    print(f"\n[{title}] Reading PDF info...")
    info = pdfinfo_from_path(pdf_path)
    total = info["Pages"]
    print(f"[{title}] {total} pages — converting at {DPI} DPI, WebP quality {WEBP_QUALITY}")

    manifest = {"title": title, "pageCount": total, "pages": []}

    for i in range(1, total + 1):
        print(f"  Page {i}/{total}...", end="\r", flush=True)
        pages = convert_from_path(pdf_path, dpi=DPI, first_page=i, last_page=i, fmt="ppm")
        page  = pages[0]

        filename = f"page_{i:03d}.webp"
        out_path = os.path.join(out_dir, filename)
        page.save(out_path, "WEBP", quality=WEBP_QUALITY, method=6)

        manifest["pages"].append({
            "file":   filename,
            "width":  page.width,
            "height": page.height,
        })

    manifest_path = os.path.join(out_dir, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    total_kb = sum(
        os.path.getsize(os.path.join(out_dir, p["file"])) for p in manifest["pages"]
    ) // 1024
    print(f"  Done — {total} pages, {total_kb} KB total ({out_dir})")

if __name__ == "__main__":
    for stem, title in DOCS.items():
        convert_doc(stem, title)
    print("\nAll conversions complete.")
