from abc import ABC, abstractmethod
import os
from typing import Optional, Union
from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings
from langchain_community.chat_models.tongyi import BaseChatModel
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.chat_models.tongyi import ChatTongyi
from utils.config_handler import rag_conf

# 从项目根目录的 .env 加载环境变量（不存在则跳过，便于直接使用系统环境变量）
load_dotenv(override=False)


def _get_api_key() -> str:
    """优先读环境变量，避免密钥进入代码仓库"""
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "未找到 DASHSCOPE_API_KEY。请在项目根目录创建 .env 文件并写入：\n"
            "DASHSCOPE_API_KEY=你的密钥\n"
            "（可参考 .env.example）"
        )
    return api_key


class BaseModelFactory(ABC):
    @abstractmethod
    def generator(self) -> Union[Optional[Embeddings], BaseChatModel]:
        pass


class ChatModelFactory(BaseModelFactory):
    def generator(self) -> BaseChatModel:
        return ChatTongyi(
            model=rag_conf["chat_model_name"],
            dashscope_api_key=_get_api_key()
        )


class EmbeddingsFactory(BaseModelFactory):
    def generator(self) -> Embeddings:
        return DashScopeEmbeddings(
            model=rag_conf["embedding_model_name"],
            dashscope_api_key=_get_api_key()
        )


chat_model = ChatModelFactory().generator()
embed_model = EmbeddingsFactory().generator()
