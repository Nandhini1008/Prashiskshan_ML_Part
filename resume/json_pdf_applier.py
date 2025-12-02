"""
JSON-Based PDF Enhancement Applier

This module applies LLM-generated enhancements (in JSON format) to PDFs
using exact pixel positioning.

Author: Prashiskshan Backend Team
"""

import fitz  # PyMuPDF
import os
from typing import Dict, Any, List
from difflib import SequenceMatcher


class JSONPDFApplier:
    """Apply JSON enhancements to PDF."""
    
    def __init__(self):
        """Initialize the applier."""
        pass
    
    def apply_enhancements(
        self,
        original_pdf_path: str,
        enhancements: List[Dict[str, str]],
        output_pdf_path: str = None
    ) -> Dict[str, Any]:
        """
        Apply JSON enhancements to PDF.
        
        Args:
            original_pdf_path: Path to original PDF
            enhancements: List of enhancement dicts with 'original' and 'enhanced'
            output_pdf_path: Path to save enhanced PDF
            
        Returns:
            Results dictionary
        """
        try:
            print(f"📋 Applying {len(enhancements)} enhancements to PDF...")
            
            # Determine output path
            if not output_pdf_path:
                base_name = os.path.splitext(original_pdf_path)[0]
                output_pdf_path = f"{base_name}_Enhanced.pdf"
            
            # Open PDF
            doc = fitz.open(original_pdf_path)
            
            # Extract text blocks with positions
            text_blocks = self._extract_text_blocks(doc)
            print(f"✓ Mapped {len(text_blocks)} text blocks")
            
            # Apply each enhancement
            replacements_made = 0
            
            for enh in enhancements:
                original = enh.get('original', '').strip()
                enhanced = enh.get('enhanced', '').strip()
                
                if not original or not enhanced:
                    continue
                
                # Find matching blocks
                matches = self._find_text_in_pdf(text_blocks, original)
                
                for match in matches:
                    page = doc[match['page']]
                    bbox = match['bbox']
                    
                    # Remove old text
                    page.add_redact_annot(bbox, text="")
                    page.apply_redactions()
                    
                    # Insert enhanced text
                    try:
                        rc = page.insert_textbox(
                            bbox,
                            enhanced,
                            fontsize=match.get('size', 11),
                            align=fitz.TEXT_ALIGN_LEFT
                        )
                        
                        if rc >= 0:
                            replacements_made += 1
                            print(f"  ✓ Applied: {original[:50]}...")
                    except Exception as e:
                        print(f"  ⚠ Skipped: {str(e)[:50]}")
            
            print(f"✓ Applied {replacements_made} enhancements")
            
            # Save PDF
            doc.save(output_pdf_path, garbage=4, deflate=True)
            doc.close()
            
            return {
                'success': True,
                'output_pdf_path': output_pdf_path,
                'replacements_made': replacements_made,
                'message': f'Successfully applied {replacements_made} enhancements'
            }
            
        except Exception as e:
            import traceback
            print(f"❌ Error: {str(e)}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'output_pdf_path': None
            }
    
    def _extract_text_blocks(self, doc: fitz.Document) -> List[Dict]:
        """Extract text blocks with positions."""
        all_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block.get("type") == 0:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text:
                                all_blocks.append({
                                    'page': page_num,
                                    'text': text,
                                    'bbox': fitz.Rect(span["bbox"]),
                                    'size': span.get("size", 11)
                                })
        
        return all_blocks
    
    def _find_text_in_pdf(
        self,
        text_blocks: List[Dict],
        search_text: str
    ) -> List[Dict]:
        """Find text blocks matching search text."""
        matches = []
        
        # Try exact match
        for block in text_blocks:
            if search_text in block['text'] or block['text'] in search_text:
                matches.append(block)
        
        # Try fuzzy match if no exact match
        if not matches:
            for block in text_blocks:
                similarity = SequenceMatcher(None, block['text'], search_text).ratio()
                if similarity > 0.7:
                    matches.append(block)
        
        return matches


def apply_enhancements_to_pdf(
    pdf_path: str,
    enhancements: List[Dict[str, str]],
    output_path: str = None
) -> Dict[str, Any]:
    """Convenience function to apply enhancements."""
    applier = JSONPDFApplier()
    return applier.apply_enhancements(pdf_path, enhancements, output_path)


if __name__ == "__main__":
    print("JSON-Based PDF Enhancement Applier")
