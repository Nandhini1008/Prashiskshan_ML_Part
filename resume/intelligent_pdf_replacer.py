"""
Intelligent PDF Text Replacer with Reflow

This module intelligently replaces text in PDFs by:
1. Identifying complete sentences/blocks to replace
2. Removing the entire original block
3. Rewriting with enhanced text and proper reflow

Author: Prashiskshan Backend Team
"""

import fitz  # PyMuPDF
import os
from typing import Dict, Any, List, Tuple
from difflib import SequenceMatcher


class IntelligentPDFReplacer:
    """Smart PDF replacer with text reflow capability."""
    
    def __init__(self):
        """Initialize the intelligent replacer."""
        pass
    
    def replace_with_reflow(
        self,
        original_pdf_path: str,
        original_text: str,
        enhanced_text: str,
        output_pdf_path: str = None
    ) -> Dict[str, Any]:
        """
        Replace text intelligently with reflow.
        
        Strategy:
        1. Find differences between original and enhanced
        2. Identify complete blocks (sentences/paragraphs) that changed
        3. Remove entire original blocks
        4. Rewrite with enhanced text, allowing reflow
        
        Args:
            original_pdf_path: Path to original PDF
            original_text: Original extracted text
            enhanced_text: Enhanced text
            output_pdf_path: Path to save enhanced PDF
            
        Returns:
            Results dictionary
        """
        try:
            print("📖 Analyzing text differences...")
            
            # Split into lines
            original_lines = [line.strip() for line in original_text.split('\n') if line.strip()]
            enhanced_lines = [line.strip() for line in enhanced_text.split('\n') if line.strip()]
            
            # Find changed blocks
            changes = self._find_changed_blocks(original_lines, enhanced_lines)
            print(f"✓ Found {len(changes)} blocks to enhance")
            
            if len(changes) == 0:
                print("⚠ No changes detected - text is identical")
                return {
                    'success': False,
                    'error': 'No changes detected between original and enhanced text',
                    'output_pdf_path': None
                }
            
            # Determine output path
            if not output_pdf_path:
                base_name = os.path.splitext(original_pdf_path)[0]
                output_pdf_path = f"{base_name}_Enhanced.pdf"
            
            # Open original PDF
            print("📄 Opening original PDF...")
            doc = fitz.open(original_pdf_path)
            
            # Extract text blocks with positions
            print("🎯 Mapping text positions...")
            text_blocks = self._extract_text_blocks_with_context(doc)
            
            # Apply intelligent replacements
            print("🔧 Applying intelligent replacements with reflow...")
            replacements_made = 0
            
            for change in changes:
                original_block = change['original']
                enhanced_block = change['enhanced']
                
                # Find matching blocks in PDF
                matches = self._find_matching_text_blocks(text_blocks, original_block)
                
                for match in matches:
                    page = doc[match['page']]
                    
                    # Get the bounding box for the entire block
                    bbox = match['bbox']
                    
                    # Remove the entire original block
                    page.add_redact_annot(bbox, text="")
                    page.apply_redactions()
                    
                    # Insert enhanced text with reflow
                    # Use insert_textbox for automatic text wrapping
                    try:
                        rc = page.insert_textbox(
                            bbox,
                            enhanced_block,
                            fontname=match.get('font', 'helv'),
                            fontsize=match.get('size', 11),
                            color=self._int_to_rgb(match.get('color', 0)),
                            align=fitz.TEXT_ALIGN_LEFT
                        )
                        
                        if rc >= 0:  # Success
                            replacements_made += 1
                        else:
                            # If text doesn't fit, try with smaller font
                            smaller_size = match.get('size', 11) * 0.9
                            rc = page.insert_textbox(
                                bbox,
                                enhanced_block,
                                fontsize=smaller_size,
                                align=fitz.TEXT_ALIGN_LEFT
                            )
                            if rc >= 0:
                                replacements_made += 1
                    except Exception as e:
                        print(f"  ⚠ Could not replace block: {str(e)[:50]}")
            
            print(f"✓ Made {replacements_made} intelligent replacements")
            
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
                'message': f'Successfully enhanced PDF with {replacements_made} intelligent replacements'
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
    
    def _find_changed_blocks(
        self,
        original_lines: List[str],
        enhanced_lines: List[str]
    ) -> List[Dict[str, str]]:
        """Find blocks of text that changed."""
        changes = []
        
        # Use SequenceMatcher for intelligent diff
        matcher = SequenceMatcher(None, original_lines, enhanced_lines)
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'replace':
                # Combine multiple lines into blocks
                original_block = ' '.join(original_lines[i1:i2])
                enhanced_block = ' '.join(enhanced_lines[j1:j2])
                
                if original_block != enhanced_block:
                    changes.append({
                        'original': original_block,
                        'enhanced': enhanced_block
                    })
        
        return changes
    
    def _extract_text_blocks_with_context(self, doc: fitz.Document) -> List[Dict]:
        """Extract text blocks with full context."""
        all_blocks = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if block.get("type") == 0:  # Text block
                    # Combine all text in the block
                    block_text = ""
                    block_bbox = None
                    block_font = "helv"
                    block_size = 11
                    block_color = 0
                    
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            block_text += span.get("text", "") + " "
                            if block_bbox is None:
                                block_bbox = list(span["bbox"])
                                block_font = span.get("font", "helv")
                                block_size = span.get("size", 11)
                                block_color = span.get("color", 0)
                            else:
                                # Expand bbox to include this span
                                bbox = span["bbox"]
                                block_bbox[0] = min(block_bbox[0], bbox[0])
                                block_bbox[1] = min(block_bbox[1], bbox[1])
                                block_bbox[2] = max(block_bbox[2], bbox[2])
                                block_bbox[3] = max(block_bbox[3], bbox[3])
                    
                    if block_text.strip():
                        all_blocks.append({
                            'page': page_num,
                            'text': block_text.strip(),
                            'bbox': fitz.Rect(block_bbox),
                            'font': block_font,
                            'size': block_size,
                            'color': block_color
                        })
        
        return all_blocks
    
    def _find_matching_text_blocks(
        self,
        text_blocks: List[Dict],
        search_text: str
    ) -> List[Dict]:
        """Find PDF blocks that match the search text."""
        matches = []
        
        # Try fuzzy matching
        for block in text_blocks:
            similarity = SequenceMatcher(None, block['text'], search_text).ratio()
            if similarity > 0.7:  # 70% similarity threshold
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


