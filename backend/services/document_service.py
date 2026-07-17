"""
Document Service Module
Handles document processing, chunking, embedding, and database operations
"""

import uuid
import asyncio
import tempfile
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from pathlib import Path

from sqlalchemy import func
from sqlalchemy.orm import Session
try:
    from llama_index.text_splitter import SemanticSplitterNodeParser
    _HAS_SEMANTIC_SPLITTER = True
except Exception:
    SemanticSplitterNodeParser = None
    _HAS_SEMANTIC_SPLITTER = False

try:
    from llama_index.core import Document as LlamaIndexDocument
except ImportError:
    from llama_index.core.schema import Document as LlamaIndexDocument
from llama_index.core.schema import TextNode

from models.database import Document, VectorStore
from services.embedding_service import EmbeddingService
from services.vector_store_service import VectorStoreService
from utils.logger import get_logger
from utils.pdf_extractor import PDFExtractor
from config.settings import settings

logger = get_logger(__name__)

MAX_DEVELOPMENT_PDF_PAGES = 10
MAX_DEVELOPMENT_PDF_PAGES_MESSAGE = "Dokumen melebihi batas maksimal pengembangan (Maksimal 10 Halaman)."
STRUCTURED_PARSER_PIPELINE_VERSION = "llamaparse_handoff_v2"


class DocumentPageLimitExceeded(ValueError):
    """Raised when an uploaded PDF exceeds the local development page limit."""


