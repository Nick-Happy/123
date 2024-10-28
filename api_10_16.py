from flask import Flask, request, jsonify
import requests
import json
import uuid
import re
from bs4 import BeautifulSoup
import os
import pandas as pd
import time
import langid
import dateparser
from datetime import datetime, timedelta
from langchain.prompts import PromptTemplate
app = Flask(__name__)

# Rasa NLU API URL
rasa_nlu_url = "http://192.168.1.111:5000/parse_message"

# 外部 API URL
url_v1 = "http://192.168.1.111:5670/api/v2/chat/completions"

# 检测语言函数，只检测一次
def detect_language(message):
    try:
        lang, confidence = langid.classify(message)
        print('检测到的语言:', lang)
        return lang if lang in ['zh', 'ja', 'ko', 'en'] else 'en'
    except Exception:
        return 'en'

def get_error_message_template(language):
    error_templates = {
        "zh": "我暂时无法回答这个问题，请尝试提问其他问题。",
        "ja": "現在この質問にはお答えできません。別の質問をしてみてください。",
        "ko": "지금은 이 질문에 답할 수 없습니다. 다른 질문을 해보세요.",
        "en": "I can't answer this question right now, please try asking another one."
    }
    return error_templates.get(language, error_templates["en"])
         
def get_success_template(language):
    success_templates = {
        "zh": "以下是<strong>{adam_name}</strong>在<strong>{time_info}</strong>的数据。",
        "ja": "以下は<strong>{adam_name}</strong>の<strong>{time_info}</strong>におけるデータです。",
        "ko": "다음은 <strong>{adam_name}</strong>의 <strong>{time_info}</strong> 기간 동안의 데이터입니다.",
        "en": "Here is the data for <strong>{adam_name}</strong> during <strong>{time_info}</strong>."
    }
    return success_templates.get(language, success_templates["en"])

#调用 Rasa NLU API 进行意图识别和实体提取
def get_intent_and_entities(message):
    headers = {
        'Content-Type': 'application/json'
    }
    body = {"text": message}
    
    response = requests.post(rasa_nlu_url, headers=headers, json=body)
    if response.status_code == 200:
        return response.json()
    else:
        return None

@app.route('/chat', methods=['POST'])
def chat():
    client_payload = request.get_json()
    print('入参', client_payload)

    #接收的参数
    adam_id = client_payload.get('adam_id')
    adam_name = client_payload.get('adam_name')
    message = client_payload.get('message')
    print(adam_id, adam_name, message)

    # 在处理流程一开始就进行语言检测
    language = detect_language(message)  # 只检测一次语言

    #如果存在 adam_id, 则进行数据查询
    if adam_id:
        #获取意图和实体
        intent_entities = get_intent_and_entities(message)
        intent = intent_entities.get('intent')#获取意图
        entities = intent_entities.get('entities')#获取实体
        print(f"意图：{intent}")
        print(f"实体：{entities}")

        if intent == 'summary_query':
            time_entity = entities.get('time')
            return summary_data(client_payload,language,time_entity)
        elif intent == 'detail_query':
            time_entity = entities.get('time')
            return detail_data(client_payload,language,time_entity)
        elif intent == 'ranking_query_Keyword':
            time_entity = entities.get('time')
            return ranking_keyword(client_payload,language,time_entity)
        elif intent == 'ranking_query_Campaign':
            time_entity = entities.get('time')
            return ranking_campaign(client_payload,language,time_entity)
        elif intent == 'ranking_query_AdGroup':
            time_entity = entities.get('time')
            return ranking_adgroup(client_payload,language,time_entity)
        else:
            return knowledge_chat(client_payload,language)

    elif adam_id and (not message or not adam_name):
        return knowledge_chat(client_payload, language)

    else:
   
        return knowledge_chat(client_payload, language)


# 提取时间信息，并处理模糊时间表达
def get_month_date_range(year, month):
    """
    根据年份和月份返回对应的起始和结束日期，考虑不同月份的天数。
    """
    if month in {1, 3, 5, 7, 8, 10, 12}:  # 31天的月份
        end_day = 31
    elif month == 2:  # 处理二月，考虑闰年
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            end_day = 29
        else:
            end_day = 28
    else:  # 30天的月份
        end_day = 30
    return f'{year}-{month:02d}-01', f'{year}-{month:02d}-{end_day}'

