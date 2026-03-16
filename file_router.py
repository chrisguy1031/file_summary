from fastapi import APIRouter, UploadFile, status, Form, File

from file_controller import file_controller as controller
from file_schema import *

router = APIRouter(prefix="/api/v1", tags=["File Service"])

@router.post("/upload", response_model=SuccessResponse, status_code=status.HTTP_202_ACCEPTED, summary="上传一个或多个文件")
async def handle_upload_files(
    files: list[UploadFile] = File(..., description="要上传的文件列表"),
    app_id: int = Form(..., description="应用ID"),
    app_user: str = Form(..., description="应用用户名"),
    batch: str = Form(..., description="批次名称")
):
    """上传一个或多个文件到指定的知识库。"""
    metadata = UploadMetadata(
        app_id=app_id,
        app_user=app_user,
        batch=batch
    )
    return await controller.upload_file(files, metadata)

    
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT, summary="从指定的知识库中删除文件或按批次删除")
async def handle_remove_file(file_ids: list[str] = Form(..., description="要删除的文件ID列表")):
    """从指定的知识库中删除文件。"""
    await controller.remove_file(file_ids)