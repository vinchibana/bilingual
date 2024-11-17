from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routers import books, tasks

app = FastAPI(
    title="Book Translation API",
    description="API for translating books using various AI models"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(books.router, prefix="/api/v1", tags=["books"])
app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])

@app.get("/health")
async def health_check():
    return {"status": "ok"} 
