"""
Vector Store Service Module
Handles storage and retrieval of vector embeddings from Supabase
"""

from typing import List, Dict, Optional, Tuple
import uuid
from datetime import datetime

from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
import json
import math

from models.database import VectorStore
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class VectorStoreService:
    """Service for managing vector store operations in Supabase"""

    @staticmethod
    def _validate_embedding_dimension(embedding_vector: List[float]) -> None:
        expected = settings.vector_dimension if settings else 1536
        if len(embedding_vector) != expected:
            raise ValueError(f"Embedding vector must have {expected} dimensions, got {len(embedding_vector)}")

    @staticmethod
    def _to_pgvector_literal(embedding_vector: List[float]) -> str:
        VectorStoreService._validate_embedding_dimension(embedding_vector)
        return "[" + ",".join(str(float(item)) for item in embedding_vector) + "]"

    @staticmethod
    def _deserialize_embedding(raw_embedding) -> List[float]:
        if isinstance(raw_embedding, list):
            return raw_embedding
        if isinstance(raw_embedding, str):
            return json.loads(raw_embedding)
        return list(raw_embedding)

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        if not a or not b:
            return 0.0
        limit = min(len(a), len(b))
        dot = sum(a[i] * b[i] for i in range(limit))
        norm_a = math.sqrt(sum(a[i] * a[i] for i in range(limit)))
        norm_b = math.sqrt(sum(b[i] * b[i] for i in range(limit)))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
    
    @staticmethod
    def save_chunk(
        db: Session,
        document_id: str,
        module_chunk_id: int,
        chunk_index: int,
        chunk_content: str,
        embedding_vector: List[float],
        metadata: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Save a text chunk with embedding to vector store.
        
        Args:
            db: Database session
            document_id: Parent document UUID
            module_chunk_id: Module sequence identifier
            chunk_index: Index within module
            chunk_content: Text content of chunk
            embedding_vector: Embedding vector (1536-dim)
            metadata: Optional metadata (page numbers, token count, etc.)
            
        Returns:
            UUID of saved chunk, or None if failed
        """
        try:
            VectorStoreService._validate_embedding_dimension(embedding_vector)
            if db.bind is not None and db.bind.dialect.name == "sqlite":
                _, chunk_ids = VectorStoreService.save_batch_chunks(
                    db=db,
                    document_id=document_id,
                    module_chunk_id=module_chunk_id,
                    chunks=[{"content": chunk_content, "chunk_index": chunk_index}],
                    embeddings=[embedding_vector],
                    metadata_list=[metadata or {}],
                )
                return chunk_ids[0] if chunk_ids else None

            vector_chunk = VectorStore(
                id=uuid.uuid4(),
                document_id=uuid.UUID(document_id),
                module_chunk_id=module_chunk_id,
                chunk_content=chunk_content,
                embedding_vector=embedding_vector,
                metadata_json=metadata or {},
            )
            
            db.add(vector_chunk)
            db.commit()
            
            logger.debug(f"Saved chunk {module_chunk_id}_{chunk_index} to vector store")
            return str(vector_chunk.id)
        
        except Exception as e:
            logger.error(f"Error saving chunk to vector store: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def save_batch_chunks(
        db: Session,
        document_id: str,
        module_chunk_id: int,
        chunks: List[Dict],
        embeddings: List[List[float]],
        metadata_list: Optional[List[Dict]] = None
    ) -> Tuple[int, List[str]]:
        """
        Save multiple chunks in a single transaction.
        
        Args:
            db: Database session
            document_id: Parent document UUID
            module_chunk_id: Module sequence identifier
            chunks: List of chunk dictionaries with 'content' key
            embeddings: List of embedding vectors
            metadata_list: Optional list of metadata dicts
            
        Returns:
            Tuple of (total_saved_count, list_of_chunk_ids)
        """
        try:
            if len(chunks) != len(embeddings):
                raise ValueError("Number of chunks must match number of embeddings")
            
            chunk_ids = []
            doc_id = uuid.UUID(document_id)

            if db.bind is not None and db.bind.dialect.name == "sqlite":
                table_columns = {column["name"] for column in inspect(db.bind).get_columns("vector_store")}
                for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                    VectorStoreService._validate_embedding_dimension(embedding)
                    metadata = metadata_list[idx] if metadata_list else {}
                    chunk_id = uuid.uuid4()
                    row = {
                        "id": str(chunk_id),
                        "document_id": str(doc_id),
                        "module_chunk_id": module_chunk_id,
                        "chunk_content": chunk.get("content", ""),
                        "embedding_vector": json.dumps(embedding),
                    }

                    if "metadata" in table_columns:
                        row["metadata"] = json.dumps(metadata or {})
                    if "metadata_json" in table_columns:
                        row["metadata_json"] = json.dumps(metadata or {})
                    if "chunk_index" in table_columns:
                        row["chunk_index"] = chunk.get("chunk_index", idx)
                    if "created_at" in table_columns:
                        row["created_at"] = datetime.utcnow()

                    columns = [column for column in row if column in table_columns]
                    placeholders = [f":{column}" for column in columns]
                    db.execute(
                        text(
                            f"INSERT INTO vector_store ({', '.join(columns)}) "
                            f"VALUES ({', '.join(placeholders)})"
                        ),
                        {column: row[column] for column in columns},
                    )
                    chunk_ids.append(str(chunk_id))

                db.commit()
                logger.info(f"Saved {len(chunk_ids)} chunks to SQLite vector store")
                return len(chunk_ids), chunk_ids
            
            for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                VectorStoreService._validate_embedding_dimension(embedding)
                metadata = metadata_list[idx] if metadata_list else None
                
                vector_chunk = VectorStore(
                    id=uuid.uuid4(),
                    document_id=doc_id,
                    module_chunk_id=module_chunk_id,
                    chunk_content=chunk.get("content", ""),
                    embedding_vector=embedding,
                    metadata_json=metadata or {},
                )
                
                db.add(vector_chunk)
                chunk_ids.append(str(vector_chunk.id))
            
            db.commit()
            logger.info(f"Saved {len(chunk_ids)} chunks to vector store")
            return len(chunk_ids), chunk_ids
        
        except Exception as e:
            logger.error(f"Error saving batch chunks to vector store: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def get_chunks_by_document(db: Session, document_id: str) -> List[VectorStore]:
        """
        Retrieve all chunks for a document.
        
        Args:
            db: Database session
            document_id: Document UUID
            
        Returns:
            List of VectorStore chunks
        """
        try:
            doc_id = uuid.UUID(document_id)
            chunks = db.query(VectorStore).filter(
                VectorStore.document_id == doc_id
            ).all()
            
            logger.info(f"Retrieved {len(chunks)} chunks for document {document_id}")
            return chunks
        
        except Exception as e:
            logger.error(f"Error retrieving chunks from vector store: {e}")
            raise
    
    @staticmethod
    def get_chunk_count_for_document(db: Session, document_id: str) -> int:
        """
        Get total number of chunks for a document.
        
        Args:
            db: Database session
            document_id: Document UUID
            
        Returns:
            Total chunk count
        """
        try:
            doc_id = uuid.UUID(document_id)
            count = db.query(VectorStore).filter(
                VectorStore.document_id == doc_id
            ).count()
            
            return count
        
        except Exception as e:
            logger.error(f"Error counting chunks for document: {e}")
            raise
    
    @staticmethod
    def delete_chunks_for_document(db: Session, document_id: str) -> int:
        """
        Delete all chunks associated with a document.
        
        Args:
            db: Database session
            document_id: Document UUID
            
        Returns:
            Number of chunks deleted
        """
        try:
            doc_id = uuid.UUID(document_id)
            count = db.query(VectorStore).filter(
                VectorStore.document_id == doc_id
            ).delete()
            
            db.commit()
            logger.info(f"Deleted {count} chunks for document {document_id}")
            return count
        
        except Exception as e:
            logger.error(f"Error deleting chunks from vector store: {e}")
            db.rollback()
            raise
    
    @staticmethod
    def vector_similarity_search(
        db: Session,
        query_vector: List[float],
        top_k: int = 3,
        document_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Perform vector similarity search using pgvector.
        
        Args:
            db: Database session
            query_vector: Query embedding vector
            top_k: Number of top results to return
            document_id: Optional filter by document
            
        Returns:
            List of similar chunks with similarity scores
        """
        try:
            VectorStoreService._validate_embedding_dimension(query_vector)
            dialect_name = db.bind.dialect.name if db.bind is not None else ""

            if dialect_name == "sqlite":
                if document_id:
                    doc_id = uuid.UUID(document_id)
                    rows = db.query(
                        VectorStore.id,
                        VectorStore.document_id,
                        VectorStore.module_chunk_id,
                        VectorStore.chunk_content,
                        VectorStore.embedding_vector,
                        VectorStore.metadata_json,
                    ).filter(VectorStore.document_id == doc_id).all()
                else:
                    rows = db.query(
                        VectorStore.id,
                        VectorStore.document_id,
                        VectorStore.module_chunk_id,
                        VectorStore.chunk_content,
                        VectorStore.embedding_vector,
                        VectorStore.metadata_json,
                    ).all()

                scored = []
                for row in rows:
                    embedding = VectorStoreService._deserialize_embedding(row.embedding_vector)
                    scored.append((VectorStoreService._cosine_similarity(query_vector, embedding), row))

                scored.sort(key=lambda item: item[0], reverse=True)

                return [
                    {
                        "chunk_id": str(row.id),
                        "document_id": str(row.document_id),
                        "content": row.chunk_content,
                        "module_chunk_id": row.module_chunk_id,
                        "module_id": row.module_chunk_id,
                        "metadata": row.metadata_json or {},
                        "similarity_score": float(score),
                    }
                    for score, row in scored[:top_k]
                ]

            params = {
                "query_vector": VectorStoreService._to_pgvector_literal(query_vector),
                "limit": int(top_k),
            }
            where_clause = ""
            if document_id:
                params["document_id"] = str(uuid.UUID(document_id))
                where_clause = "WHERE document_id = CAST(:document_id AS uuid)"

            sql = text(
                f"""
                SELECT
                    id,
                    document_id,
                    module_chunk_id,
                    chunk_content,
                    metadata,
                    1 - (embedding_vector <=> CAST(:query_vector AS vector)) AS similarity_score
                FROM vector_store
                {where_clause}
                ORDER BY embedding_vector <=> CAST(:query_vector AS vector)
                LIMIT :limit
                """
            )
            results = db.execute(sql, params).mappings().all()

            output = []
            for result in results:
                output.append({
                    "chunk_id": str(result.id),
                    "document_id": str(result.document_id),
                    "content": result.chunk_content,
                    "module_chunk_id": result.module_chunk_id,
                    "module_id": result.module_chunk_id,
                    "metadata": result.metadata,
                    "similarity_score": float(result.similarity_score),
                })
            
            logger.debug(f"Found {len(output)} similar chunks")
            return output
        
        except Exception as e:
            logger.error(f"Error performing vector similarity search: {e}")
            raise
