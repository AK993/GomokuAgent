def main() -> None:
    """启动 Gomoku Agent 后端服务"""
    import uvicorn
    print("启动 Gomoku Agent 服务...")
    print("访问 http://localhost:8000 查看 API")
    print("访问 http://localhost:8000/docs 查看 API 文档")
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
