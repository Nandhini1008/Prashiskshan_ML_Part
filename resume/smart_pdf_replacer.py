"""
Smart Differential PDF Replacer - Surgical Text Enhancement

This module intelligently compares original and enhanced text,
identifies ONLY the differences, and replaces only those specific
text blocks in the PDF while leaving everything else untouched.

Author: Prashiskshan Backend Team
"""

import fitz  # PyMuPDF
import os
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher


class SmartDifferentialReplacer:
    """Smart PDF replacer that only modifies changed text."""
    
    def __init__(self):
        """Initialize the smart replacer."""
        pass
    
    def replace_changed_text_only(
        self,
        original_pdf_path: str,
        original_text_path: str,
        enhanced_text_path: str,
        output_pdf_path: str = None
    ) -> Dict[str, Any]:
        """
        Replace only the text that actually changed.
        
        Strategy:
        1. Compare original vs enhanced text line-by-line
        2. Identify ONLY the lines that changed
        3. Find exact pixel positions of those lines in PDF
        4. Replace ONLY those specific text blocks
        5. Leave everything else untouched
        
        Args:
            original_pdf_path: Path to original PDF
            original_text_path: Path to original extracted text
            enhanced_text_path: Path to enhanced text
            output_pdf_path: Path to save enhanced PDF
            
        Returns:
            Results dictionary
        """
        try:
            # Read texts
            print("📖 Reading original and enhanced texts...")
            with open(original_text_path, 'r', encoding='utf-8') as f:
                original_text = f.read()
            
            with open(enhanced_text_path, 'r', encoding='utf-8') as f:
                enhanced_text = f.read()
            
            # Split into lines
            original_lines = [line.strip() for line in original_text.split('\n') if line.strip()]
            enhanced_lines = [line.strip() for line in enhanced_text.split('\n') if line.strip()]
            
            # Find differences
            print("🔍 Identifying changes...")
            changes = self._find_changes(original_lines, enhanced_lines)
            print(f"✓ Found {len(changes)} text blocks that need enhancement")
            
            # Determine output path
            if not output_pdf_path:
                base_name = os.path.splitext(original_pdf_path)[0]
                output_pdf_path = f"{base_name}_Enhanced.pdf"
            
            # Open original PDF
            print("📄 Opening original PDF...")
            doc = fitz.open(original_pdf_path)
            
            # Extract all text with positions
            print("🎯 Locating text positions in PDF...")
            text_blocks = self._extract_text_blocks(doc)
            
            # Match changes to PDF positions
            print("🔧 Applying surgical enhancements...")
            replacements_made = 0
            
            for change in changes:
                original_text = change['original']
                enhanced_text = change['enhanced']
                
                # Find this text block in the PDF
                matching_blocks = self._find_matching_blocks(text_blocks, original_text)
                
                for block in matching_blocks:
                    page = doc[block['page']]
                    
                    # Redact old text
                    page.add_redact_annot(block['bbox'], text="")
                    page.apply_redactions()
                    
                    # Insert enhanced text at exact same position
                    try:
                        page.insert_text(
                            (block['bbox'][0], block['bbox'][3] - 3),
                            enhanced_text,
                            fontname=block.get('font', 'helv'),
                            fontsize=block.get('size', 11),
                            color=self._int_to_rgb(block.get('color', 0))
                        )
                        replacements_made += 1
                    except:
                        # Fallback to default font
                        page.insert_text(
                            (block['bbox'][0], block['bbox'][3] - 3),
                            enhanced_text,
                            fontsize=block.get('size', 11)
                        )
                        replacements_made += 1
            
            print(f"✓ Made {replacements_made} surgical text replacements")
            
            # Save enhanced PDF
            print(f"💾 Saving enhanced PDF...")
            doc.save(output_pdf_path, garbage=4, deflate=True)
            doc.close()
            
            print(f"✅ Enhanced PDF created: {output_pdf_path}")
            
            return {
                'success': True,
                'output_pdf_path': output_pdf_path,
                'changes_identified': len(changes),
                'replacements_made': replacements_made,
                'message': f'Successfully enhanced PDF with {replacements_made} surgical improvements'
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
    
    def _find_changes(
        self,
        original_lines: List[str],
        enhanced_lines: List[str]
    ) -> List[Dict[str, str]]:
        """
        Find lines that changed between original and enhanced.
        
        Returns list of {'original': str, 'enhanced': str} dicts
        """
        changes = []
        
        # Use SequenceMatcher for intelligent diff
        matcher = SequenceMatcher(None, original_lines, enhanced_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Text was changed
                for i, j in zip(range(i1, i2), range(j1, j2)):
                    if i < len(original_lines) and j < len(enhanced_lines):
                        if original_lines[i] != enhanced_lines[j]:
                            changes.append({
                                'original': original_lines[i],
                                'enhanced': enhanced_lines[j]
                            })
            elif tag == 'insert':
                # New text was added (rare in our case)
                for j in range(j1, j2):
                    if j < len(enhanced_lines):
                        changes.append({
                            'original': '',
                            'enhanced': enhanced_lines[j]
                        })
        
        return changes
    
    def _extract_text_blocks(self, doc: fitz.Document) -> List[Dict]:
        """Extract all text blocks with positions from PDF."""
        all_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span.get("text", "").strip()
                            if text:
                                all_blocks.append({
                                    'page': page_num,
                                    'text': text,
                                    'bbox': span["bbox"],
                                    'font': span.get("font", "helv"),
                                    'size': span.get("size", 11),
                                    'color': span.get("color", 0)
                                })
        
        return all_blocks
    
    def _find_matching_blocks(
        self,
        text_blocks: List[Dict],
        search_text: str
    ) -> List[Dict]:
        """Find PDF blocks that match the search text."""
        matches = []
        
        # Try exact match first
        for block in text_blocks:
            if block['text'] == search_text:
                matches.append(block)
        
        # If no exact match, try fuzzy match
        if not matches:
            for block in text_blocks:
                similarity = SequenceMatcher(None, block['text'], search_text).ratio()
                if similarity > 0.8:  # 80% similarity threshold
                    matches.append(block)
        
        return matches
    
    def _int_to_rgb(self, color_int: int) -> tuple:
        """Convert integer color to RGB tuple (0-1 range)."""
        if color_int == 0:
            return (0, 0, 0)  # Black
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return (r, g, b)


def create_smart_enhanced_pdf(
    original_pdf: str,
    original_text: str,
    enhanced_text: str,
    output_pdf: str = None
) -> Dict[str, Any]:
    """
    Convenience function for smart differential enhancement.
    
    Args:
        original_pdf: Path to original PDF
        original_text: Path to original text file
        enhanced_text: Path to enhanced text file
        output_pdf: Path to save enhanced PDF
        
    Returns:
        Results dictionary
    """
    replacer = SmartDifferentialReplacer()
    return replacer.replace_changed_text_only(
        original_pdf,
        original_text,
        enhanced_text,
        output_pdf
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Smart Differential PDF Replacer")
        print("\nUsage:")
        print("  python smart_pdf_replacer.py <original_pdf> <original_text> <enhanced_text>")
        print("\nExample:")
        print("  python smart_pdf_replacer.py resume.pdf resume_original.txt resume_Enhanced.txt")
    else:
        original_pdf = sys.argv[1]
        original_txt = sys.argv[2]
        enhanced_txt = sys.argv[3]
        output = sys.argv[4] if len(sys.argv) > 4 else None
        
        result = create_smart_enhanced_pdf(original_pdf, original_txt, enhanced_txt, output)
        
        if result['success']:
            print(f"\n✓ {result['message']}")
            print(f"📄 Output: {result['output_pdf_path']}")
            print(f"📊 Changes: {result['changes_identified']} identified, {result['replacements_made']} applied")
        else:
            print(f"\n✗ Failed: {result['error']}")