class DocumentService:
    """Service for handling document processing and vector embedding"""
    
    @staticmethod
    async def process_large_file(
        db: Session,
        pdf_bytes: bytes,
        file_name: str,
        user_id: str
    ) -> Dict:
        """
        Main entry point for processing large PDF files.
        Implements 3.5 Large File Modularization from PRD.
        
        Args:
            db: Database session
            pdf_bytes: Raw PDF file bytes
            file_name: Original file name
            user_id: User UUID
            
        Returns:
            Dictionary with processing results
        """
        process_start_time = datetime.utcnow()
        
        try:
            # Step 1: Calculate document hash for duplicate detection.
            document_hash = PDFExtractor.calculate_document_hash(pdf_bytes)
            logger.info(f"Document hash: {document_hash}")
            user_uuid = uuid.UUID(user_id)

            cached_document = db.query(Document).filter(
                Document.user_id == user_uuid,
                Document.file_hash == document_hash,
            ).first()
            if cached_document:
                chunk_count = db.query(func.count(VectorStore.id)).filter(
                    VectorStore.document_id == cached_document.id
                ).scalar() or 0
                module_count = db.query(func.count(func.distinct(VectorStore.module_chunk_id))).filter(
                    VectorStore.document_id == cached_document.id
                ).scalar() or 0
                first_cached_chunk = db.query(VectorStore.metadata_json).filter(
                    VectorStore.document_id == cached_document.id
                ).first()
                cached_metadata = (first_cached_chunk[0] if first_cached_chunk else {}) or {}
                cached_parser_version = cached_metadata.get("structured_parser_version")
                if chunk_count == 0:
                    logger.warning(f"Removing incomplete cached document record: {cached_document.id}")
                    db.delete(cached_document)
                    db.commit()
                elif cached_parser_version != STRUCTURED_PARSER_PIPELINE_VERSION:
                    logger.warning(
                        "Removing stale cached document record for structured parser reprocess: document_id=%s cached_parser_version=%s expected=%s",
                        cached_document.id,
                        cached_parser_version,
                        STRUCTURED_PARSER_PIPELINE_VERSION,
                    )
                    db.delete(cached_document)
                    db.commit()
                else:
                    process_end_time = datetime.utcnow()
                    processing_time = (process_end_time - process_start_time).total_seconds()

                    logger.info(f"Reusing cached document record: {cached_document.id}")
                    return {
                        "success": True,
                        "message": "Document already cached",
                        "document_id": str(cached_document.id),
                        "file_name": cached_document.file_name,
                        "total_pages": cached_document.total_pages,
                        "is_cached": True,
                        "total_modules": module_count,
                        "total_chunks": chunk_count,
                        "embedding_dimension": settings.vector_dimension,
                        "source_parser": cached_metadata.get("source_parser", "legacy_fallback"),
                        "parse_success": cached_metadata.get("source_parser") == "llamaparse",
                        "has_page_metadata": bool(cached_metadata.get("page_number") or cached_metadata.get("page_start")),
                        "structured_text_length": 0,
                        "parse_errors": [],
                        "processing_time_seconds": processing_time
                    }

            # Step 2: Extract full text and metadata
            logger.info("Extracting text from PDF...")
            full_text, total_pages = PDFExtractor.extract_all_text(pdf_bytes)
            logger.info(
                "pdf_extraction.result file_name=%s total_pages=%s text_length=%s preview=%s",
                file_name,
                total_pages,
                len(full_text or ""),
                (full_text or "")[:1000].replace("\n", "\\n"),
            )
            if total_pages > MAX_DEVELOPMENT_PDF_PAGES:
                db.rollback()
                raise DocumentPageLimitExceeded(MAX_DEVELOPMENT_PDF_PAGES_MESSAGE)
            
            # Step 3: Create document record in database
            doc_id = uuid.uuid4()
            document = Document(
                id=doc_id,
                user_id=user_uuid,
                file_name=file_name,
                file_hash=document_hash,
                total_pages=total_pages,
                is_cached=False,
                created_at=datetime.utcnow()
            )
            db.add(document)
            db.commit()
            logger.info(f"Created document record: {doc_id}")

            structured_parse = None
            structured_diagnostics = {
                "source_parser": "legacy_fallback",
                "parse_success": False,
                "page_count": total_pages,
                "structured_text_length": len(full_text or ""),
                "has_page_metadata": False,
                "parse_errors": ["Structured parser not executed"],
            }
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_pdf:
                tmp_pdf.write(pdf_bytes)
                tmp_pdf_path = tmp_pdf.name
            try:
                structured_parse = parse_pdf_with_llamaparse(tmp_pdf_path, str(doc_id))
                structured_diagnostics = structured_parse_diagnostics(structured_parse)
                save_structured_parse_result(structured_parse, str(doc_id))
                logger.info(
                    "structured_parse.handoff document_id=%s parser=%s success=%s raw_length=%s normalized_length=%s pages=%s preview=%s errors=%s",
                    doc_id,
                    structured_parse.get("parser"),
                    structured_parse.get("success"),
                    structured_parse.get("raw_response_length", 0),
                    len(str(structured_parse.get("full_text") or "")),
                    len(structured_parse.get("pages") or []),
                    str(structured_parse.get("full_text") or "")[:500].replace("\n", "\\n"),
                    structured_parse.get("errors") or [],
                )
                if structured_parse.get("full_text"):
                    full_text = structured_parse.get("full_text") or full_text
                    total_pages = max(total_pages, len(structured_parse.get("pages") or []))
                    document.total_pages = total_pages
                    db.add(document)
                    db.commit()
            finally:
                try:
                    Path(tmp_pdf_path).unlink(missing_ok=True)
                except Exception:
                    logger.warning("Could not remove temporary PDF path: %s", tmp_pdf_path)
            
            # Step 4: Split PDF into modules by page groups (3.5 Large File Modularization)
            logger.info(f"Splitting PDF into {settings.pdf_pages_per_module}-page modules...")
            modules = []
            if structured_parse and structured_parse.get("full_text"):
                modules = structured_pages_to_modules(
                    structured_parse,
                    pages_per_module=settings.pdf_pages_per_module,
                )
                logger.info(
                    "structured_modules.created document_id=%s module_count=%s source_parser=%s module_lengths=%s",
                    doc_id,
                    len(modules),
                    structured_diagnostics.get("source_parser"),
                    [len(str(module.get("content") or "")) for module in modules],
                )
                if not any(len(str(module.get("content") or "").strip()) >= 80 for module in modules):
                    logger.warning(
                        "structured_modules.too_short document_id=%s parser=%s falling_back_to_legacy",
                        doc_id,
                        structured_diagnostics.get("source_parser"),
                    )
                    structured_parse = None
                    structured_diagnostics = {
                        **structured_diagnostics,
                        "source_parser": "legacy_fallback",
                        "parse_success": False,
                        "parse_errors": [
                            *(structured_diagnostics.get("parse_errors") or []),
                            "Structured parser produced no usable module text",
                        ],
                    }
                    modules = []
            if not modules:
                logger.info("structured_modules.empty document_id=%s using legacy split_by_pages", doc_id)
                modules = PDFExtractor.split_by_pages(
                    pdf_bytes,
                    pages_per_module=settings.pdf_pages_per_module
                )
            
            # Step 5: Process each module asynchronously
            total_chunks = 0
            
            for module in modules:
                module_id = module["module_id"]
                module_content = module["content"]
                
                logger.info(f"Processing module {module_id}: Pages {module['start_page']}-{module['end_page']}")
                
                # Semantic text splitting
                if module.get("blocks") and structured_parse:
                    chunks = await DocumentService._semantic_chunk_structured_blocks(
                        module["blocks"],
                        source_parser=structured_diagnostics.get("source_parser") or "legacy_fallback",
                        chunk_size_tokens=settings.chunk_size_tokens,
                        overlap_percent=settings.chunk_overlap_percent,
                    )
                else:
                    chunks = await DocumentService._semantic_chunk_text(
                        module_content,
                        chunk_size_tokens=settings.chunk_size_tokens,
                        overlap_percent=settings.chunk_overlap_percent
                    )
                
                logger.info(f"Module {module_id} split into {len(chunks)} semantic chunks")
                logger.info(
                    "chunking.handoff document_id=%s module_id=%s parser=%s chunk_count=%s first_chunk_preview=%s",
                    doc_id,
                    module_id,
                    structured_diagnostics.get("source_parser"),
                    len(chunks),
                    (chunks[0].get("content", "") if chunks else "")[:500].replace("\n", "\\n"),
                )
                
                # Step 6: Generate embeddings for chunks
                chunk_embeddings = await EmbeddingService.embed_batch(
                    [chunk["content"] for chunk in chunks]
                )
                
                # Step 7: Prepare metadata for each chunk
                chunk_metadata_list = [
                    {
                        "document_id": str(doc_id),
                        "module_id": module_id,
                        "page_start": module["start_page"],
                        "page_end": module["end_page"],
                        "page_number": chunk.get("page_number") or module["start_page"],
                        "section_heading": chunk.get("section_heading") or "",
                        "block_type": chunk.get("block_type") or "unknown",
                        "source_parser": structured_diagnostics.get("source_parser") or "legacy_fallback",
                        "structured_parser_version": STRUCTURED_PARSER_PIPELINE_VERSION,
                        "chunk_index": idx,
                        "token_count": chunk.get("token_count", 0)
                    }
                    for idx, chunk in enumerate(chunks)
                ]
                
                # Step 8: Save chunks to vector store (batch operation)
                saved_count, chunk_ids = VectorStoreService.save_batch_chunks(
                    db=db,
                    document_id=str(doc_id),
                    module_chunk_id=module_id,
                    chunks=chunks,
                    embeddings=chunk_embeddings,
                    metadata_list=chunk_metadata_list
                )
                
                total_chunks += saved_count
                logger.info(f"Module {module_id}: Saved {saved_count} chunks to vector store")
            
            # Calculate processing time
            process_end_time = datetime.utcnow()
            processing_time = (process_end_time - process_start_time).total_seconds()
            
            logger.info(f"Document processing completed in {processing_time:.2f} seconds")
            
            return {
                "success": True,
                "message": "Document uploaded and processed successfully",
                "document_id": str(doc_id),
                "file_name": file_name,
                "total_pages": total_pages,
                "is_cached": False,
                "total_modules": len(modules),
                "total_chunks": total_chunks,
                "embedding_dimension": settings.vector_dimension,
                **structured_diagnostics,
                "processing_time_seconds": processing_time
            }
        
        except Exception as e:
            logger.error(f"Error processing large file: {e}")
            db.rollback()
            raise

    @staticmethod
    async def _semantic_chunk_structured_blocks(
        blocks: List[Dict],
        source_parser: str = "llamaparse",
        chunk_size_tokens: int = 512,
        overlap_percent: float = 0.10
    ) -> List[Dict]:
        aggregated_units: List[Dict] = []
        max_chars = max(800, int(chunk_size_tokens) * 4)
        current_parts: List[str] = []
        current_meta: Dict = {}

        def flush_current() -> None:
            nonlocal current_parts, current_meta
            content = "\n\n".join(part for part in current_parts if part.strip()).strip()
            if content:
                aggregated_units.append(
                    {
                        "content": content,
                        "page_number": current_meta.get("page_number"),
                        "section_heading": current_meta.get("section_heading") or "",
                        "block_type": current_meta.get("block_type") or "paragraph",
                    }
                )
            current_parts = []
            current_meta = {}

        for block in blocks:
            text = str(block.get("content") or "").strip()
            if not text:
                continue
            block_type = block.get("block_type") or "unknown"
            if len(text) < 24 and block_type not in {"title", "heading"}:
                continue
            block_page = block.get("page_number")
            block_heading = block.get("section_heading") or ""
            if (
                current_parts
                and (
                    block_page != current_meta.get("page_number")
                    or len("\n\n".join(current_parts)) + len(text) > max_chars
                )
            ):
                flush_current()
            if not current_parts:
                current_meta = {
                    "page_number": block_page,
                    "section_heading": block_heading,
                    "block_type": block_type,
                }
            current_parts.append(text)
        flush_current()

        if not aggregated_units:
            joined = "\n\n".join(str(block.get("content") or "").strip() for block in blocks if str(block.get("content") or "").strip())
            if joined.strip():
                aggregated_units.append(
                    {
                        "content": joined.strip(),
                        "page_number": blocks[0].get("page_number") if blocks else None,
                        "section_heading": blocks[0].get("section_heading") if blocks else "",
                        "block_type": "paragraph",
                    }
                )

        chunks: List[Dict] = []
        for unit in aggregated_units:
            unit_chunks = await DocumentService._semantic_chunk_text(
                unit["content"],
                chunk_size_tokens=chunk_size_tokens,
                overlap_percent=overlap_percent,
            )
            for chunk in unit_chunks:
                chunk["page_number"] = unit.get("page_number")
                chunk["section_heading"] = unit.get("section_heading") or ""
                chunk["block_type"] = unit.get("block_type") or "paragraph"
                chunk["source_parser"] = source_parser
                chunks.append(chunk)
        for index, chunk in enumerate(chunks):
            chunk["chunk_index"] = index
        return chunks
    
    @staticmethod
    async def _semantic_chunk_text(
        text: str,
        chunk_size_tokens: int = 512,
        overlap_percent: float = 0.10
    ) -> List[Dict]:
        """
        Split text using LlamaIndex Semantic Splitter.
        Implements 3.1 Advanced Chunking from PRD.
        
        Args:
            text: Full text to split
            chunk_size_tokens: Target chunk size (default: 512 tokens)
            overlap_percent: Overlap percentage (default: 10%)
            
        Returns:
            List of chunks with content and metadata
        """
        try:
            # Create LlamaIndex document
            llama_doc = LlamaIndexDocument(text=text)
            
            # Initialize semantic splitter if available, otherwise fallback
            if _HAS_SEMANTIC_SPLITTER and SemanticSplitterNodeParser is not None:
                splitter = SemanticSplitterNodeParser(
                    buffer_size=settings.chunk_size_tokens,
                    breakpoint_percentile_threshold=95,
                    paragraph_separator="\n\n",
                )

                # Split document into nodes
                nodes = splitter.get_nodes_from_documents([llama_doc])
            else:
                # Fallback: use simple character-based chunking
                logger.info("SemanticSplitterNodeParser not available; using simple chunking fallback")
                return DocumentService._simple_chunk_text(
                    text,
                    chunk_size_tokens=chunk_size_tokens,
                    overlap_percent=overlap_percent,
                )
            
            # Convert nodes to chunk format
            chunks = []
            for idx, node in enumerate(nodes):
                chunks.append({
                    "content": node.get_content(),
                    "token_count": node.metadata.get("token_count", 0) if node.metadata else 0,
                    "chunk_index": idx
                })
            
            logger.info(f"Semantic chunking created {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"Error semantic chunking text: {e}")
            # Fallback to simple chunking if semantic splitter fails
            logger.info("Falling back to simple character-based chunking")
            return DocumentService._simple_chunk_text(
                text,
                chunk_size_tokens=chunk_size_tokens,
                overlap_percent=overlap_percent
            )
    
    @staticmethod
    def _simple_chunk_text(
        text: str,
        chunk_size_tokens: int = 512,
        overlap_percent: float = 0.10
    ) -> List[Dict]:
        """
        Fallback simple chunking by character count.
        Approximates tokens (1 token ≈ 4 characters).
        
        Args:
            text: Full text to split
            chunk_size_tokens: Target chunk size in tokens
            overlap_percent: Overlap percentage
            
        Returns:
            List of chunks
        """
        try:
            char_per_token = 4
            chunk_size_chars = max(1, int(chunk_size_tokens) * char_per_token)
            safe_overlap_percent = max(0.0, min(float(overlap_percent), 0.9))
            overlap_chars = min(
                int(chunk_size_chars * safe_overlap_percent),
                chunk_size_chars - 1,
            )
            min_advance = max(1, chunk_size_chars - overlap_chars)
            
            chunks = []
            start = 0
            chunk_idx = 0
            text_length = len(text)
            
            while start < text_length:
                end = min(start + chunk_size_chars, text_length)
                
                # Try to break at sentence boundary
                if end < text_length:
                    last_period = text.rfind(".", start + 1, end)
                    if last_period != -1:
                        end = last_period + 1
                
                chunk_text = text[start:end].strip()
                if chunk_text:
                    chunks.append({
                        "content": chunk_text,
                        "token_count": len(chunk_text) // char_per_token,
                        "chunk_index": chunk_idx
                    })
                    chunk_idx += 1

                if end >= text_length:
                    break

                next_start = max(end - overlap_chars, start + min_advance)
                if next_start <= start:
                    next_start = start + min_advance
                start = min(next_start, text_length)
            
            logger.info(f"Simple chunking created {len(chunks)} chunks")
            return chunks
        
        except Exception as e:
            logger.error(f"Error in simple chunking: {e}")
            raise
    
    @staticmethod
    def get_document_info(db: Session, document_id: str) -> Optional[Dict]:
        """
        Retrieve document information including chunk count.
        
        Args:
            db: Database session
            document_id: Document UUID
            
        Returns:
            Dictionary with document info, or None if not found
        """
        try:
            doc_id = uuid.UUID(document_id)
            document = db.query(Document).filter(Document.id == doc_id).first()
            
            if not document:
                return None
            
            chunk_count = db.query(VectorStore).filter(
                VectorStore.document_id == doc_id
            ).count()
            
            return {
                "id": str(document.id),
                "file_name": document.file_name,
                "total_pages": document.total_pages,
                "total_chunks": chunk_count,
                "is_cached": document.is_cached,
                "created_at": document.created_at
            }
        
        except Exception as e:
            logger.error(f"Error retrieving document info: {e}")
            raise
