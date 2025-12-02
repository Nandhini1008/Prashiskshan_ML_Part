"""
PDF Rebuilder - Create Pixel-Perfect Enhanced PDF

This module rebuilds a PDF with enhanced text while preserving
the exact layout, fonts, colors, and positioning.

Author: Prashiskshan Backend Team
"""

import fitz  # PyMuPDF
import os
from typing import Dict, Any, List, Tuple


class PDFRebuilder:
    """Rebuild PDF with enhanced text while preserving layout."""
    
    def __init__(self):
        """Initialize the PDF rebuilder."""
        pass
    
    def rebuild_pdf(
        self,
        original_pdf_path: str,
        final_text_path: str,
        output_pdf_path: str = None
    ) -> Dict[str, Any]:
        """
        Rebuild PDF with enhanced text.
        
        Args:
            original_pdf_path: Path to original PDF
            final_text_path: Path to final enhanced text file
            output_pdf_path: Path to save rebuilt PDF
            
        Returns:
            Dictionary with results
        """
        try:
            # Read final text
            with open(final_text_path, 'r', encoding='utf-8') as f:
                final_text = f.read()
            
            # Determine output path
            if not output_pdf_path:
                base_name = os.path.splitext(original_pdf_path)[0]
                output_pdf_path = f"{base_name}_Enhanced.pdf"
            
            # Open original PDF
            doc = fitz.open(original_pdf_path)
            
            # Create new PDF with same page sizes
            output_doc = fitz.open()
            
            # Split final text into lines
            final_lines = [line for line in final_text.split('\n')]
            line_index = 0
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Create new page with same dimensions
                new_page = output_doc.new_page(
                    width=page.rect.width,
                    height=page.rect.height
                )
                
                # Get text blocks from original page
                blocks = page.get_text("dict")["blocks"]
                
                # Process each text block
                for block in blocks:
                    if block.get("type") == 0:  # Text block
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                original_text = span.get("text", "").strip()
                                
                                # Skip empty text
                                if not original_text:
                                    continue
                                
                                # Get the corresponding enhanced line
                                if line_index < len(final_lines):
                                    enhanced_text = final_lines[line_index].strip()
                                    line_index += 1
                                else:
                                    enhanced_text = original_text
                                
                                # Get formatting from original
                                bbox = span["bbox"]
                                font = span.get("font", "helv")
                                size = span.get("size", 11)
                                color = span.get("color", 0)
                                
                                # Insert enhanced text with original formatting
                                new_page.insert_text(
                                    (bbox[0], bbox[3]),
                                    enhanced_text,
                                    fontname=font,
                                    fontsize=size,
                                    color=self._int_to_rgb(color)
                                )
                
                # Copy images and other elements
                for block in blocks:
                    if block.get("type") == 1:  # Image block
                        # Copy image
                        bbox = fitz.Rect(block["bbox"])
                        pix = page.get_pixmap(clip=bbox)
                        new_page.insert_image(bbox, pixmap=pix)
            
            # Save the rebuilt PDF
            output_doc.save(output_pdf_path)
            output_doc.close()
            doc.close()
            
            return {
                'success': True,
                'output_pdf_path': output_pdf_path,
                'message': f'Successfully rebuilt PDF: {output_pdf_path}'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output_pdf_path': None
            }
    
    def _int_to_rgb(self, color_int: int) -> Tuple[float, float, float]:
        """Convert integer color to RGB tuple."""
        # PyMuPDF uses RGB values between 0 and 1
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return (r, g, b)


def rebuild_pdf_with_enhancements(
    original_pdf: str,
    final_text: str,
    output_pdf: str = None
) -> Dict[str, Any]:
    """
    Convenience function to rebuild PDF.
    
    Args:
        original_pdf: Path to original PDF
        final_text: Path to final enhanced text
        output_pdf: Path to save output PDF
        
    Returns:
        Results dictionary
    """
    rebuilder = PDFRebuilder()
    return rebuilder.rebuild_pdf(original_pdf, final_text, output_pdf)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("PDF Rebuilder - Create pixel-perfect enhanced PDF")
        print("\nUsage:")
        print("  python pdf_rebuilder.py <original_pdf> <final_text>")
        print("\nExample:")
        print("  python pdf_rebuilder.py resume.pdf resume_Final.txt")
    else:
        original = sys.argv[1]
        final = sys.argv[2]
        output = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = rebuild_pdf_with_enhancements(original, final, output)
        
        if result['success']:
            print(f"✓ {result['message']}")
        else:
            print(f"✗ Error: {result['error']}")