def get_recent_days_range(days):
    """
    返回最近几天的日期范围，格式为 'YYYY-MM-DD' 到 'YYYY-MM-DD'。
    如果 days == 1，直接返回单个日期。
    """
    end_date = datetime.today()  # 当前日期作为结束日期
    if days == 1:
        return end_date.strftime('%Y-%m-%d')
    start_date = end_date - timedelta(days=days - 1)
    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def get_last_month_range():
    """
    返回上个月的开始日期和结束日期，格式为 'YYYY-MM-DD' 到 'YYYY-MM-DD'。
    """
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_last_month = first_day_this_month - timedelta(days=1)
    first_day_last_month = last_day_last_month.replace(day=1)
    return first_day_last_month.strftime('%Y-%m-%d'), last_day_last_month.strftime('%Y-%m-%d')

def get_last_week_range():
    """
    返回上周的开始日期（星期一）和结束日期（星期日），格式为 'YYYY-MM-DD' 到 'YYYY-MM-DD'。
    """
    today = datetime.today()
    # 计算本周的星期一
    start_of_this_week = today - timedelta(days=today.weekday())
    # 上周的星期一是本周星期一减去7天
    start_of_last_week = start_of_this_week - timedelta(days=7)
    # 上周的星期日是上周星期一加6天
    end_of_last_week = start_of_last_week + timedelta(days=6)
    
    return start_of_last_week.strftime('%Y-%m-%d'), end_of_last_week.strftime('%Y-%m-%d')

def get_now_time_range():
    now = datetime.now()
    start_time = now.replace(day=1)
    end_time = now
    return start_time.strftime('%Y-%m-%d'), end_time.strftime('%Y-%m-%d')

def get_current_week_to_now_time_range():
    # 获取当前时间
    now = datetime.now()

    # 获取本周的开始时间（星期一）
    start_date = now - timedelta(days=now.weekday())

    # 结束时间为当前时间
    end_date = now

    return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')

def get_month_start_and_end_from_string(month_str: str):
    # 使用正则表达式提取中文数字月份（'一月' 到 '十二月'）
    month_map = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10, '十一': 11, '十二': 12
    }
    
    # 匹配类似'八月份'的字符串
    match = re.match(r'([一二三四五六七八九十十一十二]+)月份', month_str)
    if match:
        month_cn = match.group(1)  # 提取中文月份部分
        month = month_map.get(month_cn, None)  # 将中文转换为数字月份
        
        if month:
            # 获取当前年份
            year = datetime.now().year
            
            # 获取月份的开始日期
            start_date = datetime(year, month, 1)
            
            # 获取月份的结束日期
            _, last_day = calendar.monthrange(year, month)
            end_date = datetime(year, month, last_day, 23, 59, 59)
            
            return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
        else:
            raise ValueError(f"无法识别的月份: {month_str}")
    else:
        raise ValueError(f"输入格式错误，应该是'X月份'，如'八月份'")

