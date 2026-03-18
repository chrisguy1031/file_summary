from fastapi import APIRouter, UploadFile, status, Form, File
import time

from file_controller import file_controller as controller
from file_schema import *

router = APIRouter(prefix="/api/v1", tags=["File Service"])

@router.post("/upload", response_model=SuccessResponse, status_code=status.HTTP_202_ACCEPTED, summary="上传一个或多个文件")
async def handle_upload_files(
    files: list[UploadFile] = File(..., description="要上传的文件列表"),
    app_id: int = Form(..., description="应用ID"),
    app_user: str = Form(..., description="应用用户名")
):
    """上传一个或多个文件到指定的知识库。"""
    # 生成批次名称，使用当前时间戳字符串
    batch = str(time.time())
    metadata = UploadMetadata(
        app_id=app_id,
        app_user=app_user,
        batch=batch
    )
    return await controller.upload_file(files, metadata)

    
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, summary="从指定的知识库中删除文件或按批次删除")
async def handle_remove_file(batch: str = Form(..., description="批次名称")):
    """从指定的知识库中删除文件。"""
    await controller.remove_file(batch)

@router.post("/summary", status_code=status.HTTP_202_ACCEPTED, summary="为指定的文件生成摘要")
async def handle_summary_file(batch: str = Form(..., description="批次名称")):
    """为指定的文件生成摘要。"""
    await controller.summary_file(batch)