import pytest
from pathlib import Path
from app.services.document_parser import DocumentParser, DocumentParsingError

def test_extract_pdf_success(sample_pdf_path):
    result = DocumentParser.parse_document(sample_pdf_path)
    assert result["format"] == "pdf"
    assert "Alex Chen" in result["raw_text"]
    assert result["word_count"] > 100
    assert result["contact_info"]["email"] == "alex.chen@example.com"
    assert result["contact_info"]["has_phone"] is True
    assert result["contact_info"]["has_linkedin"] is True
    assert result["candidate_name"] == "Alex Chen"
    assert "experience" in result["sections"]
    assert "education" in result["sections"]
    assert len(result["bullet_points"]) >= 3

def test_extract_docx_success(sample_docx_path):
    result = DocumentParser.parse_document(sample_docx_path)
    assert result["format"] == "docx"
    assert "Sarah Miller" in result["raw_text"]
    assert result["contact_info"]["email"] == "sarah.miller@example.org"
    assert result["contact_info"]["has_github"] is True
    assert "skills" in result["sections"]
    assert len(result["bullet_points"]) >= 2

def test_empty_file_rejected(tmp_path):
    empty_file = tmp_path / "empty_resume.pdf"
    empty_file.write_bytes(b"")
    
    with pytest.raises(DocumentParsingError, match="empty"):
        DocumentParser.parse_document(str(empty_file))

def test_unsupported_format_rejected(tmp_path):
    txt_file = tmp_path / "resume.txt"
    txt_file.write_text("Hello world")
    
    with pytest.raises(DocumentParsingError, match="Unsupported format"):
        DocumentParser.parse_document(str(txt_file))

def test_nonexistent_file_rejected():
    with pytest.raises(DocumentParsingError, match="File not found"):
        DocumentParser.parse_document("non_existent_file.pdf")
