from ocr_pdf_pipeline import process_pdf
from datetime import datetime
import os

PDF_PATH = r'D:\sih_project\Prashiskshan_backend\resume\OCR\AMAANUDEEN.pdf'
OUTPUT_FILE = 'ocr_output.txt'

res = process_pdf(PDF_PATH, use_ocr=True)

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    f.write('PDF Text Detection Results\n')
    f.write('='*60 + '\n')
    f.write(f"File: {res.get('file_path', PDF_PATH)}\n")
    f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Total Pages: {res.get('total_pages', 0)}\n")
    f.write('='*60 + '\n\n')

    for page in res.get('pages', []):
        f.write(f"PAGE {page.get('page_number')}\n")
        if 'text' in page:
            f.write('Extracted Text:\n')
            f.write(page.get('text','') + '\n')
        else:
            dets = page.get('detections', [])
            f.write(f"Detected Text Regions: {len(dets)}\n")
            f.write('-'*60 + '\n')
            for d in dets:
                f.write(f"[{d.get('reading_order')}] {d.get('text')} (conf: {d.get('confidence'):.2f})\n")
            f.write('\n')

print(f"Saved results to {os.path.abspath(OUTPUT_FILE)}")
