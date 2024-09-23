import nltk
from nltk import word_tokenize, pos_tag, ngrams
import re

# 示例文本
text = """
King Wars is a super game ! 
"""

# 1. 对文本进行分词和词性标注
tokens = word_tokenize(text)
pos_tags = pos_tag(tokens)

# 2. 定义我们感兴趣的词性：名词(NN, NNS, NNP, NNPS)，形容词(JJ, JJR, JJS)，动词(VB, VBD, VBG, VBN, VBP, VBZ)
def is_keyword_pos(tag):
    return tag.startswith('NN') or tag.startswith('JJ') or tag.startswith('VB')

# 3. 提取符合条件的词
keywords = [word for word, pos in pos_tags if is_keyword_pos(pos)]

# 4. 使用 ngrams 生成双词组（或三词组，可以调整 n 的值）
bigrams = ngrams(keywords, 2)  # 生成双词组
trigrams = ngrams(keywords, 3) # 生成三词组

# 5. 清理词组，去掉标点符号等
def clean_and_filter_phrases(phrases):
    clean_phrases = []
    for phrase in phrases:
        clean_phrase = " ".join(phrase)
        # 去除标点符号
        clean_phrase = re.sub(r"[’‘“”'\".,;—()]", '', clean_phrase).strip()
        if len(clean_phrase.split()) > 1:  # 过滤掉只有一个词的短语
            clean_phrases.append(clean_phrase)
    
    # 去重处理
    return list(dict.fromkeys(clean_phrases))

# 清理和过滤双词组和三词组
cleaned_bigrams = clean_and_filter_phrases(bigrams)
cleaned_trigrams = clean_and_filter_phrases(trigrams)

# 合并双词组和三词组，最终关键词词组列表
final_phrases = cleaned_bigrams + cleaned_trigrams

# 输出最终的词组列表
print(final_phrases)