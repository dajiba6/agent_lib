from openai import OpenAI
import yaml
import os
import json

# --------------------------------------------------------------
# 读取配置
# --------------------------------------------------------------
config_file_path = os.path.join(os.path.dirname(__file__), "..", "config.yaml")
with open(config_file_path, "r") as config_file:
    config = yaml.safe_load(config_file)
    api_key = config.get("DEEPSEEK_API_KEY")
    base_url = config.get("DEEPSEEK_BASE_URL")

client = OpenAI(api_key=api_key, base_url=base_url)


# --------------------------------------------------------------
# 定义函数:知识库搜索-fake
# --------------------------------------------------------------
def search_kb(question: str):
    with open("kb.json", "r") as f:
        return json.load(f)


# --------------------------------------------------------------
# 定义工具
# --------------------------------------------------------------
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_kb",
            "description": "从知识库中搜取信息，用于回答用户问题",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string"},
                },
                "required": ["question"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

# --------------------------------------------------------------
# 第一次请求：工具调用
# --------------------------------------------------------------
system_prompt = "你是一个人工智能助手"
user_prompt = "根据我知识库中的内容告诉我魔丸的信息，要快！"

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
]

compeletion = client.chat.completions.create(
    model="deepseek-chat",
    messages=messages
    tools=tools,
)

print(f"result1: \n{compeletion.model_dump()}")
# --------------------------------------------------------------
# 工具调用
# --------------------------------------------------------------

def call_function(name,args):
    if name == "search_kb":
        return search_kb(**args)
    
for tool_call in compeletion.choices[0].message.tool_calls:
    name = tool_call.function.name
    args = json.loads(tool_call.function.arguments)
    messages.append(compeletion.choices[0].message)

    result = call_function(name)
    messages.append(
        {"role":"tool","took_call_id":tool_call.id,"content":json.dump(result)}
    )

# --------------------------------------------------------------
# 第一次请求：最终回答生成
# --------------------------------------------------------------
structure1 = """
请以下面格式输出内容

example input:
{
  "name": "魔丸",
  "hight": "1.4米",
  "personality": "恐怖的小孩"
}
example output:
{
  "name": "魔丸"
  "content": "这是一个名叫魔丸的恐怖小孩，千万不要接近它！"
}
"""
