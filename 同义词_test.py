from transformers import BertTokenizer, BertModel
import torch
from langdetect import detect
import jieba
import jieba.analyse
import torch.nn.functional as F
import spacy
from sudachipy import dictionary, tokenizer
import requests
from bs4 import BeautifulSoup
from  cutword import Cutter


# url = "https://apps.apple.com/DE/app/6446616309"
# def get_data_from_url(url):
#     # try:
#     response = requests.get(url)
#     response.encoding='utf-8'
#     html_content = response.text     
#     # 使用BeautifulSoup解析HTML
#     soup = BeautifulSoup(html_content, 'html.parser')
#     title_tag = soup.find("h1", class_="product-header__title app-header__title")
#     title_tag = title_tag.text.strip().split('\n')[0] if title_tag else None # .split('\n')[0]
#     subtitle_tag = soup.find("h2", class_="product-header__subtitle app-header__subtitle")
#     subtitle_tag = subtitle_tag.text.strip() if subtitle_tag else None
#     description_tag = soup.find( "div", class_="section__description")
#     description_tag = description_tag.text.strip().replace('\n',' ') if description_tag else None
#     print(title_tag,subtitle_tag,description_tag)
# print(get_data_from_url(url))


# description = 'Honor of Kings is a multiplayer online PVP game.'
description = """
Honor of Kings: The Ultimate 5v5 Hero Battle Game


Honor of Kings International Edition, developed by Tencent Timi Studio and published by Level Infinite, is the world's most popular mobile MOBA game. Dive into the classic MOBA excitement with 5V5 hero's gorge, fair matchups; numerous battle modes and a vast selection of heroes allow you to demonstrate your dominance with first blood, pentakills, and legendary feats, crushing all competition! Localized hero voiceovers, skins, and smooth server performance ensure quick matchmaking, teaming up with friends for ranking battles, and enjoying all the fun of PC MOBAs and action games as you ascend to the pinnacle of honor! The enemy is nearing the battlefield—players, rally your allies for team battles in Honor of Kings!


Moreover, Honor of Kings invites you to partake in top global eSports events! Cheer for your favorite teams, witness thrilling, fervent gameplay, and even become a player yourself, standing on the global stage as a mobile legend MOBA player! It's all in your hands! Here, you are not a playerunknow; enjoy the battleground that's rightfully yours.


**Game Features**

1. 5V5 Tower Pushing Team Battles!

Classic 5V5 MOBA maps, three lanes to advance, providing the purest combat experience. Hero strategy combinations, forming the strongest team, seamless cooperation, showcasing extreme skills! Abundant wild monsters, a wide range of hero choices, battle after battle, fire freely, enjoying all the classic MOBA fun!


2. Legendary Heroes, Unique Skills, Dominate the Battlefield

Experience the power of heroes from myth and legend! Unleash their unique skills and experience completely different gameplay fun. Master the special skills of each hero, become a legend on the battlefield! Challenge your operations and strategies in the peak showdown of skills, experience unparalleled gaming fun. Choose your favorite heroes, unleash their power, fight alongside your teammates, conquer opponents, and create legends!


3. Ready to Team Up with Friends Anytime! Experience Ultimate Competitive Gameplay in 15 Minutes!

A MOBA game tailored for mobile, enjoy competitive gaming in just 15 minutes. Use your intellect in battle, combine strategy with skill, fight to the death, and become the MVP of the match! Team up with friends anytime, coordinate with rational hero selections, use your synergy with friends to sweep the battlefield with skill combinations, and become the heroes who dominate the battlefield!


4. Team-Based Fair Competition! Fun and Fair, It's All About Skill!

Dominate the field with skill, pursuing glory with your team. No hero cultivation, no stamina system, bringing back the original joy of gaming! A fair competitive environment without additional pay-to-win aspects. Superior skill and strategy are your only means to victory and championship honor.

Enter the mobile arena where legends are born, and valor is tested with every challenge you face.


5. Local Servers, Local Voiceovers, Local Game Content, Smooth gaming, immersive experience!

Local servers ensure smooth gaming experiences for you; localized hero voiceovers immerse you in every exciting battle; localized heroes and skins allow you to use your familiar heroes to achieve victory. At the same time, Honor of Kings prepares excellent AI for you. When you or your teammates disconnect, the AI will temporarily control the character to assist you in continuing the battle, ensuring you don't lose the victory due to outnumbered battles.


**Contact Us**

If you enjoy our game, please feel free to give us your feedback or leave a message.
"""
#语言检测函数
def detect_language(text):
    try:
        lang_code = detect(text)
        return lang_code
    except Exception as e:
        print(f"语言检测失败: {e}")
        return None

