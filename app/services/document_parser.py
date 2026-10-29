import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import pymupdf  # PyMuPDF
import docx

class DocumentParsingError(Exception):
    """Custom exception raised when document parsing fails."""
    pass

class DocumentParser:
    """
    Extracts and organizes text from PDF and DOCX resume files.
    Identifies common resume sections, contact information, and bullet points.
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".docx"}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    # Regex patterns for contact information
    EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    PHONE_PATTERN = re.compile(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}')
    LINKEDIN_PATTERN = re.compile(r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/in\/[a-zA-Z0-9_-]+', re.IGNORECASE)
    GITHUB_PATTERN = re.compile(r'(?:https?:\/\/)?(?:www\.)?github\.com\/[a-zA-Z0-9_-]+', re.IGNORECASE)

    # Standard section heading keywords
    SECTION_KEYWORDS = {
        "education": ["education", "academic background", "qualifications", "academics"],
        "experience": ["work experience", "professional experience", "experience", "employment history", "work history"],
        "projects": ["projects", "personal projects", "academic projects", "key projects"],
        "skills": ["skills", "technical skills", "core competencies", "skills & abilities", "technologies"],
        "certifications": ["certifications", "licenses", "certificates", "courses"],
        "achievements": ["achievements", "awards", "honors", "accomplishments", "publications"]
    }

    @classmethod
    def validate_file(cls, filepath: str) -> None:
        """Validates file existence, extension, and size."""
        path = Path(filepath)
        if not path.exists():
            raise DocumentParsingError(f"File not found: {path.name}")
        
        if path.suffix.lower() not in cls.SUPPORTED_EXTENSIONS:
            raise DocumentParsingError(
                f"Unsupported format '{path.suffix}'. Please upload a PDF (.pdf) or Word document (.docx)."
            )

        file_size = path.stat().st_size
        if file_size == 0:
            raise DocumentParsingError("Uploaded file is empty (0 bytes). Please upload a valid resume.")
        if file_size > cls.MAX_FILE_SIZE:
            raise DocumentParsingError(
                f"File size ({file_size / (1024*1024):.1f}MB) exceeds the 5MB limit."
            )

    @classmethod
    def extract_text_from_pdf(cls, filepath: str) -> Dict[str, Any]:
        """Extracts text, metadata, and page count from a PDF using PyMuPDF."""
        try:
            doc = pymupdf.open(filepath)
            page_count = len(doc)
            pages_text = []

            for page_num in range(page_count):
                page = doc[page_num]
                text = page.get_text("text")
                if text:
                    pages_text.append(text)
            
            doc.close()
            full_text = "\n".join(pages_text).strip()

            if not full_text:
                raise DocumentParsingError(
                    "No readable text could be extracted from this PDF. "
                    "The file might be scanned, image-only, or encrypted without selectable text."
                )

            return {
                "text": full_text,
                "page_count": page_count,
                "format": "pdf"
            }
        except DocumentParsingError:
            raise
        except Exception as e:
            raise DocumentParsingError(f"PyMuPDF error reading PDF: {str(e)}")

    @classmethod
    def extract_text_from_docx(cls, filepath: str) -> Dict[str, Any]:
        """Extracts text from a DOCX file using python-docx."""
        try:
            doc = docx.Document(filepath)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            
            # Also extract text from tables
            table_text = []
            for table in doc.tables:
                for row in table.rows:
                    row_data = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_data:
                        table_text.append(" | ".join(row_data))
            
            full_text = "\n".join(paragraphs + table_text).strip()

            if not full_text:
                raise DocumentParsingError("No readable text could be extracted from this DOCX document.")

            return {
                "text": full_text,
                "page_count": max(1, len(paragraphs) // 30),  # Approximate page count
                "format": "docx"
            }
        except DocumentParsingError:
            raise
        except Exception as e:
            raise DocumentParsingError(f"python-docx error reading DOCX: {str(e)}")

    @classmethod
    def parse_document(cls, filepath: str) -> Dict[str, Any]:
        """
        Main entry point for document parsing.
        Returns extracted text, detected sections, contact info, and bullet points.
        """
        cls.validate_file(filepath)
        path = Path(filepath)

        if path.suffix.lower() == ".pdf":
            extraction = cls.extract_text_from_pdf(filepath)
        elif path.suffix.lower() == ".docx":
            extraction = cls.extract_text_from_docx(filepath)
        else:
            raise DocumentParsingError(f"Unsupported file format: {path.suffix}")

        raw_text = extraction["text"]
        contact_info = cls.extract_contact_info(raw_text)
        sections = cls.segment_sections(raw_text)
        bullet_points = cls.extract_bullet_points(raw_text)
        words = re.findall(r'\b\w+\b', raw_text)

        # Estimate candidate name (usually top line before email/phone)
        candidate_name = cls.estimate_candidate_name(raw_text, contact_info)

        return {
            "filename": path.name,
            "format": extraction["format"],
            "page_count": extraction["page_count"],
            "word_count": len(words),
            "char_count": len(raw_text),
            "raw_text": raw_text,
            "candidate_name": candidate_name,
            "contact_info": contact_info,
            "sections": sections,
            "bullet_points": bullet_points
        }

    @classmethod
    def extract_contact_info(cls, text: str) -> Dict[str, Any]:
        """Extracts emails, phone numbers, and professional links."""
        emails = cls.EMAIL_PATTERN.findall(text)
        phones = cls.PHONE_PATTERN.findall(text)
        linkedin = cls.LINKEDIN_PATTERN.findall(text)
        github = cls.GITHUB_PATTERN.findall(text)

        return {
            "email": emails[0] if emails else None,
            "phone": phones[0] if phones else None,
            "linkedin": linkedin[0] if linkedin else None,
            "github": github[0] if github else None,
            "has_email": bool(emails),
            "has_phone": bool(phones),
            "has_linkedin": bool(linkedin),
            "has_github": bool(github)
        }

    @classmethod
    def estimate_candidate_name(cls, text: str, contact_info: Dict[str, Any]) -> str:
        """Guesses candidate name from the first few non-empty lines."""
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:5]:
            # Skip if line contains email or phone
            if contact_info.get("email") and contact_info["email"] in line:
                continue
            if len(line.split()) in (2, 3, 4) and not any(kw in line.lower() for kws in cls.SECTION_KEYWORDS.values() for kw in kws):
                # Clean up any non-alphabetic characters
                cleaned = re.sub(r'[^a-zA-Z\s\.]', '', line).strip()
                if 2 <= len(cleaned.split()) <= 4:
                    return cleaned
        return "Candidate"

    @classmethod
    def segment_sections(cls, text: str) -> Dict[str, str]:
        """
        Segments the text into standard resume sections based on heading keywords.
        """
        sections: Dict[str, List[str]] = {
            "education": [],
            "experience": [],
            "projects": [],
            "skills": [],
            "certifications": [],
            "achievements": [],
            "general": []
        }

        current_section = "general"
        lines = text.split("\n")

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            # Check if this line is likely a section header
            lower_line = trimmed.lower()
            detected_heading = None
            
            # Typical headers are short (< 35 chars)
            if len(trimmed) < 40:
                for section_name, keywords in cls.SECTION_KEYWORDS.items():
                    if any(kw == lower_line or lower_line.startswith(kw + ":") for kw in keywords):
                        detected_heading = section_name
                        break

            if detected_heading:
                current_section = detected_heading
            else:
                sections[current_section].append(trimmed)

        # Convert line lists to string blocks
        return {sec: "\n".join(lines).strip() for sec, lines in sections.items() if lines}

    @classmethod
    def extract_bullet_points(cls, text: str) -> List[Dict[str, Any]]:
        """
        Finds actionable bullet points (lines starting with bullets, dashes, asterisks, or action verbs).
        """
        bullet_markers = re.compile(r'^[\s]*[•\-\*\u2022\u2023\u25E6\u2043\u2219]\s*')
        lines = text.split("\n")
        extracted_bullets = []
        
        index = 0
        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue
            
            is_bullet = bool(bullet_markers.match(trimmed))
            cleaned_text = bullet_markers.sub("", trimmed).strip()

            # We consider lines with sufficient detail (> 25 characters, < 300 characters) as potential bullets
            if (is_bullet or (len(cleaned_text.split()) >= 6 and not cleaned_text.endswith(":"))) and len(cleaned_text) > 25:
                index += 1
                extracted_bullets.append({
                    "id": f"bp_{index}",
                    "text": cleaned_text,
                    "word_count": len(cleaned_text.split()),
                    "is_explicit_bullet": is_bullet
                })

        return extracted_bullets
