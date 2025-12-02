"""
Simple PDF Text Replacer - Pixel-Perfect Enhancement

This module creates an enhanced PDF by overlaying enhanced text
on the original PDF while preserving exact layout.

Author: Prashiskshan Backend Team
"""

import fitz  # PyMuPDF
import os
from typing import Dict, Any, List


class SimplePDFReplacer:
    """Simple PDF text replacement while preserving layout."""
    
    def __init__(self):
        """Initialize the PDF replacer."""
        pass
    
    def replace_text_in_pdf(
        self,
        original_pdf_path: str,
        final_text_path: str,
        output_pdf_path: str = None
    ) -> Dict[str, Any]:
        """
        Create enhanced PDF by replacing text.
        
        Strategy:
        1. Copy original PDF
        2. Extract text blocks with positions
        3. Redact old text
        4. Insert enhanced text at same positions
        
        Args:
            original_pdf_path: Path to original PDF
            final_text_path: Path to final enhanced text
            output_pdf_path: Path to save enhanced PDF
            
        Returns:
            Results dictionary
        """
        try:
            # Read final text
            print("📖 Reading enhanced text...")
            with open(final_text_path, 'r', encoding='utf-8') as f:
                final_text = f.read()
            
            final_lines = [line for line in final_text.split('\n') if line.strip()]
            
            # Determine output path
            if not output_pdf_path:
                base_name = os.path.splitext(original_pdf_path)[0]
                output_pdf_path = f"{base_name}_Enhanced.pdf"
            
            # Open original PDF
            print("📄 Opening original PDF...")
            doc = fitz.open(original_pdf_path)
            
            # Extract all text with positions
            print("🔍 Extracting text positions...")
            all_text_blocks = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                blocks = page.get_text("dict")["blocks"]
                
                for block in blocks:
                    if block.get("type") == 0:  # Text block
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                text = span.get("text", "").strip()
                                if text:
                                    all_text_blocks.append({
                                        'page': page_num,
                                        'text': text,
                                        'bbox': span["bbox"],
                                        'font': span.get("font", "helv"),
                                        'size': span.get("size", 11),
                                        'color': span.get("color", 0)
                                    })
            
            print(f"✓ Found {len(all_text_blocks)} text blocks")
            print(f"✓ Have {len(final_lines)} enhanced lines")
            
            # Match and replace text
            print("🔄 Replacing text...")
            replacements_made = 0
            
            # Group blocks by page for better processing
            pages_blocks = {}
            for block in all_text_blocks:
                page_num = block['page']
                if page_num not in pages_blocks:
                    pages_blocks[page_num] = []
                pages_blocks[page_num].append(block)
            
            # Process each page
            final_line_idx = 0
            for page_num in sorted(pages_blocks.keys()):
                page = doc[page_num]
                page_blocks = pages_blocks[page_num]
                
                # First pass: redact all old text
                for block in page_blocks:
                    page.add_redact_annot(block['bbox'], text="")
                
                # Apply redactions
                page.apply_redactions()
                
                # Second pass: insert new text
                for block in page_blocks:
                    if final_line_idx < len(final_lines):
                        enhanced_text = final_lines[final_line_idx]
                        final_line_idx += 1
                        
                        # Calculate better vertical position (baseline)
                        bbox = block['bbox']
                        x = bbox[0]
                        y = bbox[3] - 3  # Slight adjustment for baseline
                        
                        try:
                            # Try with original font
                            page.insert_text(
                                (x, y),
                                enhanced_text,
                                fontname=block['font'],
                                fontsize=block['size'],
                                color=self._int_to_rgb(block['color'])
                            )
                            replacements_made += 1
                        except:
                            try:
                                # Fallback to default font
                                page.insert_text(
                                    (x, y),
                                    enhanced_text,
                                    fontsize=block['size'],
                                    color=self._int_to_rgb(block['color'])
                                )
                                replacements_made += 1
                            except Exception as e:
                                print(f"  ⚠ Skipped one block: {str(e)[:50]}")
            
            print(f"✓ Made {replacements_made} text replacements")
            
            # Save enhanced PDF
            print(f"💾 Saving enhanced PDF...")
            doc.save(output_pdf_path, garbage=4, deflate=True)
            doc.close()
            
            print(f"✅ Enhanced PDF created: {output_pdf_path}")
            
            return {
                'success': True,
                'output_pdf_path': output_pdf_path,
                'replacements_made': replacements_made,
                'message': f'Successfully created enhanced PDF with {replacements_made} improvements'
            }
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Error: {str(e)}")
            print(error_details)
            return {
                'success': False,
                'error': str(e),
                'error_details': error_details,
                'output_pdf_path': None
            }
    
    def _int_to_rgb(self, color_int: int) -> tuple:
        """Convert integer color to RGB tuple (0-1 range)."""
        if color_int == 0:
            return (0, 0, 0)  # Black
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return (r, g, b)


def create_enhanced_pdf(
    original_pdf: str,
    final_text: str,
    output_pdf: str = None
) -> Dict[str, Any]:
    """
    Convenience function to create enhanced PDF.
    
    Args:
        original_pdf: Path to original PDF
        final_text: Path to final enhanced text file
        output_pdf: Path to save enhanced PDF
        
    Returns:
        Results dictionary
    """
    replacer = SimplePDFReplacer()
    return replacer.replace_text_in_pdf(original_pdf, final_text, output_pdf)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Simple PDF Text Replacer")
        print("\nUsage:")
        print("  python simple_pdf_replacer.py <original_pdf> <final_text>")
        print("\nExample:")
        print("  python simple_pdf_replacer.py resume.pdf resume_Final.txt")
    else:
        original = sys.argv[1]
        final = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = create_enhanced_pdf(original, final, output)
        
        if result['success']:
            print(f"\n✓ {result['message']}")
            print(f"📄 Output: {result['output_pdf_path']}")
        else:
            print(f"\n✗ Failed: {result['error']}")
