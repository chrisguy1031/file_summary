# core/config/settings.py
from functools import lru_cache
from pathlib import Path
from typing import Any
import os
import tomli
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings

class LogConfig(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO")
    dir: str = Field(default="./logs")
    rotation: str = Field(default="100 MB")
    retention: str = Field(default="10 days")
    api_log_enabled: bool = Field(default=True, description="是否启用API请求日志记录")

class AppConfig(BaseModel):
    """主应用配置"""
    service_name: str = Field(default="main_service")
    service_version: str = Field(default="3.0.0")
    service_host: str = Field(default="0.0.0.0")
    service_port: int = Field(default=18099, ge=1, le=65535)
    title: str = Field(default="KBOT")
    description: str = Field(default="KBot API Service")
    debug: bool = Field(default=False)
    file_storage: str = Field(default="./knowledge_base")
    llm_model: str = Field(default="xai.grok-3")
    log: LogConfig = LogConfig()

class OracleConfig(BaseModel):
    """Oracle 数据库配置"""
    username: str = Field(default="kbot")
    password: str = Field(default="")
    host: str = Field(default="localhost")
    port: int = Field(default=1521, ge=1, le=65535)
    service_name: str = Field(default="kbotdev")
    
    @property
    def dsn(self) -> str:
        """生成 Oracle DSN"""
        return f"{self.username}/{self.password}@{self.host}:{self.port}/{self.service_name}"

class SQLAlchemyConfig(BaseModel):
    """SQLAlchemy 配置"""
    echo: bool = Field(default=False)
    pool_size: int = Field(default=10, ge=1, le=50)
    pool_timeout: int = Field(default=60, ge=10, le=300)
    max_overflow: int = Field(default=20, ge=0, le=50)
    pool_pre_ping: bool = Field(default=True)
    pool_use_lifo: bool = Field(default=True)
    pool_recycle: int = Field(default=1800, ge=60, le=3600)


class Settings(BaseSettings):
    """全局配置设置"""
    
    # 环境配置 - 支持环境变量覆盖
    environment: str = "development"
    config_dir: str = "."
    
    # 各模块配置
    app: AppConfig = AppConfig()
    oracle: OracleConfig = OracleConfig()
    sqlalchemy: SQLAlchemyConfig = SQLAlchemyConfig()
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8", 
        "case_sensitive": False,
        "extra": "ignore",
        "env_prefix": "",  # 环境变量不需要前缀
    }
    
    @classmethod
    def create(cls, toml_path: Path | None = None) -> "Settings":
        """创建配置实例 - 支持环境变量切换"""
        # 首先检查环境变量
        env_from_env = os.getenv("ENVIRONMENT")
        config_dir_from_env = os.getenv("CONFIG_DIR")
        
        # 创建临时实例来获取其他配置
        temp_settings = cls()
        
        # 确定环境：环境变量优先，然后是配置文件
        environment = env_from_env or temp_settings.environment
        config_dir = Path(config_dir_from_env or temp_settings.config_dir)
        
        print(f"Loading configuration for environment: {environment}")
        print(f"Config directory: {config_dir}")
        
        if toml_path is None:
            toml_path = config_dir / f"{environment}.toml"
            print(f"Loading TOML from: {toml_path}")
        
        # 确保配置目录存在
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载基础配置
        base_config_path = config_dir / "base.toml"
        base_config = cls._load_toml(base_config_path)
        
        # 加载环境特定配置
        env_config = cls._load_toml(toml_path)
        
        # 合并配置
        merged_config = cls._deep_merge(base_config, env_config)
        
        # 创建最终配置实例
        final_settings = cls(**merged_config)
        
        # 确保环境设置正确（环境变量可能覆盖了配置文件）
        if env_from_env:
            final_settings.environment = env_from_env
        if config_dir_from_env:
            final_settings.config_dir = config_dir_from_env
            
        return final_settings
    
    @staticmethod
    def _load_toml(file_path: Path) -> dict[str, Any]:
        """加载 TOML 文件，如果文件不存在返回空字典"""
        if not file_path.exists():
            print(f"Warning: Config file {file_path} not found, using defaults")
            return {}
        
        try:
            with open(file_path, "rb") as f:
                config = tomli.load(f)
                print(f"Loaded TOML config from: {file_path}")
                return config
        except Exception as e:
            print(f"Error loading TOML config {file_path}: {e}, using defaults")
            return {}
    
    @staticmethod
    def _deep_merge(base: dict, update: dict) -> dict:
        """深度合并字典"""
        result = base.copy()
        
        for key, value in update.items():
            if (key in result and isinstance(result[key], dict) 
                and isinstance(value, dict)):
                result[key] = Settings._deep_merge(result[key], value)
            else:
                result[key] = value
                
        return result

    def is_development(self) -> bool:
        """检查是否为开发环境"""
        return self.environment.lower() in ["dev", "development", "debug"]
    
    def is_production(self) -> bool:
        """检查是否为生产环境"""
        return self.environment.lower() in ["prod", "production", "live"]
    
    def is_testing(self) -> bool:
        """检查是否为测试环境"""
        return self.environment.lower() in ["test", "testing", "staging"]


# 全局配置实例
@lru_cache()
def get_settings() -> Settings:
    """获取缓存的配置实例"""
    return Settings.create()

# 便捷访问函数
def get_app_config() -> AppConfig:
    """获取主应用配置"""
    return get_settings().app

def get_oracle_config() -> OracleConfig:
    """获取 Oracle 配置"""
    return get_settings().oracle

def get_sqlalchemy_config() -> SQLAlchemyConfig:
    """获取 SQLAlchemy 配置"""
    return get_settings().sqlalchemy

def get_log_config() -> LogConfig:
    """获取 log 配置"""
    return get_app_config().log