from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from .model_orm import KbotMdModels
from core.exceptions import DatabaseException


class KbotMdModelsRepository:
    """Repository for KBOT_MD_KB_MODELS table operations."""
    
    def __init__(self, db_session: AsyncSession):
        """
        初始化模型仓库
        """
        self.db_session = db_session
        

    async def get(self, model_name: str) -> Sequence[KbotMdModels]:
        """Get knowledge base model by model_name."""
        try:
            result = await self.db_session.execute(
                    select(KbotMdModels).where(KbotMdModels.model_name == model_name)
            )
            return result.scalars().all()
        except Exception as e:
            raise DatabaseException(f"查询模型失败: {str(e)}")