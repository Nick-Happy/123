
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

