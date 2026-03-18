from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from .file_orm import FileSummary
from core.dictionary import FileStatus


class FileSummaryRepository():
    """
    文件信息表专属仓储类
    """
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def get(self, file_id: str) -> FileSummary | None:
        try:
            result = await self.db_session.execute(select(FileSummary).where(FileSummary.file_id==file_id))
            return result.scalar_one_or_none()
        except Exception as e:
            raise Exception(f"查询文件信息失败: {str(e)}")
        
    async def get_by_ids(self, file_id_list: list[str]) -> Sequence[FileSummary]:
        try:
            result = await self.db_session.execute(select(FileSummary).where(FileSummary.file_id.in_(file_id_list)))
            return result.scalars().all()
        except Exception as e:
            raise Exception(f"查询文件信息失败: {str(e)}")
        
    async def create(self, file_summary: FileSummary):
        try:
            self.db_session.add(file_summary)
        except Exception as e:
            raise Exception(f"创建文件信息失败: {str(e)}")
        
    async def create_batch(self, file_summary_list: list[FileSummary]):
        try:
            self.db_session.add_all(file_summary_list)
        except Exception as e:
            raise Exception(f"批量创建文件信息失败: {str(e)}")
        
    async def update(self, file_id: str, **kwargs):
        try:
            await self.db_session.execute(update(FileSummary).where(FileSummary.file_id==file_id).values(**kwargs))
        except Exception as e:
            raise Exception(f"更新文件信息失败: {str(e)}")
        
    async def delete(self, file_id: str):
        try:
            await self.db_session.execute(delete(FileSummary).where(FileSummary.file_id==file_id))
        except Exception as e:
            raise Exception(f"删除文件信息失败: {str(e)}")
        
    async def delete_batch(self, batch: str):
        try:
            await self.db_session.execute(delete(FileSummary).where(FileSummary.batch == batch))
        except Exception as e:
            raise Exception(f"批量删除文件信息失败: {str(e)}")
        
    async def get_by_batch(self, batch: str):
        try:
            result = await self.db_session.execute(select(FileSummary).where(FileSummary.batch==batch))
            return result.scalars().all()
        except Exception as e:
            raise Exception(f"查询文件信息失败: {str(e)}")