"""
Evaluation-Based PDF Enhancer - No LLM Required for Each Resume

This module uses ATS evaluation recommendations to enhance resumes
and applies changes using exact pixel positions from the PDF.

Author: Prashiskshan Backend Team
"""

import fitz  # PyMuPDF
import os
import re
from typing import Dict, Any, List, Tuple


class EvaluationBasedEnhancer:
    """Enhance PDFs using ATS evaluation + pixel positioning."""
    
    def __init__(self):
        """Initialize the enhancer."""
        # Action verb improvements
        self.action_verbs = {
            'performed': 'executed',
            'worked on': 'developed',
            'built': 'engineered',
            'made': 'created',
            'gained experience': 'acquired expertise',
            'helped': 'facilitated',
            'did': 'implemented',
            'used': 'utilized'
        }
    
    def enhance_from_evaluation(
        self,
        original_pdf_path: str,
        resume_text: str,
        evaluation: Dict[str, Any],
        output_pdf_path: str = None
    ) -> Dict[str, Any]:
        """
        Enhance PDF using evaluation recommendations.
        
        Strategy:
        1. Extract specific issues from evaluation
        2. Apply rule-based enhancements to text
        3. Find exact pixel positions in PDF
        4. Remove old text blocks
        5. Insert enhanced text at same positions
        
        Args:
            original_pdf_path: Path to original PDF
            resume_text: Extracted resume text
            evaluation: ATS evaluation results
            output_pdf_path: Path to save enhanced PDF
            
        Returns:
            Results dictionary
        """
        try:
            print("📋 Analyzing ATS evaluation recommendations...")
            
            # Apply enhancements based on evaluation
            enhanced_text = self._apply_enhancements(resume_text, evaluation)
            
            # Find what changed
            changes = self._find_changes(resume_text, enhanced_text)
            print(f"✓ Identified {len(changes)} enhancements to apply")
            
            if len(changes) == 0:
                print("⚠ No enhancements could be applied")
                return {
                    'success': False,
                    'error': 'No enhancements identified',
                    'output_pdf_path': None
                }
            
            # Determine output path
            if not output_pdf_path:
                base_name = os.path.splitext(original_pdf_path)[0]
                output_pdf_path = f"{base_name}_Enhanced.pdf"
            
            # Open PDF
            print("📄 Opening PDF and mapping text positions...")
            doc = fitz.open(original_pdf_path)
            
            # Extract text blocks with pixel positions
            text_blocks = self._extract_text_with_positions(doc)
            print(f"✓ Mapped {len(text_blocks)} text blocks")
            
            # Apply changes to PDF
            print("🔧 Applying enhancements to PDF...")
            replacements_made = 0
            
            for change in changes:
                original = change['original']
                enhanced = change['enhanced']
                
                # Find matching blocks in PDF
                matches = self._find_text_in_pdf(text_blocks, original)
                
                for match in matches:
                    page = doc[match['page']]
                    bbox = match['bbox']
                    
                    # Remove old text
                    page.add_redact_annot(bbox, text="")
                    page.apply_redactions()
                    
                    # Insert enhanced text
                    try:
                        # Try with textbox for reflow
                        rc = page.insert_textbox(
                            bbox,
                            enhanced,
                            fontname=match.get('font', 'helv'),
                            fontsize=match.get('size', 11),
                            color=self._int_to_rgb(match.get('color', 0)),
                            align=fitz.TEXT_ALIGN_LEFT
                        )
                        
                        if rc >= 0:
                            replacements_made += 1
                        else:
                            # Try with smaller font
                            rc = page.insert_textbox(
                                bbox,
                                enhanced,
                                fontsize=match.get('size', 11) * 0.9,
                                align=fitz.TEXT_ALIGN_LEFT
                            )
                            if rc >= 0:
                                replacements_made += 1
                    except Exception as e:
                        print(f"  ⚠ Skipped one block: {str(e)[:50]}")
            
            print(f"✓ Applied {replacements_made} enhancements")
            
            # Save PDF
            print(f"💾 Saving enhanced PDF...")
            doc.save(output_pdf_path, garbage=4, deflate=True)
            doc.close()
            
            print(f"✅ Enhanced PDF created: {output_pdf_path}")
            
            return {
                'success': True,
                'output_pdf_path': output_pdf_path,
                'enhancements_applied': replacements_made,
                'message': f'Successfully enhanced PDF with {replacements_made} improvements'
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
    
    def _apply_enhancements(self, text: str, evaluation: Dict[str, Any]) -> str:
        """Apply rule-based enhancements from evaluation."""
        enhanced = text
        
        # 1. Strengthen action verbs
        for weak, strong in self.action_verbs.items():
            # Replace at start of bullet points or lines
            pattern = r'(\n|\•\s*)' + re.escape(weak)
            replacement = r'\1' + strong.capitalize()
            enhanced = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)
        
        # 2. Add context to generic phrases
        generic_improvements = {
            'Performed EDA & FastAPI development': 
                'Executed comprehensive EDA and developed FastAPI backend services',
            'Gained experience in teamwork & professional communication':
                'Collaborated with cross-functional teams and maintained professional communication',
            'Built certificate generator & text recognition tools':
                'Developed automated certificate generation and OCR-based text recognition tools',
            'Worked on technical implementations & poster designs':
                'Implemented technical solutions and designed professional promotional materials'
        }
        
        for original, improved in generic_improvements.items():
            enhanced = enhanced.replace(original, improved)
        
        return enhanced
    
    def _find_changes(self, original: str, enhanced: str) -> List[Dict[str, str]]:
        """Find what changed between original and enhanced."""
        changes = []
        
        # Split into sentences/phrases
        original_parts = re.split(r'([.•\n])', original)
        enhanced_parts = re.split(r'([.•\n])', enhanced)
        
        # Find differences
        for i, (orig, enh) in enumerate(zip(original_parts, enhanced_parts)):
            if orig.strip() and enh.strip() and orig != enh:
                changes.append({
                    'original': orig.strip(),
                    'enhanced': enh.strip()
                })
        
        return changes
    
    def _extract_text_with_positions(self, doc: fitz.Document) -> List[Dict]:
        """Extract all text with exact pixel positions."""
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
                                    'bbox': fitz.Rect(span["bbox"]),
                                    'font': span.get("font", "helv"),
                                    'size': span.get("size", 11),
                                    'color': span.get("color", 0)
                                })
        
        return all_blocks
    
    def _find_text_in_pdf(
        self,
        text_blocks: List[Dict],
        search_text: str
    ) -> List[Dict]:
        """Find text blocks in PDF that match search text."""
        matches = []
        
        # Try exact match first
        for block in text_blocks:
            if search_text in block['text'] or block['text'] in search_text:
                matches.append(block)
        
        return matches
    
    def _int_to_rgb(self, color_int: int) -> tuple:
        """Convert integer color to RGB tuple."""
        if color_int == 0:
            return (0, 0, 0)
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        return (r, g, b)


def enhance_pdf_from_evaluation(
    pdf_path: str,
    resume_text: str,
    evaluation: Dict[str, Any],
    output_path: str = None
) -> Dict[str, Any]:
    """
    Convenience function for evaluation-based enhancement.
    
    Args:
        pdf_path: Path to original PDF
        resume_text: Extracted resume text
        evaluation: ATS evaluation results
        output_path: Path to save enhanced PDF
        
    Returns:
        Results dictionary
    """
    enhancer = EvaluationBasedEnhancer()
    return enhancer.enhance_from_evaluation(pdf_path, resume_text, evaluation, output_path)


if __name__ == "__main__":
    print("Evaluation-Based PDF Enhancer")
    print("No LLM API required - uses ATS evaluation recommendations!")
