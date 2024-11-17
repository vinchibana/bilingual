from fastapi import APIRouter, HTTPException
from api.models import TranslationRequest, TranslationResponse
from api.services.translator import translation_service  # 导入全局实例

router = APIRouter()

@router.post("/tasks/translate", response_model=TranslationResponse)
async def create_translation_task(request: TranslationRequest):
    """
    创建新的翻译任务
    """
    try:
        # 检查book_id是否存在
        await translation_service.get_translation_status(request.book_id)
        
        # 开始翻译任务
        await translation_service.start_translation(
            request.book_id,
            {
                "target_language": request.target_language,
                "openai_key": request.openai_key,
                "model": request.model,
                "test": request.test
            }
        )
        
        return TranslationResponse(
            book_id=request.book_id,
            status="processing",
            message="Translation task started"
        )
    except HTTPException as e:
        # 重新抛出HTTP异常
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start translation: {str(e)}"
        )

@router.get("/tasks/{task_id}", response_model=TranslationResponse)
async def get_task_status(task_id: str):
    """
    获取翻译任务状态
    """
    try:
        status = await translation_service.get_translation_status(task_id)
        return TranslationResponse(
            book_id=task_id,
            status=status["status"],
            message=None
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )

@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    """
    取消翻译任务 (TODO: 实现取消功能)
    """
    raise HTTPException(
        status_code=501,
        detail="Task cancellation not implemented yet"
    ) 
