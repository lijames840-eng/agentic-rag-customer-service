"""
总结服务类：用户提问，搜索参考资料，将提问和参考资料提交给模型，让模型总结回复
用户问题->retriver(Chroma向量检索)->召回Top-k Document文档分片->拼接成context上下文->prompt模板填充：{query}+{context}->chat_model模型推理返回AIMessage->StrOutParser提取文本转成字符串->返回自然语言答案
"""
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser

from rag.vector_store import VectorStoreService
from utils.prompt_loader import load_rag_prompts
from langchain_core.prompts import PromptTemplate
from model.factory import chat_model

def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("="*20)
    return prompt
class RagSummarizeService(object):
    def __init__(self):
        self.vector_store = VectorStoreService()    #连接已经建好的Chroma向量库
        self.retriever = self.vector_store.get_retriever()   #获取检索器
        self.prompt_text = load_rag_prompts()               #读取rag提示词模板
        self.prompt_template = PromptTemplate.from_template(self.prompt_text)  #构建langchain提示模板
        self.model = chat_model         #加载千问模型
        self.chain = self._init_chain()   #组装链式链路

    def _init_chain(self):
        chain = self.prompt_template |print_prompt| self.model | StrOutputParser()
        return chain

    def retriever_docs(self, query: str) -> list[Document]:  #用户把问题交给retriver，内部把问题转成embedding向量，去Chroma里算向量相似度，返回相似度最高的K条分片文档
        return self.retriever.invoke(query)

    def rag_summarize(self, query: str) -> str:
        context_docs=self.retriever_docs(query)   #拿到返回的分片文档:list[Document]
        context=""
        counter=0
        for doc in context_docs:
            #循环拼接所以检索到的文档内容，统一做成上下文字符串
            counter+=1
            context+=f"[参考资料{counter}]:参考资料：{doc.page_content} | 参考元数据：{doc.metadata}\n"
        #把query和context两个变量传入prompt模板
        return self.chain.invoke(
            {
                "input":query,
                "context":context,
            }
        )

if __name__ == '__main__':
    rag=RagSummarizeService()
    print(rag.rag_summarize("小户型适合哪些扫地机器人"))

