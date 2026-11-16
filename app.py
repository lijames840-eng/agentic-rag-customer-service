import json

import streamlit as st
from langchain_core.messages import AIMessage, ToolMessage

from agent.react_agent import ReactAgent
from utils.config_handler import chroma_conf, rag_conf

st.set_page_config(
    page_title="智扫通 · 智能客服",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container { max-width: 960px; padding-top: 2rem; padding-bottom: 6rem; }
        .app-header { margin-bottom: 1.4rem; }
        .app-title {
            font-size: 2.1rem; font-weight: 800; letter-spacing: .5px;
            background: linear-gradient(90deg, #2563eb, #06b6d4);
            -webkit-background-clip: text; background-clip: text; color: transparent;
        }
        .app-subtitle { color: #6b7280; font-size: .95rem; margin-top: .35rem; }
        .badge {
            display: inline-block; padding: 3px 11px; margin: .5rem .4rem 0 0;
            border-radius: 999px; background: rgba(37, 99, 235, .10);
            color: #2563eb; font-size: .75rem; font-weight: 600;
        }
        .welcome { text-align: c/enter; padding: 2.4rem 1rem 1.2rem; }
        .welcome h2 { font-size: 1.35rem; margin-bottom: .4rem; }
        .welcome p { color: #6b7280; font-size: .9rem; margin: 0; }
        .logo-mark {
            width: 38px; height: 38px; border-radius: 11px; flex: 0 0 38px;
            display: flex; align-items: center; justify-content: center;
            background: linear-gradient(135deg, #2563eb, #06b6d4);
            color: #fff; font-weight: 700; font-size: 1.05rem;
        }
        .brand { display: flex; align-items: center; gap: 10px; }
        .brand-name { font-weight: 700; line-height: 1.2; }
        .brand-sub { font-size: .72rem; color: #6b7280; }
        div[data-testid="stChatMessage"] { border-radius: 14px; }
        div[data-testid="stSidebar"] { border-right: 1px solid rgba(128, 128, 128, .16); }
        .stButton > button { border-radius: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner="正在加载智能客服…")
def get_agent() -> ReactAgent:
    # 整个进程复用一个实例，避免每个浏览器会话都重建向量库与模型
    return ReactAgent()


agent = get_agent()

if "session_id" not in st.session_state:
    st.session_state["session_id"] = ReactAgent.new_thread_id()
if "messages" not in st.session_state:
    st.session_state["messages"] = []


def render_steps(steps: list[dict]) -> None:
    for step in steps:
        if step["type"] == "thinking":
            st.markdown(f"> {step['content']}")
        elif step["type"] == "tool_call":
            args = json.dumps(step.get("args") or {}, ensure_ascii=False)
            st.markdown(f"**调用工具** · `{step['name']}`")
            st.code(args, language="json")
        elif step["type"] == "tool_result":
            text = step.get("content") or "（无返回内容）"
            st.markdown(f"**工具返回** · `{step['name']}`")
            st.code(text if len(text) <= 600 else text[:600] + " …", language=None)


def run_turn(prompt: str) -> None:
    steps: list[dict] = []
    answer = ""

    with st.chat_message("assistant"):
        status = st.status("正在理解您的问题…", expanded=True)
        answer_box = st.empty()

        try:
            for message in agent.execute_stream_steps(
                prompt, thread_id=st.session_state["session_id"]
            ):
                if isinstance(message, ToolMessage):
                    text = str(message.content or "").strip()
                    steps.append(
                        {"type": "tool_result", "name": message.name or "", "content": text}
                    )
                    with status:
                        st.markdown(f"**工具返回** · `{message.name}`")
                        if text:
                            st.caption(text[:200] + ("…" if len(text) > 200 else ""))
                    status.update(label="正在整理回答…")

                elif isinstance(message, AIMessage):
                    if isinstance(message.content, str):
                        content = message.content
                    else:
                        content = str(message.content or "")
                    content = content.strip()

                    # 有工具调用时，content 是模型的思考过程，展示在调用之前
                    if content and message.tool_calls:
                        steps.append({"type": "thinking", "content": content})
                        with status:
                            st.markdown(content)

                    for call in message.tool_calls:
                        name, args = call.get("name", ""), call.get("args") or {}
                        steps.append({"type": "tool_call", "name": name, "args": args})
                        with status:
                            st.markdown(f"**调用工具** · `{name}`")
                            st.code(json.dumps(args, ensure_ascii=False), language="json")
                        status.update(label=f"正在调用 {name}…")

                    if content and not message.tool_calls:
                        answer = content
                        answer_box.markdown(answer)

        except Exception as exc:
            answer = f"抱歉，服务暂时不可用，请稍后重试。\n\n> 错误信息：{exc}"
            answer_box.error(answer)
            status.update(label="执行出错", state="error", expanded=True)

        if answer:
            status.update(label="回答完成", state="complete", expanded=False)
        else:
            answer = "抱歉，我暂时无法回答这个问题，请换个问法试试。"
            answer_box.warning(answer)
            status.update(label="未生成有效回答", state="error", expanded=False)

    st.session_state["messages"].append(
        {"role": "assistant", "content": answer, "steps": steps}
    )


with st.sidebar:
    st.markdown(
        """
        <div class="brand">
            <div class="logo-mark">智</div>
            <div>
                <div class="brand-name">智扫通</div>
                <div class="brand-sub">扫地机器人智能客服</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.divider()

    st.markdown("#### 会话控制")
    if st.button("新建对话", use_container_width=True, type="primary"):
        agent.reset_thread(st.session_state["session_id"])
        st.session_state["session_id"] = ReactAgent.new_thread_id()
        st.session_state["messages"] = []
        st.rerun()
    st.caption(f"会话标识：`{st.session_state['session_id']}`")
    st.caption(f"上下文消息数：{agent.history_length(st.session_state['session_id'])}")

    st.divider()
    st.markdown("#### 系统信息")
    st.markdown(
        f"""
        - 对话模型：`{rag_conf['chat_model_name']}`
        - 向量模型：`{rag_conf['embedding_model_name']}`
        - 知识库集合：`{chroma_conf['collection_name']}`
        - 召回数量：`Top {chroma_conf['k']}`
        """
    )

    st.divider()
    st.markdown("#### 我能做什么")
    st.markdown(
        """
        - 查询选购、使用、保养、故障知识
        - 结合所在地天气给出使用建议
        - 生成个人月度使用报告
        """
    )
    st.caption("回答由 AI 生成，仅供参考。")

st.markdown(
    """
    <div class="app-header">
        <div class="app-title">智扫通 · 扫地机器人智能客服</div>
        <div class="app-subtitle">知识库问答 · 环境适配建议 · 个性化使用报告</div>
        <div>
            <span class="badge">Agentic RAG</span>
            <span class="badge">工具自主编排</span>
            <span class="badge">多轮上下文</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 快捷提问由按钮写入 pending，重跑后在下方统一处理
pending_prompt = st.session_state.pop("pending_prompt", None)
if pending_prompt:
    st.session_state["messages"].append({"role": "user", "content": pending_prompt})

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant" and message.get("steps"):
            with st.expander("查看执行过程", expanded=False):
                render_steps(message["steps"])
        st.markdown(message["content"])

if not st.session_state["messages"]:
    st.markdown(
        """
        <div class="welcome">
            <h2>你好，我是智扫通智能客服</h2>
            <p>可以问我扫地机器人的选购、使用、保养与故障问题，也能为你生成使用报告。</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    examples = [
        "我家是木地板，拖地后需要注意什么？",
        "扫地机器人在我所在地区的气温下如何保养？",
        "生成我本月的机器人使用报告",
        "小户型适合哪些扫地机器人？",
    ]
    columns = st.columns(2)
    for index, example in enumerate(examples):
        with columns[index % 2]:
            if st.button(example, key=f"example_{index}", use_container_width=True):
                st.session_state["pending_prompt"] = example
                st.rerun()

typed_prompt = st.chat_input("请输入您关于扫地机器人的问题…")

if typed_prompt:
    st.session_state["messages"].append({"role": "user", "content": typed_prompt})
    with st.chat_message("user"):
        st.markdown(typed_prompt)

run_prompt = typed_prompt or pending_prompt
if run_prompt:
    run_turn(run_prompt)
