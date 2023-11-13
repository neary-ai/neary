from fastapi import HTTPException, APIRouter, Body, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .models import *
from .services.document_service import DocumentManager
from database import get_db

router = APIRouter()


@router.get("/documents/{conversation_id}")
async def get_documents(conversation_id: int, db: Session = Depends(get_db)):
    """Get a conversation's documents"""
    document_manager = DocumentManager(db, conversation_id)
    documents = document_manager.get_documents(conversation_only=False)

    return JSONResponse(content=documents)


@router.patch("/documents/{doc_key}/conversations/{conversation_id}")
async def manage_conversation_id(
    doc_key: str,
    conversation_id: int,
    action: str = Body(...),
    db: Session = Depends(get_db),
):
    """Add or remove a conversation from a document"""
    document_manager = DocumentManager(db, conversation_id)
    if action == "add":
        document_manager.add_conversation_id(doc_key)
    else:
        document_manager.remove_conversation_id(doc_key)

    return JSONResponse(content={"status": "success"})


@router.delete("/documents/{doc_key}")
async def delete_document(doc_key: str, db: Session = Depends(get_db)):
    """Delete a document"""
    document_manager = DocumentManager(db)
    document_manager.delete_documents(doc_key)

    return JSONResponse(content={"status": "success"})


@router.post("/documents/{conversation_id}/add_file")
async def upload_document(
    conversation_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Create a new document from a file"""
    document_manager = DocumentManager(db, conversation_id)
    try:
        await document_manager.load_files([file])
        return JSONResponse(status_code=200, content={"detail": "success"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/documents/{conversation_id}/add_url")
async def upload_url(
    conversation_id: int, url: str = Body(...), db: Session = Depends(get_db)
):
    """Create a new document from a URL"""
    document_manager = DocumentManager(db, conversation_id)
    await document_manager.load_url(url)

    return JSONResponse(status_code=200, content={"detail": "success"})