#加载多语言分词器
nlp_multilingual = spacy.load(r'models/xx_ent_wiki_sm')

sudachi_tokenizer = dictionary.Dictionary().create()
sudachi_mode = tokenizer.Tokenizer.SplitMode.C  # 使用细粒度分词

cutter = Cutter()

#多语言分词函数
def split_multilingual_text(text):
    # 检测语言
    lang_code = detect_language(text)
    # print('2222',lang_code)
    if lang_code == 'zh-cn':  # 中文
        # return jieba.lcut(text,cut_all=True)
        return cutter.cutword(text)
    elif lang_code == 'ja':  # 日文
        tokens = sudachi_tokenizer.tokenize(text, sudachi_mode)
        return [token.surface() for token in tokens]
    else:  # 其他语言使用 spaCy 分词
        doc = nlp_multilingual(text)
        return [token.text for token in doc]


words = split_multilingual_text(description)
print(words)

words_in_description = [word for word in words if word != ' ']
print(words_in_description)
# words2 = jieba.analyse.extract_tags(description, topK=10)    
# print(words)
# print(words2)


# # 加载预训练的BERT模型和分词器
model_words = {
    '游戏': ['王者荣耀游戏', '多人在线游戏'],
    'game': ['multiplayer online game', 'video game', 'online game'],
    'ゲーム': ['オンラインゲーム', 'マルチプレイヤーゲーム'],  
    '게임': ['온라인 게임', '멀티플레이어 게임'] 
}

model_path = 'models\google_bert_bert_base_uncased'

tokenizer = BertTokenizer.from_pretrained(model_path)
model = BertModel.from_pretrained(model_path)

def cosine_similarity(vec1, vec2):
    # return torch.dot(vec1, vec2) / (torch.norm(vec1) * torch.norm(vec2))
# 使用 torch.nn.functional.cosine_similarity 来计算二维张量的余弦相似度
    return F.cosine_similarity(vec1, vec2, dim=1)  # 在指定维度计算相似度

def get_word_embedding(word):
    inputs = tokenizer(word, return_tensors='pt', padding=True, truncation=True)
    outputs = model(**inputs)
    a = outputs.last_hidden_state.mean(dim=1)
    # print('1111111',a.shape)
    return a


def find_similar_words(word, model_words, threshold=0.8):
    word_embedding = get_word_embedding(word)
    # print('22222',word_embedding.shape)
    for key, synonyms in model_words.items():
        for synonym in synonyms:  # 只比较 synonyms 列表中的词，排除 key 本身
            synonym_embedding = get_word_embedding(synonym)
            similarity = cosine_similarity(word_embedding, synonym_embedding)
            # print('22222',similarity)
            if similarity > threshold:
                return word
    return None

# 遍历产品描述，找出与模型词语相似的词
matched_words_in_description = []
for word in words_in_description:
    result = find_similar_words(word, model_words)
    if result:
        matched_words_in_description.append(result)

print("描述中与模型词汇相似的词：", matched_words_in_description)


# # 计算句子中每个词的向量
# air_purifier_vec = embeddings.mean(dim=1).squeeze()

# # 计算余弦相似度


# # 假设我们有另一个词向量 'cleaner' 来比较
# text2 = "cleaner"
# inputs2 = tokenizer(text2, return_tensors="pt")
# outputs2 = model(**inputs2)
# cleaner_vec = outputs2.last_hidden_state.mean(dim=1).squeeze()

# similarity = cosine_similarity(air_purifier_vec, cleaner_vec)
# print(similarity.item())
