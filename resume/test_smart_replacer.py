"""
Test Smart PDF Replacer

This script demonstrates the smart differential PDF replacement.
"""

import os

# File paths
original_pdf = "nandhini_resume_.pdf"
original_txt = "nandhini_resume__Original.txt"  # Will be created if doesn't exist
enhanced_txt = "nandhini_resume__Final.txt"
output_pdf = "nandhini_resume__Smart_Enhanced.pdf"

# Check if files exist
if not os.path.exists(original_pdf):
    print(f"❌ Original PDF not found: {original_pdf}")
    exit(1)

if not os.path.exists(enhanced_txt):
    print(f"❌ Enhanced text not found: {enhanced_txt}")
    print("   Run: python process_resume.py nandhini_resume_.pdf")
    exit(1)

# Create original text if it doesn't exist
if not os.path.exists(original_txt):
    print(f"📝 Creating original text file...")
    from OCR.ocr_pdf_pipeline import PDFTextExtractor
    extractor = PDFTextExtractor()
    result = extractor.extract_text_from_pdf(original_pdf, use_ocr=False)
    
    if 'pages' in result:
        text_parts = []
        for page in result['pages']:
            if 'text' in page:
                text_parts.append(page['text'])
        
        original_text = '\n'.join(text_parts)
        with open(original_txt, 'w', encoding='utf-8') as f:
            f.write(original_text)
        print(f"✓ Created: {original_txt}")

# Run smart differential replacement
print("\n" + "="*60)
print("🎯 SMART DIFFERENTIAL PDF ENHANCEMENT")
print("="*60 + "\n")

from smart_pdf_replacer import create_smart_enhanced_pdf

result = create_smart_enhanced_pdf(
    original_pdf,
    original_txt,
    enhanced_txt,
    output_pdf
)

if result['success']:
    print("\n" + "="*60)
    print("✅ SUCCESS!")
    print("="*60)
    print(f"\n📄 Enhanced PDF: {result['output_pdf_path']}")
    print(f"📊 Changes identified: {result['changes_identified']}")
    print(f"✂️ Surgical replacements: {result['replacements_made']}")
    print(f"\n💡 Only the changed text was replaced!")
    print(f"   Everything else in the PDF remains pixel-perfect!")
else:
    print("\n" + "="*60)
    print("❌ FAILED")
    print("="*60)
    print(f"\nError: {result['error']}")