def extract_time_info(time_entity):
    """
    根据 Rasa NLU 提取到的时间实体来修改 message 中的时间表达，支持中文、日文、韩文和英文。
    如果时间实体中直接包含日期或日期区间，则直接返回这些信息。
    """
    # 日期区间正则表达式 (处理日期范围)
    date_range_patterns = [
        r'(\d{4})年(\d{1,2})月(\d{1,2})日到(\d{4})年(\d{1,2})月(\d{1,2})日',  # 中文
        r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4}),?\s+(?:to|and)\s+([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4}),?',  # 英文
        r'(\d{4})년 (\d{1,2})월 (\d{1,2})일부터 (\d{4})년 (\d{1,2})월 (\d{1,2})일',  # 韩文
        r'(\d{4})년 (\d{1,2})월 (\d{1,2})일부터 (\d{1,2})월 (\d{1,2})일',
        r'^\s*(\d{4})年(\d{1,2})月(\d{1,2})日から(\d{1,2})月(\d{1,2})日まで\s*$',
        r'(\d{4})年(\d{1,2})月(\d{1,2})日から(\d{4})年(\d{1,2})月(\d{1,2})日',  # 日文
        r'(\d{4})-(\d{2})-(\d{2})\s*到\s*(\d{4})-(\d{2})-(\d{2})'
    ]
    
    for pattern in date_range_patterns:
        date_range_match = re.search(pattern, time_entity)
        if date_range_match:
            # 如果是英文日期，处理月份
            if pattern == date_range_patterns[1]:  
                try:
                    start_date = datetime.strptime(f"{date_range_match.group(3)} {date_range_match.group(1)} {date_range_match.group(2)}", '%Y %B %d').strftime('%Y-%m-%d')
                    end_date = datetime.strptime(f"{date_range_match.group(6)} {date_range_match.group(4)} {date_range_match.group(5)}", '%Y %B %d').strftime('%Y-%m-%d')
                except ValueError:
                    # 如果月份是缩写 (Jan, Feb等)，改用缩写的解析
                    start_date = datetime.strptime(f"{date_range_match.group(3)} {date_range_match.group(1)} {date_range_match.group(2)}", '%Y %b %d').strftime('%Y-%m-%d')
                    end_date = datetime.strptime(f"{date_range_match.group(6)} {date_range_match.group(4)} {date_range_match.group(5)}", '%Y %b %d').strftime('%Y-%m-%d')
            else:
                # 其他语言日期格式的处理
                year1 = date_range_match.group(1)
                month1 = int(date_range_match.group(2))
                day1 = int(date_range_match.group(3))

                if len(date_range_match.groups()) == 6:
                    year2 = date_range_match.group(4)
                    month2 = int(date_range_match.group(5))
                    day2 = int(date_range_match.group(6))
                else:
                    # 如果结束日期没有年份，使用起始年份
                    year2 = year1
                    month2 = int(date_range_match.group(4))
                    day2 = int(date_range_match.group(5))

                # 格式化日期
                start_date = f"{year1}-{month1:02}-{day1:02}"
                end_date = f"{year2}-{month2:02}-{day2:02}"

            return f'{start_date}~{end_date}'
    
    # 单个日期正则表达式 (多语言支持)
    single_date_patterns = [
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # 中文
        r'(\w+) (\d{1,2}), (\d{4})',  # 英文
        r'(\d{4})년 (\d{1,2})월 (\d{1,2})일',  # 韩文
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # 日文
        r'(\d{4})-(\d{2})-(\d{2})\s*'
    ]
    
    for pattern in single_date_patterns:
        single_date_match = re.search(pattern, time_entity)
        if single_date_match:
            if pattern == single_date_patterns[1]:  # 英文处理月名
                single_date = datetime.strptime(f"{single_date_match.group(3)} {single_date_match.group(1)} {single_date_match.group(2)}", '%Y %B %d').strftime('%Y-%m-%d')
                return f'{single_date}'
            else:
                single_date = f"{single_date_match.group(1)}-{int(single_date_match.group(2)):02}-{int(single_date_match.group(3)):02}"
                return f'{single_date}'

    today = datetime.today().strftime('%Y-%m-%d')
    
    # 使用时间实体返回相应的日期范围
    if time_entity in ["最近一个月","近一个月", "近30天","最近30天","30天","last 30 days","past month","最近1ヶ月", "過去1ヶ月","最近30日間","過去30日間","過去1ヶ月間","過去1か月","최근 1개월","지난 한 달","최근 30일","지난 1개월","최근 한 달","지난 30일"]:
        start_date, end_date = get_recent_days_range(30)
        return f'{start_date}~{end_date}'

    elif time_entity in ["一月份","二月份","三月份","四月份","五月份","六月份","七月份","八月份","九月份","十月份","十一月份","十二月份"]:
        start_date, end_date = get_month_start_and_end_from_string(time_entity)
        return f'{start_date}~{end_date}'
    
    elif time_entity in ["本月","这个月","这月","this month", "this month's","이번 달","今月"]:
        start_date, end_date = get_now_time_range()
        return f'{start_date}~{end_date}'

    elif time_entity in ["本周","这个周","这周","this week", "this week's","이번 주","今週"]:
        start_date, end_date = get_current_week_to_now_time_range()
        return f'{start_date}~{end_date}'
        
    elif time_entity in ["上周", "上个星期", "지난주", "지난 주","先週", "last week", "last week's","past week"]:
        start_date, end_date = get_last_week_range()
        return f'{start_date}~{end_date}'
    
    elif time_entity in ["上个月", "上月", "过去一个月","지난달", "지난 달","先月", "last month", "last month's","past month"]:
        start_date, end_date = get_last_month_range()
        return f'{start_date}~{end_date}'
    
    elif time_entity in ["最近一天", "最近1天", "最近(1|一)天", "近一天", "近1天","최근 하루","최근 1일","過去1日間","過去1日","last day","past day"]:
        return f'{today}'

    elif time_entity in ["最近两天", "最近2天", "最近(2|二)天", "近两天", "近2天","최근 이틀","최근 2일","지난 2일","last two days","past two days","過去2日","過去2日間"]:
        start_date, end_date = get_recent_days_range(2)
        return f'{start_date}~{end_date}'

    elif time_entity in ["最近三天", "最近3天", "最近(3|三)天", "近三天", "近3天","최근 사흘","최근 3일","최근 3일간","지난 3일","last three days","past three days","過去3日","過去3日間"]:
        start_date, end_date = get_recent_days_range(3)
        return f'{start_date}~{end_date}'

    elif time_entity in ["最近一周", "近一周", "近7天","近七天" ,"近一星期", "最近7天", "最近七天","last week","past week", "last seven days", "최근 일주일","지난 7일","최근 7일","최근 일주일간","最近1週間","過去7日間","直近1週間","過去7日"]:
        start_date, end_date = get_recent_days_range(7)
        return f'{start_date}~{end_date}'

    elif time_entity in ["近几天", "近几日","几天","past few days"]:
        start_date, end_date = get_recent_days_range(3)  # 默认处理为最近三天
        return f'{start_date}~{end_date}'

    elif time_entity == "最近" or re.search(r'最近|recently|최근|直近|latest|recent', time_entity):
        start_date, end_date = get_recent_days_range(7)  # 默认处理为最近一周
        return f'{start_date}~{end_date}'

    month_pattern = r'(\d{1,2})月份|(\d{1,2})月|(\d{1,2})달|(\d{1,2}) month'
    month_match = re.search(month_pattern, time_entity)
    if month_match:
        month = int(month_match.group(1) or month_match.group(2) or month_match.group(3) or month_match.group(4))
        year = datetime.today().year
        if 1 <= month <= 12:
            start_date, end_date = get_month_date_range(year, month)
            return f'{start_date}至{end_date}'

    if re.search(r'昨天|어제|昨日|yesterday', time_entity):
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        return f'{yesterday}'

    return None, None

