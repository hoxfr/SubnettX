import fitz
import sys

pdf_path = sys.argv[1]
doc = fitz.open(pdf_path)

for page_idx in [2, 7]:
    page = doc[page_idx]
    
    # Print all text blocks
    print(f"--- PAGE {page_idx+1} TEXT BLOCKS ---")
    blocks = page.get_text("blocks")
    for b in blocks:
        print(f"Rect: {b[:4]}, Text: {b[4].strip()}")
        
    print(f"--- PAGE {page_idx+1} IMAGES ---")
    images = page.get_images()
    for img in images:
        print(img)
