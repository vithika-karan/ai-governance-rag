import pymupdf


PDF_PATH = "data/raw/eu_ai_act_2026-07-27.pdf"

doc = pymupdf.open(PDF_PATH)

print(f"Pages: {len(doc)}")

for page_number in range(min(5, len(doc))):
    page = doc[page_number]
    text = page.get_text()

    print("\n" + "=" * 80)
    print(f"PAGE {page_number + 1}")
    print("=" * 80)
    print(text[:4000])

doc.close()