def get_time_on_entity(time_entity):
    """
    根据 Rasa NLU 提取到的时间实体来修改 message 中的时间表达，支持中文、日文、韩文和英文。
    如果时间实体中直接包含日期或日期区间，则直接返回这些信息。
    """
    # 日期区间正则表达式 (处理日期范围)
    date_range_patterns = [
        r'(\d{4})年(\d{1,2})月(\d{1,2})日到(\d{4})年(\d{1,2})月(\d{1,2})日',  # 中文
        r'([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4}),?\s+(?:to|and)\s+([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4}),?',  # 英文
        r'(\d{4})년 (\d{1,2})월 (\d{1,2})일부터 (\d{4})년 (\d{1,2})월 (\d{1,2})일',  # 韩文
        r'(\d{4})년 (\d{1,2})월 (\d{1,2})일부터 (\d{1,2})월 (\d{1,2})일',
        r'^\s*(\d{4})年(\d{1,2})月(\d{1,2})日から(\d{1,2})月(\d{1,2})日まで\s*$',
        r'(\d{4})年(\d{1,2})月(\d{1,2})日から(\d{4})年(\d{1,2})月(\d{1,2})日',  # 日文
        r'(\d{4})-(\d{2})-(\d{2})\s*到\s*(\d{4})-(\d{2})-(\d{2})'
    ]

    for pattern in date_range_patterns:
        date_range_match = re.search(pattern, time_entity)
        if date_range_match:
            # 如果是英文日期，处理月份
            if pattern == date_range_patterns[1]:  
                try:
                    start_date = datetime.strptime(f"{date_range_match.group(3)} {date_range_match.group(1)} {date_range_match.group(2)}", '%Y %B %d').strftime('%Y-%m-%d')
                    end_date = datetime.strptime(f"{date_range_match.group(6)} {date_range_match.group(4)} {date_range_match.group(5)}", '%Y %B %d').strftime('%Y-%m-%d')
                except ValueError:
                    # 如果月份是缩写 (Jan, Feb等)，改用缩写的解析
                    start_date = datetime.strptime(f"{date_range_match.group(3)} {date_range_match.group(1)} {date_range_match.group(2)}", '%Y %b %d').strftime('%Y-%m-%d')
                    end_date = datetime.strptime(f"{date_range_match.group(6)} {date_range_match.group(4)} {date_range_match.group(5)}", '%Y %b %d').strftime('%Y-%m-%d')
            else:
                # 其他语言日期格式的处理
                year1 = date_range_match.group(1)
                month1 = int(date_range_match.group(2))
                day1 = int(date_range_match.group(3))

                if len(date_range_match.groups()) == 6:
                    year2 = date_range_match.group(4)
                    month2 = int(date_range_match.group(5))
                    day2 = int(date_range_match.group(6))
                else:
                    # 如果结束日期没有年份，使用起始年份
                    year2 = year1
                    month2 = int(date_range_match.group(4))
                    day2 = int(date_range_match.group(5))

                # 格式化日期
                start_date = f"{year1}-{month1:02}-{day1:02}"
                end_date = f"{year2}-{month2:02}-{day2:02}"

            return start_date, end_date
    
    # 单个日期正则表达式 (多语言支持)
    single_date_patterns = [
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # 中文
        r'(\w+) (\d{1,2}), (\d{4})',  # 英文
        r'(\d{4})년 (\d{1,2})월 (\d{1,2})일',  # 韩文
        r'(\d{4})年(\d{1,2})月(\d{1,2})日',  # 日文
        r'(\d{4})-(\d{2})-(\d{2})\s*'
    ]
    
    for pattern in single_date_patterns:
        single_date_match = re.search(pattern, time_entity)
        if single_date_match:
            if pattern == single_date_patterns[1]:  # 英文处理月名
                single_date = datetime.strptime(f"{single_date_match.group(3)} {single_date_match.group(1)} {single_date_match.group(2)}", '%Y %B %d').strftime('%Y-%m-%d')
                return single_date, single_date
            else:
                single_date = f"{single_date_match.group(1)}-{int(single_date_match.group(2)):02}-{int(single_date_match.group(3)):02}"
                return single_date, single_date

    today = datetime.today().strftime('%Y-%m-%d')
    
    # # 使用时间实体返回相应的日期范围
    if time_entity in ["最近一个月","近一个月", "近30天","最近30天","30天","last 30 days","past month","最近1ヶ月", "過去1ヶ月","最近30日間","過去30日間","過去1ヶ月間","過去1か月","최근 1개월","지난 한 달","최근 30일","지난 1개월","최근 한 달","지난 30일"]:
        start_date, end_date = get_recent_days_range(30)
        return start_date, end_date

    elif time_entity in ["一月份","二月份","三月份","四月份","五月份","六月份","七月份","八月份","九月份","十月份","十一月份","十二月份"]:
        start_date, end_date = get_month_start_and_end_from_string(time_entity)
        return start_date, end_date

    elif time_entity in ["本月","这个月","这月","this month", "this month's","이번 달","今月"]:
        start_date, end_date = get_now_time_range()
        return start_date, end_date

    elif time_entity in ["本周","这个周","这周","this week", "this week's","이번 주","今週"]:
        start_date, end_date = get_current_week_to_now_time_range()
        return start_date, end_date
    
    elif time_entity in ["上周", "上个星期", "지난주", "지난 주","先週", "last week", "last week's"]:
        start_date, end_date = get_last_week_range()
        return start_date, end_date

    elif time_entity in ["上个月", "上月","过去一个月", "지난달", "지난 달","先月", "last month", "last month's"]:
        start_date, end_date = get_last_month_range()
        return start_date, end_date
    
    elif time_entity in ["最近一天", "最近1天", "最近(1|一)天", "近一天", "近1天","최근 하루","최근 1일","過去1日間","過去1日","last day","past day"]:
        return today, today

    elif time_entity in ["最近两天", "最近2天", "最近(2|二)天", "近两天", "近2天","최근 이틀","최근 2일","지난 2일","last two days","past two days","過去2日","過去2日間"]:
        start_date, end_date = get_recent_days_range(2)
        return start_date, end_date

    elif time_entity in ["最近三天", "最近3天", "最近(3|三)天", "近三天", "近3天","최근 사흘","최근 3일","최근 3일간","지난 3일","last three days","past three days","過去3日","過去3日間"]:
        start_date, end_date = get_recent_days_range(3)
        return start_date, end_date

    elif time_entity in ["最近一周", "近一周", "近7天","近七天" ,"近一星期", "最近7天", "最近七天","last week","past week", "last seven days", "최근 일주일","지난 7일","최근 7일","최근 일주일간","最近1週間","過去7日間","直近1週間","過去7日"]:
        start_date, end_date = get_recent_days_range(7)
        return start_date, end_date

    elif time_entity in ["近几天", "近几日","几天","past few days"]:
        start_date, end_date = get_recent_days_range(3)  # 默认处理为最近三天
        return start_date, end_date

    elif time_entity == "最近" or re.search(r'最近|recently|최근|直近|latest|recent', time_entity):
        start_date, end_date = get_recent_days_range(7)  # 默认处理为最近一周
        return start_date, end_date


    month_pattern = r'(\d{1,2})月份|(\d{1,2})月|(\d{1,2})달|(\d{1,2}) month'
    month_match = re.search(month_pattern, time_entity)
    if month_match:
        month = int(month_match.group(1) or month_match.group(2) or month_match.group(3) or month_match.group(4))
        year = datetime.today().year
        if 1 <= month <= 12:
            start_date, end_date = get_month_date_range(year, month)
            return start_date, end_date

    if re.search(r'昨天|어제|昨日|yesterday', time_entity):
        yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')
        return yesterday, yesterday

    return None, None

