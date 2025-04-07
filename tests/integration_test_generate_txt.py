# generate_1txt.py
import spacy
from textblob import TextBlob
import jieba.analyse as analyse
from gensim import corpora, models
import re

# 加载模型
nlp = spacy.load("zh_core_web_sm")

# 读取原始文本和分词结果
def read_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误：文件 {file_path} 未找到")
        return None
    except Exception as e:
        print(f"读取文件 {file_path} 时发生错误：{e}")
        return None

raw_text = read_file("text_s1.txt")
segmented_text = read_file("segmented_text_s1.txt")

if raw_text is None or segmented_text is None:
    exit()

# 分句处理（假设句子以句号分隔）
sentences = [s.strip() for s in raw_text.split("。") if s.strip()]
segmented_lines = segmented_text.splitlines()

# 训练LDA主题模型（示例：3个主题）
tokenized_sentences = [sentence.split() for sentence in segmented_lines]
dictionary = corpora.Dictionary(tokenized_sentences)
corpus = [dictionary.doc2bow(tokens) for tokens in tokenized_sentences]
lda_model = models.LdaModel(corpus, num_topics=3, id2word=dictionary)

# 定义维度分析函数
def analyze_sentence(sentence_id: int, text: str, segmented: list) -> dict:
    try:
        # 依存分析
        doc = nlp(text)
        dependency_tags = [token.dep_ for token in doc]
        complexity = "复杂" if "nsubj" in dependency_tags and "dobj" in dependency_tags else "简单"
        
        # 关键词提取（TF-IDF）
        keywords = analyse.extract_tags(" ".join(segmented), topK=3, withWeight=False)
        
        # 情感子类型（英文示例，需替换为中文情感词典）
        blob = TextBlob(text)
        sentiment_subtype = "愤怒" if blob.sentiment.polarity < -0.5 else "悲伤" if blob.sentiment.polarity < 0 else "希望"
        
        # 主题分类
        bow = dictionary.doc2bow(segmented)
        topics = lda_model.get_document_topics(bow)
        main_topic = max(topics, key=lambda x: x[1])[0]
        topic_map = {0: "情感矛盾", 1: "经济纠纷", 2: "自我反思"}
        
        return {
            "sentence_id": sentence_id,
            "text": text,
            "polarity": -0.4,  # 假设已有极性数据（需替换为实际值）
            "intensity": 0.8,   # 假设已有强度数据（需替换为实际值）
            "topic": topic_map.get(main_topic, "其他"),
            "keywords": "、".join(keywords),
            "dependency_complexity": complexity,
            "sentiment_subtype": sentiment_subtype,
            "sentence_length": len(segmented)
        }
    except Exception as e:
        print(f"分析句子 {sentence_id} 时发生错误：{e}")
        return None

# 生成多维度数据
enhanced_data = []
for idx, (sent, seg) in enumerate(zip(sentences, segmented_lines)):
    seg_words = seg.split()
    result = analyze_sentence(idx+1, sent, seg_words)
    if result is not None:
        enhanced_data.append(result)

# 保存到1.txt
def write_to_file(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            for item in data:
                f.write(
                    f"句子 {item['sentence_id']}:\n"
                    f"内容：{item['text']}\n"
                    f"极性：{item['polarity']:.2f} （{'积极' if item['polarity'] > 0 else '消极' if item['polarity'] < 0 else '中性'})\n"
                    f"强度：{item['intensity']:.2f}\n"
                    f"主题：{item['topic']}\n"
                    f"关键词：{item['keywords']}\n"
                    f"依存复杂度：{item['dependency_complexity']}\n"
                    f"情感子类型：{item['sentiment_subtype']}\n"
                    f"句子长度：{item['sentence_length']}\n\n"
                )
        print(f"文件已生成：{file_path}")
    except Exception as e:
        print(f"写入文件 {file_path} 时发生错误：{e}")

write_to_file("1.txt", enhanced_data)