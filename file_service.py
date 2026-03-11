import os
import uuid
import shutil
from pathlib import Path
from fastapi import UploadFile
from loguru import logger
from core.settings import get_app_config
from core.dictionary import FileStatus
from core.meta_oracle import get_session
from core.exceptions import *
from dao.file_orm import FileSummary
from dao.file_repo import FileSummaryRepository



class FileService:
    '''
    文件上传/删除等服务
    '''
    def __init__(self) -> None:
        '''初始化文件上传/删除服务'''
        config = get_app_config()
        self.file_storage = config.file_storage

    @property
    def db_session(self):
        return get_session()

###############################################################################
# 保存文件
###############################################################################

    def _save_file(self, file: UploadFile, batch: str) -> dict:
            '''
            保存单个文件到磁盘并返回文件保存结果
            
            参数:
                file: 要上传的文件
                batch: 本次上传的批次
                
            返回:
                dict: 文件保存结果，包含:
                    {
                        "file_path": str,  // 文件保存路径
                        "file_name": str,  // 文件名
                        "file_ext": str,   // 文件扩展名
                        "file_size": int     // 文件大小
                    }
                或出错时返回空字典
            '''
            filename = file.filename
            if filename is None:
                raise ParamValueError("文件名不能为空")
            
            
            logger.debug(f"开始保存文件: {filename} 到 {self.file_storage}")
            try:
                # 读取文件内容
                file_content = file.file.read()

                root_path = Path(self.file_storage).resolve()  # 转换为绝对路径
                target_path = root_path / Path(batch)
                target_path.mkdir(parents=True, exist_ok=True)
                file_path = target_path / Path(filename)

                # 获取文件相关参数
                name, ext = os.path.splitext(filename)

                fileparams = {"file_path": str(file_path), 
                              "file_name": filename, 
                              "file_ext": ext, 
                              "file_size": len(file_content)}          
                
                # 保存文件
                with open(file_path, "wb") as f:
                    f.write(file_content)
                
                logger.info(f"文件保存成功: {filename} -> {file_path}")
                return fileparams

            except Exception as e:
                msg = f"保存文件 {filename if 'filename' in locals() else '未知文件'} 失败: {e}"
                handle_exception(e, msg)

    async def _save_metadata(self, 
                             fileparams: list[dict],
                             app_id: int,
                             app_user: str,
                             batch: str):
        """
        保存文件元数据到数据库
        """
        async with self.db_session as session:
            file_repo = FileSummaryRepository(db_session=session)
            
            # 构造 file 的实体列表用于批量保存到数据库
            file_list = []
            for fileparam in fileparams:
                # 构造文件实体
                file = FileSummary(
                    file_id = str(uuid.uuid4()),
                    app_id = app_id,
                    app_user = app_user,
                    batch = batch,
                    file_path = fileparam["file_path"],
                    file_name = fileparam["file_name"],
                    file_ext = fileparam["file_ext"],
                    file_size = fileparam["file_size"],
                    status=FileStatus.UPLOADED.value
                )
                file_list.append(file)
            
            # 保存文件元数据到数据库
            try:
                logger.debug(f"开始将 {len(file_list)} 个文件保存到数据库")
                await file_repo.create_batch(file_list)
                logger.info(f"成功将 {len(file_list)} 个文件保存到数据库")
            except Exception as e:
                handle_exception(e, "保存文件元数据到数据库失败")


    async def upload_file_service(self, 
                                files: list[UploadFile], 
                                app_id: int,
                                app_user: str,
                                batch: str
                                ):
        '''
        上传文件到知识库并保存记录到数据库
            
        Args:
            files: 要上传的文件列表
            app_id: APP标识
            app_user: 用户标识
            batch: 本次上传的批次名称
        '''
        async with self.db_session as session:
            param_list = []
            for file in files:
                try:
                    # 保存文件到磁盘
                    param_list.append(self._save_file(file=file, batch=batch))
                except Exception as e:
                    error_msg = f"保存文件到磁盘失败: {e}"
                    logger.error(error_msg)
                    raise InternalServerError(error_msg)
            
            # 保存文件元数据到数据库
            await self._save_metadata(fileparams=param_list,
                                    app_id=app_id,
                                    app_user=app_user,
                                    batch=batch)
            
###############################################################################
# 删除文件
###############################################################################
        
    def _delete_file(self, file_path: str):
        '''根据完整文件名从磁盘删除文件，如果batch文件夹为空则自动删除
        
        Args:
            file_path: 要删除的完整文件名
        '''
        
        logger.debug(f"正在删除文件: {file_path}")
        file_obj = Path(file_path)
        
        if not file_obj.exists():
            logger.info(f"文件 {file_path} 不存在, 跳过删除")
            return
        
        # 记录batch文件夹路径
        batch_folder = file_obj.parent
        
        try:
            file_obj.unlink()  # 删除文件
            logger.debug(f"成功删除文件: {file_path}")
        except Exception as e:
            logger.error(f"删除文件 {file_path} 失败: {e}")
            raise InternalServerError(f"删除文件 {file_path} 失败: {e}")
        
        # 检查并删除空的batch文件夹

        try:
            if batch_folder.exists() and batch_folder.is_dir():
                # 检查文件夹是否为空
                if not any(batch_folder.iterdir()):
                    batch_folder.rmdir()
                    logger.debug(f"成功删除空的batch文件夹: {batch_folder}")
        except Exception as e:
            # 其他异常情况需要记录警告
            logger.warning(f"删除batch文件夹 {batch_folder} 失败: {e}")

    async def delete_file_service(
            self,
            file_ids: list[str]
        ):
        """
        文件删除服务
        
        Args:
            file_ids: 文件ID列表(用于特定文件删除)
        """
        async with self.db_session as session:
            file_repo = FileSummaryRepository(session)
            logger.info(f"开始删除 {len(file_ids)} 个文件")
            # 1. 获取文件路径
            try:
                file_list = await file_repo.get_by_ids(file_ids)
            except Exception as e:
                raise InternalServerError(f"获取文件路径失败: {e}")
            
            # 2. 删除文件的元数据
            try:
                await file_repo.delete_batch(file_ids)
            except DatabaseException as e:
                logger.error(e.original_error or e.message)
                raise InternalServerError(e.message)
            
            for file in file_list:
                self._delete_file(file.file_path)
            