def summary_data(client_payload, language, time_entity):
    try:
        #time_entity异常捕获
        # if time_entity is None:
        #     raise ValueError("时间识别为空")

        message = client_payload.get('message')
        adam_name = client_payload.get("adam_name")
        time_start_end = get_time_on_entity(time_entity)
        #time_entity异常捕获
        if time_start_end:
            start_date, end_date = time_start_end
        else:
            start_date, end_date = None, None

        # time_info 用于界面时间展示
        time_info = extract_time_info(time_entity)
        print(time_info)
        success_message_template = get_success_template(language)
        new_message = success_message_template.format(adam_name=adam_name, time_info=time_info)
        response_data = {
            "type": 1,
            "message": new_message,
            "data": {
                "start_date": start_date,
                "end_date": end_date
            },
            "language":language
        }
        print(f"response_data:{response_data}")
        return jsonify(response_data)

    # except ValueError as e:
    #     #捕获ValueError并返回错误
    #     error_message = str(e)
    #     error_response = {
    #         "type": 0,
    #         "message": error_message,
    #         "data": {}
    #     }
    #     return jsonify(error_response)

    except Exception as e:
        # 如果在处理过程中出现任何异常，返回一个错误消息
        error_message = get_error_message_template(language)
        error_response = {
            "type": 0,
            "message": error_message,
            "data": {}
        }
        return jsonify(error_response)