def create_intelligent_enhanced_pdf(
    original_pdf: str,
    original_text: str,
    enhanced_text: str,
    output_pdf: str = None
) -> Dict[str, Any]:
    """
    Convenience function for intelligent PDF enhancement.
    
    Args:
        original_pdf: Path to original PDF
        original_text: Original text content
        enhanced_text: Enhanced text content
        output_pdf: Path to save enhanced PDF
        
    Returns:
        Results dictionary
    """
    replacer = IntelligentPDFReplacer()
    return replacer.replace_with_reflow(
        original_pdf,
        original_text,
        enhanced_text,
        output_pdf
    )


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 4:
        print("Intelligent PDF Replacer with Reflow")
        print("\nUsage:")
        print("  python intelligent_pdf_replacer.py <original_pdf> <original_text> <enhanced_text>")
    else:
        original_pdf = sys.argv[1]
        original_txt = sys.argv[2]
        enhanced_txt = sys.argv[3]
        output = sys.argv[4] if len(sys.argv) > 4 else None
        
        # Read text files
        with open(original_txt, 'r', encoding='utf-8') as f:
            orig_text = f.read()
        with open(enhanced_txt, 'r', encoding='utf-8') as f:
            enh_text = f.read()
        
        result = create_intelligent_enhanced_pdf(original_pdf, orig_text, enh_text, output)
        
        if result['success']:
            print(f"\n✓ {result['message']}")
            print(f"📄 Output: {result['output_pdf_path']}")
        else:
            print(f"\n✗ Failed: {result['error']}")
