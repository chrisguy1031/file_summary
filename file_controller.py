from fastapi import UploadFile, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from loguru import logger
from file_service import FileService
from file_schema import UploadMetadata, SuccessResponse


class FileController:
    """知识库文件控制器"""
    def __init__(self):
        self.file_service = FileService()

    async def upload_file(self, files: list[UploadFile], metadata: UploadMetadata) -> SuccessResponse:
        """上传文件到知识库"""
        await self.file_service.upload_file_service(
            files=files,
            app_id=metadata.app_id,
            app_user=metadata.app_user,
            batch=metadata.batch
        )
        return SuccessResponse(message="文件上传成功")
                               

    async def remove_file(self, file_ids: list[str]):
        """从知识库中删除文件"""
        await self.file_service.delete_file_service(file_ids=file_ids)

    
file_controller = FileController()