def detail_data(client_payload, language, time_entity):
    try:
        #time_entity异常捕获
        # if time_entity is None:
        #     raise ValueError("时间识别为空")
        message = client_payload.get('message')
        adam_name = client_payload.get("adam_name")
        time_start_end = get_time_on_entity(time_entity)
        
        if time_start_end:
            start_date, end_date = time_start_end
        else:
            start_date, end_date = None, None
 
        # time_info 用于界面时间展示
        time_info = extract_time_info(time_entity)
        success_message_template = get_success_template(language)
        new_message = success_message_template.format(adam_name=adam_name, time_info=time_info)
        print(f"new_message:{new_message}")
        response_data = {
            "type": 2,
            "message": new_message,
            "data": {
                "start_date": start_date,
                "end_date": end_date
            },
            "language":language
        }
        print(f"response_data:{response_data}")
        return jsonify(response_data)
    
    # except ValueError as e:
    #     #捕获ValueError并返回错误
    #     error_message = str(e)
    #     error_response = {
    #         "type": 0,
    #         "message": error_message,
    #         "data": {}
    #     }
    #     return jsonify(error_response)

    except Exception as e:
        # 捕获异常并返回错误信息
        error_message = get_error_message_template(language)
        error_response = {
            "type": 0,
            "message": error_message,
            "data": {}
        }
        return jsonify(error_response)


