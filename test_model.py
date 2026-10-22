import re
import json
from langchain_core.tools import tool
# 复用你项目的模型工厂，和原代码保持一致
from model.factory import chat_model


@tool
def get_local_temperature() -> str:
    """获取用户当前地区的实时气温，返回气温字符串"""
    print("\n===== [工具执行] get_local_temperature =====")
    return "28℃"

@tool
def get_robot_maintain_tips(temp: str) -> str:
    """根据传入的气温，返回扫地机器人保养建议，必须拿到气温后才可以调用"""
    print("\n===== [工具执行] get_robot_maintain_tips =====")
    return """
气温28℃保养要点：
1. 避免长时间暴晒充电；
2. 检查散热风口不要积灰；
3. 电池不要高温下持续回充。
"""

tool_map = {
    "get_local_temperature": get_local_temperature,
    "get_robot_maintain_tips": get_robot_maintain_tips
}


class ReactAgent:
    def __init__(self):
        self.system_prompt = """你是设备保养助手。
用户询问扫地机器人保养，你必须先调用 get_local_temperature 获取本地温度，
拿到温度结果之后，再调用 get_robot_maintain_tips，把温度传给它获取保养方案。
禁止直接编造气温、禁止直接回答。必须连续调用两个工具，两轮调用完成后再输出最终回答。

调用工具必须严格使用格式：
<tool_call>{"name": "工具名", "arguments": {"参数名":"参数值"}}</tool_call>
"""
        self.max_round = 5

    def execute_stream(self, query):
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query}
        ]

        for _ in range(self.max_round):
            resp = chat_model.invoke(messages)
            content = resp.content
            yield content.strip() + "\n"

            # 正则捕获 qwen 的 <tool_call>
            match = re.search(r"<tool_call>(.*?)</tool_call>", content, re.DOTALL)
            if not match:
                # 没有工具调用，代表最终回答，结束循环
                return

            try:
                call_data = json.loads(match.group(1))
                tool_name = call_data["name"]
                tool_args = call_data.get("arguments", {})
                tool_func = tool_map[tool_name]
                tool_result = tool_func.invoke(tool_args)
            except Exception as e:
                yield f"\n工具调用解析异常：{e}"
                return

            # 把工具返回追加进对话历史
            messages.append({"role": "assistant", "content": content})
            messages.append({"role": "tool", "content": str(tool_result)})


if __name__ == '__main__':
    agent = ReactAgent()
    print("==== 【手写ReAct版本】开始测试：扫地机器人保养 ====\n")
    for chunk in agent.execute_stream("扫地机器人在我所在的地区的气温下如何保养"):
        print(chunk, end="", flush=True)
