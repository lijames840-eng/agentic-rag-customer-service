import uuid

from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

from model.factory import chat_model
from utils.prompt_loader import load_system_prompts
from agent.tools.agent_tools import rag_summarize,get_weather,get_user_location,get_user_id,get_current_month,fetch_external_data,fill_context_for_report
from agent.tools.middleware import monitor_tool,log_before_model,report_prompt_switch


class ReactAgent:
    def __init__(self):
        # 会话级状态存储器：按 thread_id 保存每一轮的消息历史
        # 放在 __init__ 里，配合 st.cache_resource，整个进程复用同一个实例
        self.checkpointer = InMemorySaver()

        self.agent=create_agent(
            model=chat_model,
            system_prompt=load_system_prompts(),
            tools=[rag_summarize,get_weather,get_user_location,get_user_id,get_current_month,fetch_external_data,fill_context_for_report],
            middleware=[monitor_tool,log_before_model,report_prompt_switch],
            # 开启状态持久化：没有它，每轮都是全新的图执行，历史不会被带上
            checkpointer=self.checkpointer,
        )

    @staticmethod
    def new_thread_id() -> str:
        """为一个新会话生成独立 thread_id。

        一个 thread_id 对应一条独立的对话上下文，互不串扰。
        """
        return f"thread_{uuid.uuid4().hex[:12]}"

    def execute_stream(self,query,thread_id: str):
        """流式执行一轮问答。

        Args:
            query: 本轮用户输入。只传当前这一句，历史由 checkpointer 按 thread_id 自动补全。
            thread_id: 会话标识。同一个 id 的多次调用共享上下文，不同 id 互相隔离。
        """
        if not thread_id:
            raise ValueError("thread_id 不能为空：缺少会话标识会导致上下文丢失")

        # LangGraph 依靠 config 里的 thread_id 定位该会话的 checkpoint
        config={"configurable":{"thread_id":thread_id}}

        input_dict={
            "messages" : [
                {"role":"user","content":query},
            ]
        }
        #第三个参数context就是上下文runtime中的信息，就是我们做提示词切换的标记
        for chunk in self.agent.stream(
            input_dict,
            config=config,
            stream_mode="values",
            context={"report":False},
        ):
            latest_message=chunk["messages"][-1]
            if latest_message.content:
                yield latest_message.content.strip()+"\n"

    def execute_stream_steps(self,query,thread_id: str):
        """按「消息」粒度流式执行一轮问答。

        与 execute_stream 拼接纯文本不同，这里原样产出本轮新增的消息对象，
        前端据此区分模型思考、工具调用、工具结果与最终回答。
        """
        if not thread_id:
            raise ValueError("thread_id 不能为空：缺少会话标识会导致上下文丢失")

        config={"configurable":{"thread_id":thread_id}}
        input_dict={
            "messages" : [
                {"role":"user","content":query},
            ]
        }

        cursor=None
        for chunk in self.agent.stream(
            input_dict,
            config=config,
            stream_mode="values",
            context={"report":False},
        ):
            messages=chunk["messages"]
            if cursor is None:
                # 首个快照里带着历史消息，只放行本轮用户消息之后的部分
                last_human_index=-1
                for index,message in enumerate(messages):
                    if isinstance(message,HumanMessage):
                        last_human_index=index
                cursor=last_human_index+1

            for message in messages[cursor:]:
                yield message
            cursor=len(messages)

    def reset_thread(self,thread_id: str) -> None:
        """清空某个会话的全部历史，用于「清空会话」按钮。"""
        try:
            self.checkpointer.delete_thread(thread_id)
        except Exception:
            # 部分 checkpointer 实现没有 delete_thread，忽略即可：
            # 换一个新的 thread_id 等效于开新会话
            pass

    def history_length(self,thread_id: str) -> int:
        """返回该会话已累积的消息条数，便于排查上下文是否被正确带上。"""
        try:
            tup=self.checkpointer.get_tuple({"configurable":{"thread_id":thread_id}})
            if not tup:
                return 0
            return len(tup.checkpoint.get("channel_values",{}).get("messages",[]))
        except Exception:
            return 0


if __name__ == '__main__':
    agent=ReactAgent()
    tid=agent.new_thread_id()

    print("="*50)
    print("第一轮")
    for chunk in agent.execute_stream("扫地机器人在我所在的地区的气温下如何保养",tid):
        print(chunk,end="",flush=True)

    print("\n"+"="*50)
    print(f"第二轮（历史消息数：{agent.history_length(tid)}）")
    for chunk in agent.execute_stream("那滤网多久换一次",tid):
        print(chunk,end="",flush=True)

    print("\n"+"="*50)
    print(f"最终历史消息数：{agent.history_length(tid)}")
