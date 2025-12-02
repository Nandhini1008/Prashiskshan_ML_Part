"""
JSON-Based Resume Enhancement System

This module uses LLM-generated enhancement JSON to apply changes to PDFs.

Author: Prashiskshan Backend Team
"""

import os
import json
from typing import Dict, Any


class SimpleResumeEnhancer:
    """LLM-based enhancement with JSON output."""
    
    def __init__(self):
        """Initialize the enhancer."""
        pass
    
    def enhance_resume_text(
        self,
        original_pdf_path: str,
        resume_text: str,
        evaluation: Dict[str, Any] = None,
        output_dir: str = None
    ) -> Dict[str, Any]:
        """
        Enhance resume using LLM and create enhancement JSON.
        
        Args:
            original_pdf_path: Path to original PDF
            resume_text: Extracted resume text
            evaluation: ATS evaluation results
            output_dir: Directory to save outputs
            
        Returns:
            Dictionary with results
        """
        try:
            # Determine output path
            if not output_dir:
                output_dir = os.path.dirname(original_pdf_path)
            
            # Extract filename
            pdf_filename = os.path.basename(original_pdf_path)
            base_name = os.path.splitext(pdf_filename)[0]
            
            # Step 1: Generate enhancements using LLM
            print("🤖 Generating enhancements with LLM...")
            from llm_enhancement_analyzer import analyze_and_generate_enhancements
            
            enhancement_json_path = os.path.join(output_dir, f"{base_name}_Enhancements.json")
            
            result = analyze_and_generate_enhancements(
                resume_text,
                evaluation or {},
                enhancement_json_path
            )
            
            if not result.get('success'):
                print(f"⚠ LLM enhancement failed: {result.get('error')}")
                return {
                    'success': False,
                    'error': result.get('error'),
                    'enhancement_json_path': None
                }
            
            enhancements = result['enhancements']
            enhancement_list = enhancements.get('enhancements', [])
            
            # Step 2: Create enhanced text by applying changes
            enhanced_text = resume_text
            for enh in enhancement_list:
                original = enh.get('original', '')
                enhanced = enh.get('enhanced', '')
                if original and enhanced:
                    enhanced_text = enhanced_text.replace(original, enhanced)
            
            # Step 3: Save enhanced text
            enhanced_text_path = os.path.join(output_dir, f"{base_name}_Enhanced.txt")
            with open(enhanced_text_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_text)
            print(f"✓ Enhanced text saved: {enhanced_text_path}")
            
            # Step 4: Save original text
            original_text_path = os.path.join(output_dir, f"{base_name}_Original.txt")
            with open(original_text_path, 'w', encoding='utf-8') as f:
                f.write(resume_text)
            print(f"✓ Original text saved: {original_text_path}")
            
            # Step 5: Create comparison file
            comparison_path = os.path.join(output_dir, f"{base_name}_Comparison.txt")
            with open(comparison_path, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("RESUME ENHANCEMENTS\n")
                f.write("="*80 + "\n\n")
                
                for i, enh in enumerate(enhancement_list, 1):
                    f.write(f"\n{i}. {enh.get('reason', 'Enhancement')}\n")
                    f.write(f"   ORIGINAL: {enh.get('original', '')}\n")
                    f.write(f"   ENHANCED: {enh.get('enhanced', '')}\n")
                
                f.write("\n\n" + "="*80 + "\n")
                f.write("ORIGINAL RESUME\n")
                f.write("="*80 + "\n\n")
                f.write(resume_text)
                
                f.write("\n\n" + "="*80 + "\n")
                f.write("ENHANCED RESUME\n")
                f.write("="*80 + "\n\n")
                f.write(enhanced_text)
            
            print(f"✓ Comparison file saved: {comparison_path}")
            
            # Step 6: Try to create enhanced PDF
            print("📄 Creating enhanced PDF...")
            output_pdf_path = os.path.join(output_dir, f"{base_name}_Enhanced.pdf")
            
            try:
                from json_pdf_applier import apply_enhancements_to_pdf
                pdf_result = apply_enhancements_to_pdf(
                    original_pdf_path,
                    enhancement_list,
                    output_pdf_path
                )
                
                if pdf_result.get('success'):
                    print(f"✅ Enhanced PDF created: {output_pdf_path}")
                    pdf_success = True
                else:
                    print(f"⚠ PDF creation had issues: {pdf_result.get('error')}")
                    pdf_success = False
            except Exception as e:
                print(f"⚠ PDF creation failed: {str(e)[:100]}")
                pdf_success = False
            
            return {
                'success': True,
                'enhancement_json_path': enhancement_json_path,
                'enhanced_text_path': enhanced_text_path,
                'original_text_path': original_text_path,
                'comparison_path': comparison_path,
                'enhanced_pdf_path': output_pdf_path if pdf_success else None,
                'enhancements_count': len(enhancement_list),
                'message': f'Generated {len(enhancement_list)} enhancements successfully!'
            }
            
        except Exception as e:
            import traceback
            print(f"❌ Error: {str(e)}")
            print(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'enhancement_json_path': None
            }


def enhance_resume_simple(
    pdf_path: str,
    resume_text: str,
    evaluation: Dict[str, Any] = None
) -> Dict[str, Any]:
    """Convenience function for enhancement."""
    enhancer = SimpleResumeEnhancer()
    return enhancer.enhance_resume_text(pdf_path, resume_text, evaluation)


if __name__ == "__main__":
    print("LLM-Based JSON Enhancement System")
