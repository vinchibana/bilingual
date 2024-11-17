from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
from api.models import TranslationStatus
from api.services.translator import translation_service  # 导入全局实例

router = APIRouter()

@router.post("/books/upload")
async def upload_book(
    file: UploadFile = File(..., description="The epub file to upload")
):
    """上传epub文件"""
    if not file.filename:
        raise HTTPException(400, "No file provided")
    return await translation_service.save_uploaded_file(file)

@router.get("/books/{book_id}")
async def get_book_status(book_id: str):
    """获取翻译状态"""
    return await translation_service.get_translation_status(book_id)

@router.get("/books/{book_id}/download")
async def download_book(book_id: str):
    """下载翻译后的文件"""
    return await translation_service.get_translated_file(book_id) 
