import json
from pydantic import BaseModel, Field, field_validator
from typing import Generic, TypeVar

T = TypeVar('T')

class UploadMetadata(BaseModel):
    """上传文件表单模型"""
    app_id: int = Field(..., description="业务域ID")
    app_user: str = Field(..., description="用户名")
    batch: str = Field(..., description="批次名称")



class SuccessResponse(BaseModel, Generic[T]):
    """Cube API 成功响应模型"""
    message: str = Field("Success", description="返回的响应信息，用于前端显示给用户")
    data: T | None = Field(default=None, description="响应返回的业务数据")
    
    # 显式设置模型配置
    model_config = {
        "arbitrary_types_allowed": True,
    }