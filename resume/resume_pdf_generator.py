"""
Resume PDF Generator - Professional PDF Creation

This module generates professional, ATS-friendly PDF resumes using ReportLab.

Key Features:
- Clean, professional layout
- ATS-compatible formatting
- Consistent styling and spacing
- Support for all resume sections

Author: Prashiskshan Backend Team
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, Any, List
import os


class ResumePDFGenerator:
    """Professional PDF resume generator."""
    
    def __init__(self):
        """Initialize PDF generator with styles."""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for resume."""
        # Name style
        self.styles.add(ParagraphStyle(
            name='ResumeName',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#444444'),
            alignment=TA_CENTER,
            spaceAfter=12
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=8,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=colors.HexColor('#2c5aa0'),
            borderPadding=0,
            leftIndent=0,
            underlineProportion=0.3,
            underlineGap=2,
            underlineColor=colors.HexColor('#2c5aa0'),
            underlineWidth=2
        ))
        
        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#1a1a1a'),
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        # Company style
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#444444'),
            fontName='Helvetica-Bold',
            spaceAfter=4
        ))
        
        # Date style
        self.styles.add(ParagraphStyle(
            name='DateStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Oblique',
            alignment=TA_RIGHT
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            leftIndent=20,
            spaceAfter=4,
            leading=14
        ))
        
        # Summary style
        self.styles.add(ParagraphStyle(
            name='Summary',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=14
        ))
        
        # Skill style
        self.styles.add(ParagraphStyle(
            name='Skill',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#333333'),
            spaceAfter=3
        ))
    
    def generate_resume_pdf(
        self, 
        enhanced_content: Dict[str, Any], 
        output_path: str
    ) -> str:
        """
        Generate PDF resume from enhanced content.
        
        Args:
            enhanced_content: Enhanced resume content from ResumeEnhancer
            output_path: Path to save the PDF
            
        Returns:
            Path to generated PDF
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Build content
        story = []
        
        # Header
        story.extend(self._create_header(enhanced_content.get('header', {})))
        story.append(Spacer(1, 0.2*inch))
        
        # Summary
        if enhanced_content.get('summary'):
            story.extend(self._create_summary(enhanced_content['summary']))
            story.append(Spacer(1, 0.15*inch))
        
        # Professional Experience
        if enhanced_content.get('experience'):
            story.extend(self._create_experience_section(enhanced_content['experience']))
            story.append(Spacer(1, 0.15*inch))
        
        # Skills
        if enhanced_content.get('skills'):
            story.extend(self._create_skills_section(enhanced_content['skills']))
            story.append(Spacer(1, 0.15*inch))
        
        # Projects
        if enhanced_content.get('projects'):
            story.extend(self._create_projects_section(enhanced_content['projects']))
            story.append(Spacer(1, 0.15*inch))
        
        # Education
        if enhanced_content.get('education'):
            story.extend(self._create_education_section(enhanced_content['education']))
            story.append(Spacer(1, 0.15*inch))
        
        # Certifications
        if enhanced_content.get('certifications'):
            story.extend(self._create_certifications_section(enhanced_content['certifications']))
            story.append(Spacer(1, 0.15*inch))
        
        # Accomplishments
        if enhanced_content.get('accomplishments'):
            story.extend(self._create_accomplishments_section(enhanced_content['accomplishments']))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _create_header(self, header: Dict[str, str]) -> List:
        """Create header section with name and contact info."""
        elements = []
        
        # Name
        name = header.get('name', 'Professional Resume')
        elements.append(Paragraph(name, self.styles['ResumeName']))
        
        # Contact info
        contact_parts = []
        
        if header.get('location'):
            contact_parts.append(header['location'])
        
        if header.get('phone'):
            contact_parts.append(header['phone'])
        
        if header.get('email'):
            contact_parts.append(f"<a href='mailto:{header['email']}'>{header['email']}</a>")
        
        if header.get('linkedin'):
            linkedin_url = f"https://{header['linkedin']}" if not header['linkedin'].startswith('http') else header['linkedin']
            contact_parts.append(f"<a href='{linkedin_url}'>{header['linkedin']}</a>")
        
        if header.get('github'):
            github_url = f"https://{header['github']}" if not header['github'].startswith('http') else header['github']
            contact_parts.append(f"<a href='{github_url}'>{header['github']}</a>")
        
        if contact_parts:
            contact_text = " | ".join(contact_parts)
            elements.append(Paragraph(contact_text, self.styles['ContactInfo']))
        
        return elements
    
    def _create_summary(self, summary: str) -> List:
        """Create professional summary section."""
        elements = []
        
        # Section header with underline
        elements.append(self._create_section_header("PROFESSIONAL SUMMARY"))
        elements.append(Paragraph(summary, self.styles['Summary']))
        
        return elements
    
    def _create_section_header(self, title: str) -> Paragraph:
        """Create a section header with underline."""
        # Create table for header with underline
        header_text = f"<b>{title}</b>"
        return Paragraph(header_text, self.styles['SectionHeader'])
    
    def _create_experience_section(self, experiences: List[Dict[str, Any]]) -> List:
        """Create professional experience section."""
        elements = []
        
        elements.append(self._create_section_header("PROFESSIONAL EXPERIENCE"))
        
        for i, exp in enumerate(experiences):
            # Job title and dates in a table for alignment
            title = exp.get('title', 'Position')
            company = exp.get('company', '')
            location = exp.get('location', '')
            dates = exp.get('dates', '')
            
            # Title and company
            if company:
                title_text = f"<b>{title}</b>"
                elements.append(Paragraph(title_text, self.styles['JobTitle']))
                
                company_location = company
                if location:
                    company_location += f" – {location}"
                
                # Create table for company and dates alignment
                data = [[company_location, dates]]
                t = Table(data, colWidths=[4.5*inch, 2*inch])
                t.setStyle(TableStyle([
                    ('FONT', (0, 0), (0, 0), 'Helvetica-Bold', 10),
                    ('FONT', (1, 0), (1, 0), 'Helvetica-Oblique', 9),
                    ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#444444')),
                    ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#666666')),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(t)
            else:
                # Just title and dates
                data = [[f"<b>{title}</b>", dates]]
                t = Table(data, colWidths=[4.5*inch, 2*inch])
                t.setStyle(TableStyle([
                    ('FONT', (0, 0), (0, 0), 'Helvetica-Bold', 11),
                    ('FONT', (1, 0), (1, 0), 'Helvetica-Oblique', 9),
                    ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#1a1a1a')),
                    ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#666666')),
                    ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(t)
            
            elements.append(Spacer(1, 0.05*inch))
            
            # Bullets
            for bullet in exp.get('bullets', []):
                bullet_text = f"• {bullet}"
                elements.append(Paragraph(bullet_text, self.styles['BulletPoint']))
            
            # Add spacing between jobs
            if i < len(experiences) - 1:
                elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _create_skills_section(self, skills: List[str]) -> List:
        """Create skills section."""
        elements = []
        
        elements.append(self._create_section_header("TECHNICAL SKILLS"))
        
        # Organize skills in a clean format
        for skill in skills:
            skill_text = f"• {skill}"
            elements.append(Paragraph(skill_text, self.styles['Skill']))
        
        return elements
    
    def _create_projects_section(self, projects: List[Dict[str, Any]]) -> List:
        """Create projects section."""
        elements = []
        
        elements.append(self._create_section_header("PROJECTS"))
        
        for i, project in enumerate(projects):
            name = project.get('name', 'Project')
            description = project.get('description', '')
            technologies = project.get('technologies', [])
            
            # Project name and description
            project_text = f"<b>{name}</b>: {description}"
            elements.append(Paragraph(f"• {project_text}", self.styles['BulletPoint']))
            
            # Technologies
            if technologies:
                tech_text = " | ".join(technologies)
                elements.append(Paragraph(f"  <i>{tech_text}</i>", self.styles['Skill']))
            
            if i < len(projects) - 1:
                elements.append(Spacer(1, 0.05*inch))
        
        return elements
    
    def _create_education_section(self, education: List[Dict[str, Any]]) -> List:
        """Create education section."""
        elements = []
        
        elements.append(self._create_section_header("EDUCATION"))
        
        for edu in education:
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            dates = edu.get('dates', '')
            gpa = edu.get('gpa', '')
            achievements = edu.get('achievements', [])
            
            # Degree
            elements.append(Paragraph(f"<b>{degree}</b>", self.styles['JobTitle']))
            
            # Institution and dates
            data = [[institution, dates]]
            t = Table(data, colWidths=[4.5*inch, 2*inch])
            t.setStyle(TableStyle([
                ('FONT', (0, 0), (0, 0), 'Helvetica', 10),
                ('FONT', (1, 0), (1, 0), 'Helvetica-Oblique', 9),
                ('TEXTCOLOR', (0, 0), (0, 0), colors.HexColor('#444444')),
                ('TEXTCOLOR', (1, 0), (1, 0), colors.HexColor('#666666')),
                ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))
            elements.append(t)
            
            # GPA
            if gpa:
                elements.append(Paragraph(gpa, self.styles['Skill']))
            
            # Achievements
            for achievement in achievements:
                elements.append(Paragraph(f"• {achievement}", self.styles['Skill']))
            
            elements.append(Spacer(1, 0.08*inch))
        
        return elements
    
    def _create_certifications_section(self, certifications: List[str]) -> List:
        """Create certifications section."""
        elements = []
        
        elements.append(self._create_section_header("CERTIFICATIONS"))
        
        for cert in certifications:
            elements.append(Paragraph(f"• {cert}", self.styles['Skill']))
        
        return elements
    
    def _create_accomplishments_section(self, accomplishments: List[str]) -> List:
        """Create accomplishments section."""
        elements = []
        
        elements.append(self._create_section_header("ACCOMPLISHMENTS"))
        
        for accomp in accomplishments:
            elements.append(Paragraph(f"• {accomp}", self.styles['BulletPoint']))
        
        return elements


def generate_pdf_from_enhanced_content(
    enhanced_content: Dict[str, Any],
    output_path: str
) -> str:
    """
    Convenience function to generate PDF from enhanced content.
    
    Args:
        enhanced_content: Enhanced resume content
        output_path: Path to save PDF
        
    Returns:
        Path to generated PDF
    """
    generator = ResumePDFGenerator()
    return generator.generate_resume_pdf(enhanced_content, output_path)


if __name__ == "__main__":
    print("Resume PDF Generator - Ready to create professional PDFs!")
    print("Use generate_pdf_from_enhanced_content() to create a PDF.")
