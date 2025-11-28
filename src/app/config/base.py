# src/app/config/base.py

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """
    整个项目的“全局配置”。

    设计原则：
    - 所有硬编码字符串（端口、URL、模型名等）都放这里；
    - 支持通过环境变量覆盖，方便不同机器 / 环境；
    - 其他模块统一通过 get_settings() 读取。
    """

    # 告诉 pydantic-settings 怎么从环境变量读取
    model_config = SettingsConfigDict(
        env_prefix="AGENT_",  # 所有环境变量都以 AGENT_ 开头
        env_file=".env",      # 如果存在 .env 文件，也会读取
        extra="ignore",       # 忽略未定义字段
    )

    # 基础信息
    env: Literal["dev", "prod", "test"] = Field(
        default="dev", description="当前运行环境"
    )
    project_name: str = Field(
        default="continual_agent_lab", description="项目名称"
    )
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", description="默认日志级别"
    )

    # LLM / vLLM 相关配置（占个位，后面会用到）
    vllm_base_url: str = Field(
        default="http://localhost:8000/v1",
        description="vLLM OpenAI-compatible API 的基础 URL",
    )
    qwen_model: str = Field(
        default="Qwen/Qwen2.5-3B-Instruct",
        description="默认使用的 Qwen 模型名称（当前使用 3B 版本）",
    )

    # Embedding 相关配置（BGE-M3 占个位）
    embedding_model: str = Field(
        default="BAAI/bge-m3",
        description="默认使用的 embedding 模型",
    )


@lru_cache
def get_settings() -> AppSettings:
    """
    全局唯一的配置获取入口。

    使用 lru_cache 的原因：
    - BaseSettings 会读环境变量 / .env，如果每次都 new 会有开销；
    - 我们希望整个进程里只有一个 settings 实例。
    """
    return AppSettings()