def ranking_keyword(client_payload, language, time_entity):
    try:
        # if time_entity is None:
        #     raise ValueError("时间识别为空")
        message = client_payload.get('message')
        adam_name = client_payload.get("adam_name")
        time_start_end = get_time_on_entity(time_entity)

        if time_start_end:
            start_date, end_date = time_start_end
        else:
            start_date, end_date = None, None
        
        entities = get_intent_and_entities(message)
        print("开始_结束时间",time_start_end)
        print("意图_实体",entities)
        #{'entities': {'impressions': None, 'install': None, 'limit': '10', 'spend': '消耗', 'taps': None, 'time': '2024年12月19日'}, 'intent': 'ranking_query_Keyword'}
        limit = entities['entities']['limit']
        # 检查 limit 是否为 None
        if limit is not None:
            limit = int(limit)
        else:
            limit = 10  # 例如设置默认值为 10
        impressions = entities['entities']['impressions']
        install = entities['entities']['install']
        spend = entities['entities']['spend']
        taps = entities['entities']['taps']
        print(type(limit))
        # 根据 impressions, install, spend, taps 的值设置 sort
        if impressions and not install and not spend and not taps:
            sort = 1
        elif install and not impressions and not spend and not taps:
            sort = 3
        elif spend and not impressions and not install and not taps:
            sort = 4
        elif taps and not impressions and not install and not spend:
            sort = 2
        else:
            sort = 0  # 如果多个值都有或者都没有，默认给一个值，比如 0

        # time_info 用于界面时间展示
        time_info = extract_time_info(time_entity)
        print(time_info)
        success_message_template = get_success_template(language)
        new_message = success_message_template.format(adam_name=adam_name, time_info=time_info)
        print(f"new_message:{new_message}")
        response_data = {
            "type":3,
            "message":new_message,
            "data":{
                "start_date":start_date,
                "end_date":end_date,
                "limit":limit,
                "sort":sort
            },
            "language":language
        }
        print(f"response_data:{response_data}")
        return jsonify(response_data)
        
    # except ValueError as e:
    #     #捕获ValueError并返回错误
    #     error_message = str(e)
    #     error_response = {
    #         "type": 0,
    #         "message": error_message,
    #         "data": {}
    #     }
    #     return jsonify(error_response)

    except Exception as e:
        error_message = get_error_message_template(language)
        error_response = {
            "type": 0,
            "message": error_message,
            "data": {}
        }
        return jsonify(error_response)

def ranking_campaign(client_payload, language, time_entity):
    try:
        # if time_entity is None:
        #     raise ValueError("时间识别为空")
        message = client_payload.get('message')
        adam_name = client_payload.get("adam_name")
        time_start_end = get_time_on_entity(time_entity)
        if time_start_end:
            start_date, end_date = time_start_end
        else:
            start_date, end_date = None, None
        
        entities = get_intent_and_entities(message)
        print("开始_结束时间",time_start_end)
        print("意图_实体",entities)
        #{'entities': {'impressions': None, 'install': None, 'limit': '10', 'spend': '消耗', 'taps': None, 'time': '2024年12月19日'}, 'intent': 'ranking_query_Keyword'}
        limit = entities['entities']['limit']
        if limit is not None:
            limit = int(limit)
        else:
            limit = 10  # 例如设置默认值为 10
        impressions = entities['entities']['impressions']
        install = entities['entities']['install']
        spend = entities['entities']['spend']
        taps = entities['entities']['taps']
        print(limit)
        # 根据 impressions, install, spend, taps 的值设置 sort
        if impressions and not install and not spend and not taps:
            sort = 1
        elif install and not impressions and not spend and not taps:
            sort = 3
        elif spend and not impressions and not install and not taps:
            sort = 4
        elif taps and not impressions and not install and not spend:
            sort = 2
        else:
            sort = 0  # 如果多个值都有或者都没有，默认给一个值，比如 0

        # time_info 用于界面时间展示
        time_info = extract_time_info(time_entity)
        print(time_info)
        success_message_template = get_success_template(language)
        new_message = success_message_template.format(adam_name=adam_name, time_info=time_info)
        print(f"new_message:{new_message}")
        response_data = {
            "type":4,
            "message":new_message,
            "data":{
                "start_date":start_date,
                "end_date":end_date,
                "limit":limit,
                "sort":sort
            },
            "language":language
        }
        print(f"response_data:{response_data}")
        return jsonify(response_data)

    # except ValueError as e:
    #     #捕获ValueError并返回错误
    #     error_message = str(e)
    #     error_response = {
    #         "type": 0,
    #         "message": error_message,
    #         "data": {}
    #     }
    #     return jsonify(error_response)

    except Exception as e:
        error_message = get_error_message_template(language)
        error_response = {
            "type": 0,
            "message": error_message,
            "data": {}
        }
        return jsonify(error_response)
