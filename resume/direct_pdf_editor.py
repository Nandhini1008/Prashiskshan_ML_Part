"""
Direct PDF Editor - Modify Original PDF Content

This module directly edits the original PDF file, replacing text content
while preserving the exact layout, fonts, colors, and formatting.

Author: Prashiskshan Backend Team
"""

import os
import fitz  # PyMuPDF
from typing import Dict, Any, List, Tuple
from content_improver import ContentImprover


class DirectPDFEditor:
    """Edit PDF content directly without changing layout."""
    
    def __init__(self):
        """Initialize the PDF editor."""
        self.content_improver = ContentImprover()
    
    def enhance_pdf_directly(
        self,
        input_pdf_path: str,
        output_pdf_path: str,
        resume_text: str
    ) -> Dict[str, Any]:
        """
        Enhance PDF by directly editing text content.
        
        Args:
            input_pdf_path: Path to original PDF
            output_pdf_path: Path to save enhanced PDF
            resume_text: Original resume text (for LLM enhancement)
            
        Returns:
            Dictionary with success status and details
        """
        try:
            # Step 1: Get enhanced text from LLM
            print("🤖 Enhancing content with LLM...")
            enhanced_text = self.content_improver.improve_resume_content(resume_text)
            print("✓ LLM enhancement complete")
            
            # Step 2: Open original PDF
            doc = fitz.open(input_pdf_path)
            
            # Step 3: Extract text blocks with positions
            text_replacements = self._create_replacement_map(
                resume_text,
                enhanced_text
            )
            
            # Step 4: Apply replacements to PDF
            modifications_count = 0
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get all text instances on the page
                text_instances = page.get_text("dict")
                
                # Apply replacements
                for block in text_instances.get("blocks", []):
                    if block.get("type") == 0:  # Text block
                        for line in block.get("lines", []):
                            for span in line.get("spans", []):
                                original_text = span.get("text", "")
                                
                                # Check if we have a replacement
                                if original_text.strip() in text_replacements:
                                    replacement = text_replacements[original_text.strip()]
                                    
                                    # Get position and font info
                                    bbox = span["bbox"]
                                    font = span.get("font", "")
                                    size = span.get("size", 11)
                                    color = span.get("color", 0)
                                    
                                    # Remove old text
                                    page.add_redact_annot(bbox)
                                    
                                    # Add new text with same formatting
                                    page.insert_text(
                                        (bbox[0], bbox[3]),
                                        replacement,
                                        fontname=font,
                                        fontsize=size,
                                        color=color
                                    )
                                    
                                    modifications_count += 1
                
                # Apply redactions
                page.apply_redactions()
            
            # Step 5: Save enhanced PDF
            doc.save(output_pdf_path)
            doc.close()
            
            return {
                'success': True,
                'enhanced_pdf_path': output_pdf_path,
                'modifications_count': modifications_count,
                'message': f'Successfully enhanced PDF with {modifications_count} text modifications'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'enhanced_pdf_path': None
            }
    
    def _create_replacement_map(
        self,
        original_text: str,
        enhanced_text: str
    ) -> Dict[str, str]:
        """
        Create a mapping of original text to enhanced text.
        
        Args:
            original_text: Original resume text
            enhanced_text: Enhanced resume text
            
        Returns:
            Dictionary mapping original phrases to enhanced ones
        """
        replacements = {}
        
        # Split into sentences/phrases
        original_lines = [line.strip() for line in original_text.split('\n') if line.strip()]
        enhanced_lines = [line.strip() for line in enhanced_text.split('\n') if line.strip()]
        
        # Create mapping (simple line-by-line for now)
        for i, orig_line in enumerate(original_lines):
            if i < len(enhanced_lines):
                enh_line = enhanced_lines[i]
                if orig_line != enh_line and len(orig_line) > 10:
                    replacements[orig_line] = enh_line
        
        return replacements


def enhance_pdf_in_place(
    input_pdf_path: str,
    output_pdf_path: str,
    resume_text: str
) -> Dict[str, Any]:
    """
    Convenience function to enhance PDF in place.
    
    Args:
        input_pdf_path: Path to original PDF
        output_pdf_path: Path to save enhanced PDF
        resume_text: Original resume text
        
    Returns:
        Enhancement results
    """
    editor = DirectPDFEditor()
    return editor.enhance_pdf_directly(input_pdf_path, output_pdf_path, resume_text)


if __name__ == "__main__":
    print("Direct PDF Editor - Modify PDFs while preserving layout")
