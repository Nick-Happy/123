
import os
import qianfan
from langchain.prompts import PromptTemplate
import re
# 替换下列示例中参数，安全认证Access Key替换your_iam_ak，Secret Key替换your_iam_sk，如何获取请查看https://cloud.baidu.com/doc/Reference/s/9jwvz2egb
os.environ["QIANFAN_ACCESS_KEY"] = ""
os.environ["QIANFAN_SECRET_KEY"] = ""
#实例化模型
chat_comp = qianfan.ChatCompletion()
#提示词
prompt = PromptTemplate.from_template("现在你是一个意图识别专家,意图类别信息有(ASA聊天)和(数据查询)为了能够更加准确的得到我想要的结果所以对你做出一些约束:1.你要充分理解用户的问题,然后判断他是以上那种意图,并且只输出意图类别信息。2.输出结果要简洁明了,例如以下模板:问:广告投放的方式有哪些?答:ASA聊天问:帮我查询xxx时间段的xxx产品的投放数据?答:数据查询以下是用户的问题:{message}")
messages = '你是谁'
prompt = prompt.format(message=messages)
#message
messages=[{
    "role": "user",
    "content": prompt,
}]
# 指定特定模型
resp = chat_comp.do(model="ERNIE-Speed-128K", messages=messages)
#模型回答结果
angser = resp['body']['result']
print(angser)
#正则进行意图分类
if re.search('ASA聊天', angser):
    print('chat_rag')
else:
    print('chat_DB')




# pip install zhipuai 请先在终端进行安装

from zhipuai import ZhipuAI

client = ZhipuAI(api_key="")

prompt = PromptTemplate.from_template("现在你是一个意图识别专家,意图类别信息有(ASA聊天)和(数据查询)为了能够更加准确的得到我想要的结果所以对你做出一些约束:1.你要充分理解用户的问题,然后判断他是以上那种意图,并且只输出意图类别信息。2.输出结果要简洁明了,例如以下模板:问:广告投放的方式有哪些?答:ASA聊天问:帮我查询xxx时间段的xxx产品的投放数据?答:数据查询以下是用户的问题:{message}")
messages = '你是谁'
prompt = prompt.format(message=messages)


messages=[
        {
            "role": "system",
            "content": "你是一个意图识别专家,意图类别信息有(ASA聊天)和(数据查询)" 
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

response = client.chat.completions.create(model="glm-4-flash",messages=messages,top_p= 0.7,temperature= 0.95,max_tokens=1024,tools = [{"type":"web_search","web_search":{"search_result":True}}],stream=False)
content = response.choices[0].message.content
print(content)

############################################################################################################################################################################################################################################
def intention():
    client_payload = request.get_json()  # 从请求体中获得JSON数据
    print('入参',client_payload)
    #{'country': 'IN', 'adam_id': '1471102783', 'message': '查询2024-07-01投放的关键词数据是'}
     #实例化模型
    client = ZhipuAI(api_key="")
    #提示词
    text = """
        现在你是一个意图识别专家。你的任务是根据用户的问题，将其归类为“知识库查询”或“数据库查询”。为了确保准确判断，请遵循以下策略：
        判断策略
        1.关键词识别：
            知识库查询：
            关注日常聊天、知识、概念、定义、操作步骤等问题。
            关键词包括：你好、你能做什么、你好啊、什么是、如何、为什么、定义、解释、方式、方法、用途、例子等。
            数据库查询：
            关注具体的数据查询、统计、报告或分析。
            关键词包括：查询、获取、统计、数据、报告、日期、时间段、记录、历史、特定条件等。
        2.时间与条件：
            数据库查询：
            通常涉及特定的时间段、日期或其他条件(如“查询2024年7月的数据”)。
            知识库查询：
            通常不涉及具体的时间段或条件。
        3.操作意图：
            知识库查询：
            意图是获取信息或知识，而非操作数据库。
            数据库查询：
            意图是进行数据操作或获取特定的数据库信息。
        示例判断
        示例 1:
        问题: “什么是ASA广告投放?”
        判断: 这是一个询问ASA广告投放定义的问题,属于知识库查询。
        示例 2:
        问题: “帮我查询2024年7月的广告投放数据。”
        判断: 这是一个具体的数据查询问题，涉及特定的时间段，属于数据库查询。
        示例 3:
        问题: “如何优化我的广告投放策略？”
        判断: 这是一个关于优化策略的询问，属于知识库查询。
        示例 4:
        问题: “获取过去一个月的销售数据。”
        判断: 这是一个请求特定时间段数据的问题，属于数据库查询。
        以下是用户的问题请根据用户的问题进行合理回答：
        {message}
    """

    prompt = PromptTemplate.from_template(text)
    messages = client_payload['message']
    prompt = prompt.format(message=messages)
    #message
    messages=[
            {
                "role": "system",
                "content": "你是一个意图识别专家,意图类别信息有(ASA聊天)和(数据查询)" 
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    # 指定特定模型
    response = client.chat.completions.create(model="glm-4-flash",messages=messages,top_p= 0.7,temperature= 0.95,max_tokens=1024,tools = [{"type":"web_search","web_search":{"search_result":True}}],stream=False)
    #模型回答结果
    angser = response.choices[0].message.content
    # print(angser)
    #正则进行意图分类
    if re.search('知识库查询', angser):
        intention = 'chat_RAG'
        print(f"意图类别是{intention}")
        return intention
    else:
        intention = 'chat_DB'
        print(f"意图类别是{intention}")
        return intention