def ranking_adgroup(client_payload, language, time_entity):
    try:
        # if time_entity is None:
        #     raise ValueError("时间识别为空")

        message = client_payload.get('message')
        adam_name = client_payload.get("adam_name")
        time_start_end = get_time_on_entity(time_entity)
        if time_start_end:
            start_date, end_date = time_start_end
        else:
            start_date, end_date = None, None
        
        entities = get_intent_and_entities(message)
        print("开始_结束时间",time_start_end)
        print("意图_实体",entities)
        #{'entities': {'impressions': None, 'install': None, 'limit': '10', 'spend': '消耗', 'taps': None, 'time': '2024年12月19日'}, 'intent': 'ranking_query_Keyword'}
        limit = entities['entities']['limit']
        if limit is not None:
            limit = int(limit)
        else:
            limit = 10  # 例如设置默认值为 10
        impressions = entities['entities']['impressions']
        install = entities['entities']['install']
        spend = entities['entities']['spend']
        taps = entities['entities']['taps']
        print(limit)
        # 根据 impressions, install, spend, taps 的值设置 sort
        if impressions and not install and not spend and not taps:
            sort = 1
        elif install and not impressions and not spend and not taps:
            sort = 3
        elif spend and not impressions and not install and not taps:
            sort = 4
        elif taps and not impressions and not install and not spend:
            sort = 2
        else:
            sort = 0  # 如果多个值都有或者都没有，默认给一个值，比如 0

        # time_info 用于界面时间展示
        time_info = extract_time_info(time_entity)
        success_message_template = get_success_template(language)
        new_message = success_message_template.format(adam_name=adam_name, time_info=time_info)
        print(f"new_message:{new_message}")
        response_data = {
            "type":5,
            "message":new_message,
            "data":{
                "start_date":start_date,
                "end_date":end_date,
                "limit":limit,
                "sort":sort
            },
            "language":language
        }
        print(f"response_data:{response_data}")
        return jsonify(response_data)

    # except ValueError as e:
    #     #捕获ValueError并返回错误
    #     error_message = str(e)
    #     error_response = {
    #         "type": 0,
    #         "message": error_message,
    #         "data": {}
    #     }
    #     return jsonify(error_response)

    except Exception as e:
        error_message = get_error_message_template(language)
        error_response = {
            "type": 0,
            "message": error_message,
            "data": {}
        }
        return jsonify(error_response)

def knowledge_chat(client_payload, language):
    message = client_payload.get("message")
    
    if language == 'en':
        chat_param = '123_en'
        lang_class = '英语'
    elif language == 'ja':
        chat_param = '123_ja'
        lang_class = '日语'
    elif language == 'ko':
        chat_param = '123_ko'
        lang_class = '韩语'
    elif language == 'zh':
        chat_param = '123'
        lang_class = '中文'
    else:
        chat_param = '123'
        lang_class = '英语' 

    text = """{message},请用{lang_class}回答"""
    prompt = PromptTemplate.from_template(text)
    prompt = prompt.format(lang_class=lang_class,message=message)
    print(f'prompt:{prompt}')
    if language == 'en':
        message = prompt
    else:
        message =message
    conv_uid_2 = str(uuid.uuid4())
    url = url_v1
    payload = {
        "model": "ollama_proxyllm",
        "messages": message,
        "stream": 'false',
        "temperature": 0,
        "max_new_tokens": 0,
        "conv_uid": conv_uid_2,
        "span_id": "string",
        "chat_mode": "chat_knowledge",
        "chat_param": chat_param
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()

        content = data.get("choices", [])[0].get("message", {}).get("content", "")
        print(f"content: {content}")

        if not content:
            error_message_template = get_error_message_template(language)
            return jsonify({
                "status": False,
                "message": error_message_template,
                "type":0
            }), 404

        # 返回成功信息
        message_response = content.replace("\\n", "\n")
        return jsonify({
            "status": True,
            "type":0,
            "message": message_response,
            "language":language
        }), 200

    except requests.exceptions.RequestException:
        error_message_template = get_error_message_template(language)
        return jsonify({
            "status": False,
            "type":0,
            "message": error_message_template,
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True)
