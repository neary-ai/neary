from fastapi import HTTPException, APIRouter, Body, UploadFile, File
from fastapi.responses import JSONResponse

from .models import *
from .services.document_service import DocumentManager


router = APIRouter()


@router.get("/{conversation_id}")
async def get_documents(conversation_id: int):
    """Get a conversation's documents"""
    document_manager = DocumentManager(conversation_id)
    documents = await document_manager.get_documents(conversation_only=False)

    return JSONResponse(content=documents)


@router.patch("/{doc_key}/conversations/{conversation_id}")
async def manage_conversation_id(
    doc_key: str, conversation_id: int, action: str = Body(...)
):
    """Add or remove a conversation from a document"""
    document_manager = DocumentManager(conversation_id)
    if action == "add":
        await document_manager.add_conversation_id(doc_key, conversation_id)
    else:
        await document_manager.remove_conversation_id(doc_key, conversation_id)

    return JSONResponse(content={"status": "success"})


@router.delete("/{doc_key}")
async def delete_document(doc_key: str):
    """Delete a document"""
    conversation = await ConversationModel.first()
    document_manager = DocumentManager(conversation.id)
    await document_manager.delete_documents(doc_key)

    return JSONResponse(content={"status": "success"})


@router.post("/{conversation_id}/add_file")
async def upload_document(conversation_id: int, file: UploadFile = File(...)):
    """Create a new document from a file"""
    document_manager = DocumentManager(conversation_id)
    try:
        await document_manager.load_files([file])
        return JSONResponse(status_code=200, content={"detail": "success"})
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{conversation_id}/add_url")
async def upload_url(conversation_id: int, url: str = Body(...)):
    """Create a new document from a URL"""
    document_manager = DocumentManager(conversation_id)
    await document_manager.load_url(url)

    return JSONResponse(status_code=200, content={"detail": "success"})
