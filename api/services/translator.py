import os
import uuid
import asyncio
from fastapi import HTTPException, UploadFile
from fastapi.responses import FileResponse
from book_maker.cli import main as translate_book
from api.models import TranslationStatus
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class TranslationService:
    def __init__(self):
        self.upload_dir = "uploads"
        self.translated_dir = "translated"
        self._ensure_directories()
        self.tasks = {}  # 存储任务状态

    def _ensure_directories(self):
        """确保必要的目录存在并有正确的权限"""
        for directory in [self.upload_dir, self.translated_dir]:
            os.makedirs(directory, exist_ok=True)
            # 设置目录权限为 755 (rwxr-xr-x)
            os.chmod(directory, 0o755)

    async def save_uploaded_file(self, file: UploadFile) -> dict:
        """保存上传的文件并返回book_id"""
        if not file.filename.endswith('.epub'):
            raise HTTPException(400, "Only epub files are supported")
        
        book_id = str(uuid.uuid4())
        file_path = os.path.join(self.upload_dir, f"{book_id}.epub")
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        self.tasks[book_id] = TranslationStatus.PENDING
        return {"book_id": book_id}

    async def start_translation(self, book_id: str, params: dict):
        """开始翻译任务"""
        try:
            self.tasks[book_id] = TranslationStatus.PROCESSING
            input_path = os.path.join(self.upload_dir, f"{book_id}.epub")
            
            if not os.path.exists(input_path):
                raise HTTPException(404, "Book file not found")
                
            # 异步执行翻译
            try:
                await self._translate_book(input_path, params)
                self.tasks[book_id] = TranslationStatus.COMPLETED
            except HTTPException as e:
                self.tasks[book_id] = TranslationStatus.FAILED
                raise e
            except Exception as e:
                self.tasks[book_id] = TranslationStatus.FAILED
                raise HTTPException(500, f"Translation failed: {str(e)}")
                
        except Exception as e:
            self.tasks[book_id] = TranslationStatus.FAILED
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(500, str(e))

    async def _translate_book(self, input_path: str, params: dict):
        """执行翻译任务"""
        import sys
        from book_maker.cli import main as translate_book
        
        # 获取 book_id（从文件名中）
        book_id = os.path.splitext(os.path.basename(input_path))[0]
        
        # 构建命令行参数
        sys.argv = [
            'book_maker',
            '--book_name', input_path,
            '--openai_key', params.get("openai_key"),
            '--language', params.get("target_language", "zh-hans"),
            '--model', params.get("model", "chatgptapi"),
        ]
        
        if params.get("test", False):
            sys.argv.extend(['--test'])
        
        try:
            logger.debug(f"Starting translation for {input_path}")
            await asyncio.to_thread(translate_book)
            
            # 获取预期的输出文件路径（在输入文件同目录下）
            name, _ = os.path.splitext(input_path)
            source_path = f"{name}_bilingual.epub"
            
            logger.debug(f"Checking for output file at: {source_path}")
            if os.path.exists(source_path):
                target_path = os.path.join(self.translated_dir, f"{book_id}_bilingual.epub")
                os.rename(source_path, target_path)
                logger.debug(f"Successfully moved output file to: {target_path}")
            else:
                raise HTTPException(500, f"Translation output not found at: {source_path}")
                
        except SystemExit:
            # 检查翻译是否成功完成
            name, _ = os.path.splitext(input_path)
            source_path = f"{name}_bilingual.epub"
            if os.path.exists(source_path):
                target_path = os.path.join(self.translated_dir, f"{book_id}_bilingual.epub")
                os.rename(source_path, target_path)
                return
            raise HTTPException(500, "Translation process terminated without output file")
        except Exception as e:
            logger.error(f"Translation failed: {str(e)}", exc_info=True)
            raise

    async def get_translation_status(self, book_id: str) -> dict:
        """获取翻译状态"""
        if book_id not in self.tasks:
            raise HTTPException(404, "Book not found")
        return {
            "status": self.tasks[book_id],
            "book_id": book_id
        }

    async def get_translated_file(self, book_id: str) -> FileResponse:
        """获取翻译后的文件"""
        file_path = os.path.join(self.translated_dir, f"{book_id}_bilingual.epub")
        if not os.path.exists(file_path):
            raise HTTPException(404, "Translated file not found")
        return FileResponse(file_path) 

# 创建全局实例
translation_service = TranslationService() 
