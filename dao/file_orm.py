from sqlalchemy import create_engine, String, Integer, Date, Numeric, CLOB
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from .base import Base



# 文件摘要表 ORM 模型
class FileSummary(Base):
    """
    文件摘要表 ORM 模型，对应 Oracle 的 file_summary 表
    """
    __tablename__ = "file_summary"  # 数据库表名
    
    # 字段映射（严格对应建表语句的字段类型和约束）
    file_id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        comment="文件ID，主键"
    )
    app_id: Mapped[int] = mapped_column(
        Numeric(4, 0), 
        nullable=False, 
        comment="应用ID"
    )
    app_user: Mapped[str] = mapped_column(
        String(100), 
        nullable=False, 
        comment="应用用户"
    )
    upload_date: Mapped[datetime] = mapped_column(
        Date, 
        default=datetime.now,  # 对应 Oracle 的 SYSDATE
        comment="上传日期，默认当前时间"
    )
    file_name: Mapped[str] = mapped_column(
        String(200), 
        nullable=False, 
        comment="文件名"
    )
    file_ext: Mapped[str | None] = mapped_column(
        String(10), 
        comment="文件扩展名"
    )
    file_size: Mapped[int | None] = mapped_column(
        Numeric(10, 0), 
        comment="文件大小（字节）"
    )
    file_path: Mapped[str] = mapped_column(
        String(500), 
        comment="文件路径"
    )
    batch: Mapped[str | None] = mapped_column(
        String(100), 
        comment="批次号"
    )
    file_seq: Mapped[int] = mapped_column(
        Numeric(5, 0), 
        nullable=False, 
        comment="文件序号"
    )
    language: Mapped[str] = mapped_column(
        String(50), 
        comment="文件语言"
    )
    status: Mapped[int] = mapped_column(
        Numeric(2, 0), 
        comment="文件状态"
    )
    summary_en: Mapped[str | None] = mapped_column(
        CLOB, 
        comment="英文摘要"
    )
    summary_cn: Mapped[str | None] = mapped_column(
        CLOB, 
        comment="中文摘要"
    )
    summary_kr: Mapped[str | None] = mapped_column(
        CLOB, 
        comment="韩文摘要"
    )
    summary_ja: Mapped[str | None] = mapped_column(
        CLOB, 
        comment="日文摘要"
    )