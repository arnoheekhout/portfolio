"""
Render PDFs at multiple DPI/quality settings for visual comparison.
Creates images_compare/{label}/{stem}/ with AVIF pages and a manifest.json
so each variant can be loaded directly in the viewer.

Requirements:
    pip install pdf2image Pillow
    Poppler must be installed and on PATH
"""

import os
import json
from pdf2image import convert_from_path, pdfinfo_from_path

# ADD THE PDFs YOU WANT TO CONVERT HERE:
PDFS = {
    "MilenaMarcowka_Portfolio":   "Portfolio",
    "MilenaMarcowka_CV":          "CV",
    "MilenaMarcowka_Masterproef": "Masterproef",
}

# ADD THE SETTINGS YOU WANT TO TEST HERE: (DPI, QUALITY, NAME)
# quality=-1 means lossless
SETTINGS = [
    # (200, 85,  "200_q85"),
    # (200, 90,  "200_q90"),
    # (200, 92,  "200_q92"),
    (200, -1,  "200_lossless"),
    # (250, 85,  "250_q85"),
    # (250, 90,  "250_q90"),
    # (250, 92,  "250_q92"),
    (250, -1,  "250_lossless"),
    # (300, 85,  "300_q85"),
    # (300, 90,  "300_q90"),
    # (300, 92,  "300_q92"),
    (300, -1,  "300_lossless"),
    # (350, 85,  "350_q85"),
    # (350, 90,  "350_q90"),
    # (350, 92,  "350_q92"),
    (350, -1,  "350_lossless"),
    # (400, 85,  "400_q85"),
    # (400, 90,  "400_q90"),
    # (400, 92,  "400_q92"),
    (400, -1,  "400_lossless"),
    # (450, 85,  "450_q85"),
    # (450, 90,  "450_q90"),
    # (450, 92,  "450_q92"),
    (450, -1,  "450_lossless"),
]

def dir_size_kb(path):
    total = 0
    for f in os.listdir(path):
        fp = os.path.join(path, f)
        if os.path.isfile(fp) and f.endswith(".avif"):
            total += os.path.getsize(fp)
    return total // 1024

def convert_setting(dpi, quality, label):
    sizes = {}
    for stem, title in PDFS.items():
        pdf_path = os.path.join("pdfs", f"{stem}.pdf")
        out_dir  = os.path.join("images_compare", label, stem)
        os.makedirs(out_dir, exist_ok=True)

        info  = pdfinfo_from_path(pdf_path)
        total = info["Pages"]

        print(f"  [{title}] {total} pages...", end="", flush=True)

        manifest = {"title": title, "pageCount": total, "pages": []}

        for i in range(1, total + 1):
            filename = f"page_{i:03d}.avif"
            out_path = os.path.join(out_dir, filename)

            if os.path.exists(out_path):
                from PIL import Image
                with Image.open(out_path) as img:
                    w, h = img.size
            else:
                pages = convert_from_path(pdf_path, dpi=dpi, first_page=i, last_page=i, fmt="ppm")
                page  = pages[0]
                w, h  = page.size
                if quality == -1:
                    page.save(out_path, "AVIF", lossless=True, speed=2)
                else:
                    page.save(out_path, "AVIF", quality=quality, speed=2)
                print(".", end="", flush=True)

            manifest["pages"].append({"file": filename, "width": w, "height": h})

        with open(os.path.join(out_dir, "manifest.json"), "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        kb = dir_size_kb(out_dir)
        sizes[stem] = kb
        print(f" {kb:,} KB")

    return sizes

# ── Check baseline (current images/) ────────────────────────────────────────
print("Reading baseline (current images/)...")
baseline = {}
for stem in PDFS:
    d = os.path.join("images", stem)
    baseline[stem] = dir_size_kb(d) if os.path.isdir(d) else 0

# ── Run all settings ─────────────────────────────────────────────────────────
results = {"baseline": baseline}

for dpi, quality, label in SETTINGS:
    q_label = "lossless" if quality == -1 else f"q{quality}"
    print(f"\n[{dpi} DPI, {q_label}]")
    results[label] = convert_setting(dpi, quality, label)

# ── Print table ──────────────────────────────────────────────────────────────
stems  = list(PDFS.keys())
titles = list(PDFS.values())

col_w = 14
hdr   = f"{'Setting':<22}" + "".join(f"{t:>{col_w}}" for t in titles) + f"{'Total':>{col_w}}"
sep   = "-" * len(hdr)

print(f"\n\n{'=' * len(hdr)}")
print("RESULTS (sizes in KB)")
print(f"{'=' * len(hdr)}")
print(hdr)
print(sep)

all_rows = [("baseline", "baseline (current)")] + [
    (label, label.replace("_", " ")) for _, _, label in SETTINGS
]

for key, display in all_rows:
    row_data = results.get(key, {})
    total    = sum(row_data.get(s, 0) for s in stems)
    row      = f"{display:<22}" + "".join(f"{row_data.get(s, 0):>{col_w},}" for s in stems) + f"{total:>{col_w},}"
    print(row)

print(f"{'=' * len(hdr)}\n")
print("Files saved in images_compare/ — load via the viewer to compare.")
