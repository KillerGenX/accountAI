import os
import uuid
import pypdf
import litellm
import structlog
from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.core.database import get_db
from src.core.auth import get_current_user
from src.domains.account.models import (
    AccountModel,
    AccountDocumentModel,
    AccountDocumentChunkModel,
    AccountEmbeddingModel,
    AccountNoteModel,
)
from src.domains.account.embeddings import embedding_client
from src.domains.account.schemas import (
    DocumentResponse,
    RagQueryRequest,
    RagQueryResponse,
    RagCitation,
)

logger = structlog.get_logger()
router = APIRouter(tags=["Documents"])

# Max allowed upload size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 150) -> List[str]:
    """
    Slices text into overlapping semantical segments.
    """
    chunks = []
    if not text:
        return chunks
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += chunk_size - overlap
    return chunks


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    account_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Uploads a corporate PDF document, parses its text content, chunks it,
    and indexes the vector representations (embeddings) in pgvector database.
    """
    workspace_id = UUID(current_user["workspace_id"])
    await logger.ainfo(
        "pdf_upload_requested",
        filename=file.filename,
        account_id=str(account_id),
        workspace_id=str(workspace_id),
    )

    # 1. Verify account exists in workspace
    acc_res = await db.execute(
        select(AccountModel).where(
            AccountModel.id == account_id,
            AccountModel.workspace_id == workspace_id,
            AccountModel.deleted_at.is_(None),
        )
    )
    account = acc_res.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found in your workspace",
        )

    # 2. Validate PDF format
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF documents are allowed",
        )

    # 3. Create Storage Dir and Save Physical File
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    storage_dir = os.path.join(root_dir, "storage", "documents")
    os.makedirs(storage_dir, exist_ok=True)

    unique_filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join(storage_dir, unique_filename)

    # Read content to check file size and save
    content = await file.read()
    file_size = len(content)
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 10MB limit",
        )

    try:
        with open(file_path, "wb") as f:
            f.write(content)
    except Exception as e:
        await logger.aerror("file_write_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to write document file to storage disk",
        )

    # 4. Extract text from PDF using pypdf
    extracted_text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
    except Exception as e:
        # Cleanup file if parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        await logger.aerror("pdf_parsing_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to parse text from the uploaded PDF document",
        )

    if not extracted_text.strip():
        # Cleanup
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF contains no readable text content (image-only/scanned PDFs are not supported)",
        )

    # 5. Insert Document metadata into Database
    new_doc = AccountDocumentModel(
        workspace_id=workspace_id,
        account_id=account_id,
        filename=file.filename,
        file_size=file_size,
        file_path=unique_filename,
    )
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)

    # 6. Chunk text and generate vector embeddings
    chunks = chunk_text(extracted_text)
    await logger.ainfo("text_chunking_completed", chunks_count=len(chunks))

    try:
        for idx, chunk in enumerate(chunks):
            # 6a. Insert Chunk into Database
            db_chunk = AccountDocumentChunkModel(
                document_id=new_doc.id,
                account_id=account_id,
                chunk_index=idx,
                content=chunk,
            )
            db.add(db_chunk)
            await db.commit()
            await db.refresh(db_chunk)

            # 6b. Generate Embedding for this Chunk
            vector = await embedding_client.get_embedding(chunk)
            db_embedding = AccountEmbeddingModel(
                account_id=account_id,
                content_type="document",
                embedding=vector,
                source_record_id=db_chunk.id,
            )
            db.add(db_embedding)

        await db.commit()
    except Exception as emb_err:
        await logger.aerror("chunk_embedding_indexing_failed", error=str(emb_err))
        # Rollback metadata since embedding pipeline collapsed
        await db.delete(new_doc)
        await db.commit()
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF was saved but vector indexing failed. Cleanup executed.",
        )

    await logger.ainfo(
        "pdf_indexing_success",
        doc_id=str(new_doc.id),
        chunks_count=len(chunks),
    )
    return new_doc


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    account_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Lists all uploaded knowledge documents for a specific account.
    """
    workspace_id = UUID(current_user["workspace_id"])
    result = await db.execute(
        select(AccountDocumentModel).where(
            AccountDocumentModel.account_id == account_id,
            AccountDocumentModel.workspace_id == workspace_id,
        )
    )
    return result.scalars().all()


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Deletes a document metadata, removes its physical file, and cascades-deletes
    all corresponding text chunks and pgvector embeddings.
    """
    workspace_id = UUID(current_user["workspace_id"])
    await logger.ainfo("pdf_deletion_requested", document_id=str(document_id))

    # 1. Fetch document
    doc_res = await db.execute(
        select(AccountDocumentModel).where(
            AccountDocumentModel.id == document_id,
            AccountDocumentModel.workspace_id == workspace_id,
        )
    )
    document = doc_res.scalar_one_or_none()
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found in your workspace",
        )

    # 2. Delete physical file from disk
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
    file_path = os.path.join(root_dir, "storage", "documents", document.file_path)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            await logger.awarn("physical_file_removal_failed", error=str(e))

    # 3. Fetch all chunks of this document to delete their embeddings
    chunks_res = await db.execute(
        select(AccountDocumentChunkModel.id).where(
            AccountDocumentChunkModel.document_id == document_id
        )
    )
    chunk_ids = [row for row in chunks_res.scalars().all()]

    if chunk_ids:
        # Cascade delete embeddings linked to these chunks
        await db.execute(
            AccountEmbeddingModel.__table__.delete().where(
                AccountEmbeddingModel.content_type == "document",
                AccountEmbeddingModel.source_record_id.in_(chunk_ids),
            )
        )

    # 4. Delete document metadata (which cascades to account_document_chunks)
    await db.delete(document)
    await db.commit()

    await logger.ainfo("pdf_deletion_success", document_id=str(document_id))
    return None


@router.post("/rag-query", response_model=RagQueryResponse)
async def rag_query(
    req: RagQueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Retrieves the most semantically relevant chunks from both uploaded PDF documents
    and private notes, then synthesizes a highly professional response using Gemini.
    """
    workspace_id = UUID(current_user["workspace_id"])
    await logger.ainfo(
        "rag_query_requested", query=req.query, account_id=str(req.account_id)
    )

    # 1. Fetch account
    acc_res = await db.execute(
        select(AccountModel).where(
            AccountModel.id == req.account_id,
            AccountModel.workspace_id == workspace_id,
            AccountModel.deleted_at.is_(None),
        )
    )
    account = acc_res.scalar_one_or_none()
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found in your workspace",
        )

    # 2. Embed user query string
    try:
        query_vector = await embedding_client.get_embedding(req.query)
    except Exception as e:
        await logger.aerror("query_embedding_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate embedding for your question",
        )

    # 3. Semantic similarity search over documents and notes (top 5 matches)
    try:
        distance_col = AccountEmbeddingModel.embedding.cosine_distance(
            query_vector
        ).label("distance")

        stmt = (
            select(AccountEmbeddingModel, distance_col)
            .where(
                AccountEmbeddingModel.account_id == req.account_id,
                AccountEmbeddingModel.content_type.in_(["document", "note"]),
            )
            .order_by("distance")
            .limit(5)
        )

        res = await db.execute(stmt)
        embeddings = res.all()
    except Exception as db_err:
        await logger.aerror("rag_similarity_search_failed", error=str(db_err))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Vector database lookup failed during semantic retrieval",
        )

    # 4. Consolidate context text and compile citations
    context_chunks = []
    citations = []
    seen_sources = set()

    for emb_record, dist in embeddings:
        similarity = 1.0 - float(dist) if dist is not None else 0.0
        # Filter out extremely weak matches (arbitrary threshold: cosine distance > 0.6)
        if similarity < 0.4:
            continue

        if emb_record.content_type == "document":
            # Retrieve chunk text from AccountDocumentChunkModel
            chk_res = await db.execute(
                select(AccountDocumentChunkModel).where(
                    AccountDocumentChunkModel.id == emb_record.source_record_id
                )
            )
            chunk = chk_res.scalar_one_or_none()
            if chunk:
                # Retrieve document filename
                doc_res = await db.execute(
                    select(AccountDocumentModel.filename).where(
                        AccountDocumentModel.id == chunk.document_id
                    )
                )
                filename = doc_res.scalar_one_or_none() or "Corporate Document"
                context_chunks.append(f"[Sumber: {filename}]\n{chunk.content}")

                if filename not in seen_sources:
                    citations.append(
                        RagCitation(source_name=filename, source_type="document")
                    )
                    seen_sources.add(filename)

        elif emb_record.content_type == "note":
            # Retrieve note text from AccountNoteModel
            note_res = await db.execute(
                select(AccountNoteModel).where(
                    AccountNoteModel.id == emb_record.source_record_id,
                    AccountNoteModel.deleted_at.is_(None),
                )
            )
            note = note_res.scalar_one_or_none()
            if note:
                context_chunks.append(f"[Sumber: Catatan AM Pribadi]\n{note.content}")
                source_lbl = "Catatan AM Pribadi"
                if source_lbl not in seen_sources:
                    citations.append(
                        RagCitation(source_name=source_lbl, source_type="note")
                    )
                    seen_sources.add(source_lbl)

    # 5. Synthesize answer using Gemini 2.5 Flash through LiteLLM
    if not context_chunks:
        # Fallback if no relevant corporate documents exist
        system_prompt = (
            "You are a helpful business research assistant for an Account Manager. "
            "The AM is asking a question about the account company, but we have absolutely no internal documents "
            "or notes stored for this account. Respond politely in Indonesian explaining that there are no uploaded "
            "documents or private notes for this company yet, so you cannot provide customized answers."
        )
        user_prompt = f"Company: {account.company_name}\nQuestion: {req.query}"
    else:
        compiled_context = "\n\n---\n\n".join(context_chunks)
        system_prompt = (
            "You are an elite corporate intelligence assistant. "
            "Answer the user's question about the company based ONLY on the provided Context of internal documents "
            "and private notes. Synthesize the answer professionally, clearly, and concisely in Indonesian. "
            "Use clear bullet points and bold formatting where appropriate. "
            "If the answer cannot be found in the provided Context, politely state that the internal documents "
            "do not contain this information, but do NOT make up any facts."
        )
        user_prompt = (
            f"Company: {account.company_name}\n\n"
            f"Context:\n{compiled_context}\n\n"
            f"Question: {req.query}"
        )

    # Setup LiteLLM Vertex project credentials
    llm_provider = os.getenv("RESEARCH_LLM_PROVIDER", "vertex_ai").lower()
    llm_model = os.getenv("RESEARCH_LLM_MODEL", "vertex_ai/gemini-2.5-flash")

    if llm_provider == "vertex_ai":
        if not os.getenv("VERTEX_PROJECT") and os.getenv("GCP_PROJECT_ID"):
            os.environ["VERTEX_PROJECT"] = os.getenv("GCP_PROJECT_ID")
        if not os.getenv("VERTEX_LOCATION") and os.getenv("GCP_LOCATION"):
            os.environ["VERTEX_LOCATION"] = os.getenv("GCP_LOCATION")

    try:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = await litellm.acompletion(
            model=llm_model, messages=messages, timeout=30.0
        )
        answer = response.choices[0].message.content.strip()
    except Exception as llm_err:
        await logger.aerror("rag_llm_call_failed", error=str(llm_err))
        # fallback
        answer = (
            "Maaf, asisten AI sedang mengalami kendala saat memproses jawaban dari dokumen Anda. "
            f"Koneksi LLM gagal: {str(llm_err)}"
        )

    return RagQueryResponse(answer=answer, citations=citations)
