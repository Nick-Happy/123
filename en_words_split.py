from transformers import AutoTokenizer, AutoModel
from sklearn.cluster import KMeans
import torch
import numpy as np
import matplotlib.pyplot as plt
from kneed import KneeLocator

# 自动检测肘点
def find_optimal_clusters(embeddings, max_k):
    iters = range(1, max_k+1)
    sse = []
    for k in iters:
        kmeans = KMeans(n_clusters=k, random_state=0, n_init=10)
        kmeans.fit(embeddings)
        sse.append(kmeans.inertia_)

    # 使用 kneed 检测肘点
    kneedle = KneeLocator(iters, sse, curve='convex', direction='decreasing')
    optimal_k = kneedle.elbow

    # 绘制肘部法图
    plt.plot(iters, sse, marker='o')
    plt.axvline(x=optimal_k, color='r', linestyle='--')  # 标记肘点
    plt.xlabel('Cluster Centers')
    plt.ylabel('SSE')
    plt.title(f"Elbow Method to find Optimal k (Optimal k = {optimal_k})")
    # plt.show()

    return optimal_k

def merge_subwords(tokens):
    """合并包含 '##' 的子词"""
    merged_tokens = []
    current_token = ""

    for token in tokens:
        if token.startswith("##"):
            current_token += token[2:]  # 拼接子词，去掉"##"
        else:
            if current_token:
                merged_tokens.append(current_token)  # 把之前合并的词加进去
            current_token = token  # 开始一个新的词

    # 最后一个词处理
    if current_token:
        merged_tokens.append(current_token)

    return merged_tokens

# 合并同一聚类的词
def merge_clusters(tokens, labels):
    """根据聚类标签合并同一类的词，并去掉 '##' 子词"""
    # 先合并子词
    tokens = merge_subwords(tokens)
    
    merged_tokens = []
    current_cluster = labels[0]
    current_phrase = tokens[0]

    for token, label in zip(tokens[1:], labels[1:]):
        if label == current_cluster:
            current_phrase += " " + token  # 合并同一聚类的 token
        else:
            merged_tokens.append(current_phrase)  # 添加聚类词组
            current_phrase = token  # 开始新的词组
            current_cluster = label

    merged_tokens.append(current_phrase)  # 添加最后的词组
    return merged_tokens


# 加载预训练的BERT分词器和模型
tokenizer = AutoTokenizer.from_pretrained("models\google_bert_bert_base_uncased")
model = AutoModel.from_pretrained("models\google_bert_bert_base_uncased")

# 输入文本
text = """
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

"""

# 获取BERT模型的输出（隐藏状态包含每个 token 的词向量）
inputs = tokenizer(text, return_tensors="pt", max_length=512, truncation=True)
with torch.no_grad():
    outputs = model(**inputs)

# 提取最后一层的隐藏状态作为词嵌入
last_hidden_states = outputs.last_hidden_state  # (batch_size, sequence_length, hidden_size)
tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
embeddings = last_hidden_states.squeeze(0).numpy()

# 1. 调用 find_optimal_clusters 函数，找到最优聚类数
optimal_k = find_optimal_clusters(embeddings, max_k=10)

# 2. 使用最优的 k 进行 KMeans 聚类
kmeans = KMeans(n_clusters=optimal_k, random_state=0, n_init=10)
kmeans.fit(embeddings)
labels = kmeans.labels_

# 3. 合并同一聚类的 token
merged_phrases = merge_clusters(tokens, labels)

# 4. 输出聚类后的分词结果
print("聚类后的分词结果:")
print(merged_phrases)





