"""
PDF Extraction Utility Module
Handles PDF text extraction and document splitting
"""

import io
import hashlib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from PyPDF2 import PdfReader
from utils.logger import get_logger

logger = get_logger(__name__)

MIN_EXTRACTED_TEXT_ALNUM_CHARS = 24


class PDFTextExtractionFailed(ValueError):
    """Raised when both native extraction and OCR fallback fail."""


class PDFExtractor:
    """Utility class for extracting text from PDF files."""

    @staticmethod
    def _find_tesseract_executable() -> Optional[str]:
        candidates = [
            shutil.which("tesseract"),
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for candidate in candidates:
            if candidate and Path(candidate).exists():
                return str(candidate)
        return None

    @staticmethod
    def _find_ghostscript_executable() -> Optional[str]:
        direct_candidates = [
            shutil.which("gswin64c"),
            shutil.which("gswin32c"),
            shutil.which("gs"),
        ]
        for candidate in direct_candidates:
            if candidate and Path(candidate).exists():
                return str(candidate)

        program_files_roots = [
            Path(r"C:\Program Files\gs"),
            Path(r"C:\Program Files (x86)\gs"),
        ]
        for root in program_files_roots:
            if not root.exists():
                continue
            matches = sorted(root.glob(r"*\bin\gswin64c.exe"), reverse=True)
            if matches:
                return str(matches[0])
            matches = sorted(root.glob(r"*\bin\gswin32c.exe"), reverse=True)
            if matches:
                return str(matches[0])
        return None
    
    @staticmethod
    def calculate_document_hash(pdf_bytes: bytes) -> str:
        """
        Calculate SHA-256 hash of PDF document.
        Used for detecting duplicate documents.
        
        Args:
            pdf_bytes: Raw PDF file bytes
            
        Returns:
            Hexadecimal hash string
        """
        try:
            sha256_hash = hashlib.sha256()
            sha256_hash.update(pdf_bytes)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating document hash: {e}")
            raise
    
    @staticmethod
    def extract_all_text(pdf_bytes: bytes) -> Tuple[str, int]:
        """
        Extract all text from PDF file.
        
        Args:
            pdf_bytes: Raw PDF file bytes
            
        Returns:
            Tuple of (extracted_text, total_pages)
            
        Raises:
            ValueError: If PDF is invalid or empty
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PdfReader(pdf_file)
            
            total_pages = len(pdf_reader.pages)
            if total_pages == 0:
                raise ValueError("PDF contains no pages")
            
            native_page_texts = PDFExtractor._extract_native_page_texts(pdf_reader)
            full_text = PDFExtractor._combine_page_texts(native_page_texts)
            
            if PDFExtractor._is_text_sufficient(full_text):
                logger.info(f"Successfully extracted text from {total_pages} pages")
                return full_text, total_pages

            logger.info("Native PDF text extraction was empty or near-empty; attempting OCR fallback")
            ocr_page_texts = PDFExtractor._extract_page_texts_with_ocr(pdf_bytes, total_pages=total_pages)
            ocr_text = PDFExtractor._combine_page_texts(ocr_page_texts)
            if PDFExtractor._is_text_sufficient(ocr_text):
                logger.info(f"OCR fallback extracted text from {total_pages} pages")
                return ocr_text, total_pages
            
            raise PDFTextExtractionFailed("No text content extracted from PDF")
        
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            raise

    @staticmethod
    def _is_text_sufficient(text: str) -> bool:
        alnum_chars = len(re.findall(r"[A-Za-z0-9]", text or ""))
        return bool(text and text.strip() and alnum_chars >= MIN_EXTRACTED_TEXT_ALNUM_CHARS)

    @staticmethod
    def _extract_native_page_texts(pdf_reader: PdfReader) -> List[str]:
        page_texts: List[str] = []
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_texts.append((page.extract_text() or "").strip())
            except Exception as e:
                logger.warning(f"Error extracting text from page {page_num + 1}: {e}")
                page_texts.append("")
        return page_texts

    @staticmethod
    def _combine_page_texts(page_texts: List[str]) -> str:
        combined_parts: List[str] = []
        for page_index, page_text in enumerate(page_texts, start=1):
            if page_text:
                combined_parts.append(f"\n[Page {page_index}]\n{page_text}\n")
        return "".join(combined_parts)

    @staticmethod
    def _extract_page_texts_with_ocr(pdf_bytes: bytes, total_pages: int = 0) -> List[str]:
        tesseract_exe = PDFExtractor._find_tesseract_executable()
        gs_exe = PDFExtractor._find_ghostscript_executable()
        if not tesseract_exe or not gs_exe:
            logger.warning(
                "OCR fallback unavailable (tesseract=%s, ghostscript=%s)",
                bool(tesseract_exe),
                bool(gs_exe),
            )
            return []

        with tempfile.TemporaryDirectory(prefix="pdf-ocr-") as tmp_dir:
            tmp_path = Path(tmp_dir)
            pdf_path = tmp_path / "input.pdf"
            pdf_path.write_bytes(pdf_bytes)
            output_pattern = tmp_path / "page-%03d.png"

            render_cmd = [
                gs_exe,
                "-dSAFER",
                "-dBATCH",
                "-dNOPAUSE",
                "-sDEVICE=png16m",
                "-r200",
                f"-sOutputFile={output_pattern}",
                str(pdf_path),
            ]
            render_result = subprocess.run(
                render_cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                check=False,
            )
            if render_result.returncode != 0:
                logger.warning("Ghostscript OCR render failed: %s", render_result.stderr[:1000] or render_result.stdout[:1000])
                return []

            image_paths = sorted(tmp_path.glob("page-*.png"))
            if not image_paths:
                logger.warning("OCR fallback rendered no page images")
                return []

            page_texts: List[str] = []
            for page_index, image_path in enumerate(image_paths, start=1):
                ocr_cmd = [tesseract_exe, str(image_path), "stdout", "--psm", "6"]
                ocr_result = subprocess.run(
                    ocr_cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="ignore",
                    check=False,
                )
                if ocr_result.returncode != 0:
                    logger.warning("Tesseract OCR failed on page %s: %s", page_index, ocr_result.stderr[:500])
                    page_texts.append("")
                    continue
                page_text = (ocr_result.stdout or "").strip()
                page_texts.append(page_text)

            combined = PDFExtractor._combine_page_texts(page_texts)
            logger.info(
                "OCR fallback completed (rendered_pages=%s, text_pages=%s, text_length=%s, expected_pages=%s)",
                len(image_paths),
                sum(1 for page_text in page_texts if page_text),
                len(combined),
                total_pages,
            )
            return page_texts
    
    @staticmethod
    def split_by_pages(pdf_bytes: bytes, pages_per_module: int = 5) -> List[Dict[str, any]]:
        """
        Split PDF into modules based on page groups.
        Used for large file modularization.
        
        Args:
            pdf_bytes: Raw PDF file bytes
            pages_per_module: Number of pages per module (default: 5)
            
        Returns:
            List of dictionaries containing module info and text
            
        Raises:
            ValueError: If PDF is invalid
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PdfReader(pdf_file)
            total_pages = len(pdf_reader.pages)
            
            if total_pages == 0:
                raise ValueError("PDF contains no pages")

            page_texts = PDFExtractor._extract_native_page_texts(pdf_reader)
            if not PDFExtractor._is_text_sufficient(PDFExtractor._combine_page_texts(page_texts)):
                logger.info("Native page splitting produced empty or near-empty text; attempting OCR fallback for modules")
                ocr_page_texts = PDFExtractor._extract_page_texts_with_ocr(pdf_bytes, total_pages=total_pages)
                if PDFExtractor._is_text_sufficient(PDFExtractor._combine_page_texts(ocr_page_texts)):
                    page_texts = ocr_page_texts
            
            modules = []
            current_module = 0
            module_text = ""
            start_page = 1
            
            for page_num, page_text in enumerate(page_texts):
                if page_text:
                    module_text += f"\n[Page {page_num + 1}]\n{page_text}\n"
                
                # Check if module is complete
                if (page_num + 1) % pages_per_module == 0 or page_num + 1 == total_pages:
                    end_page = page_num + 1
                    
                    if module_text.strip():
                        modules.append({
                            "module_id": current_module,
                            "start_page": start_page,
                            "end_page": end_page,
                            "content": module_text.strip()
                        })
                        logger.info(f"Module {current_module}: Pages {start_page}-{end_page}")
                    
                    current_module += 1
                    module_text = ""
                    start_page = end_page + 1
            
            logger.info(f"Split PDF into {len(modules)} modules")
            return modules
        
        except Exception as e:
            logger.error(f"Error splitting PDF by pages: {e}")
            raise
    
    @staticmethod
    def get_pdf_metadata(pdf_bytes: bytes) -> Dict[str, any]:
        """
        Extract metadata from PDF (title, author, creation date, etc).
        
        Args:
            pdf_bytes: Raw PDF file bytes
            
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            pdf_reader = PdfReader(pdf_file)
            
            metadata = pdf_reader.metadata or {}
            return {
                "title": metadata.get("/Title", "Unknown"),
                "author": metadata.get("/Author", "Unknown"),
                "creation_date": metadata.get("/CreationDate", "Unknown"),
                "total_pages": len(pdf_reader.pages)
            }
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            return {
                "title": "Unknown",
                "author": "Unknown",
                "creation_date": "Unknown",
                "total_pages": 0
            }
