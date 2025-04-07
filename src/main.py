# main.py
import pandas as pd
from datetime import datetime
import logging
from pathlib import Path
from gua_config import GUAS, INTENSITY_RANK

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def load_and_clean_sentences(file_path: str) -> pd.DataFrame:
    """读取并清洗句子数据
    
    Args:
        file_path: 输入文件路径
        
    Returns:
        包含清洗后句子数据的DataFrame
        
    Raises:
        FileNotFoundError: 当文件不存在时
        ValueError: 当数据格式不正确时
    """
    if not Path(file_path).exists():
        raise FileNotFoundError(f"输入文件不存在：{file_path}")
        
    sentences = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                if "句子" in line:
                    try:
                        parts = line.strip().split(":")
                        sentence_id = parts[0].split(" ")[1]
                        content = parts[1].split("极性")[0].strip()
                        polarity = float(parts[1].split("极性：")[1].split("（")[0].strip())
                        intensity = float(parts[1].split("强度：")[1].split()[0].strip())
                        
                        sentences.append({
                            "sentence_id": int(sentence_id),
                            "text": content,
                            "polarity": polarity,
                            "intensity": intensity
                        })
                    except (IndexError, ValueError) as e:
                        logging.warning(f"第{line_num}行数据格式错误：{e}")
                        continue
    except Exception as e:
        logging.error(f"读取文件时发生错误：{e}")
        raise
    
    if not sentences:
        raise ValueError("未找到有效的句子数据")
    
    return pd.DataFrame(sentences)

def map_gua(polarity: float, intensity: float, gua_df: pd.DataFrame) -> dict:
    """映射情感值到卦象
    
    Args:
        polarity: 极性值 (-1到1之间)
        intensity: 强度值 (0到1之间)
        gua_df: 卦象数据DataFrame
        
    Returns:
        包含卦象名称和关键词的字典
    """
    # 确定极性类别，使用更细致的阈值
    if polarity >= 0.7:
        category = "positive"
    elif polarity <= -0.7:
        category = "negative"
    elif -0.2 <= polarity <= 0.2:
        category = "neutral"
    elif polarity > 0:
        category = "positive"
    else:
        category = "negative"
    
    # 确定强度级别，调整阈值使分布更均匀
    if intensity >= 0.75:
        intensity_level = "high"
    elif intensity >= 0.4:
        intensity_level = "medium"
    else:
        intensity_level = "low"
    
    # 获取候选卦象
    candidate_guas = GUAS.get(category, [])
    priority_guas = INTENSITY_RANK.get(intensity_level, [])
    
    # 优先匹配同时满足极性和强度的卦象
    matched_guas = [gua for gua in candidate_guas if gua in priority_guas]
    
    if matched_guas:
        # 如果有多个匹配的卦象，根据极性值的绝对值选择
        if len(matched_guas) > 1:
            if abs(polarity) >= 0.8:
                selected_gua = matched_guas[0]  # 选择列表中第一个（通常强度最高）
            else:
                selected_gua = matched_guas[-1]  # 选择列表中最后一个（通常强度较低）
        else:
            selected_gua = matched_guas[0]
    elif candidate_guas:
        # 如果没有完全匹配的，优先考虑极性
        selected_gua = candidate_guas[0]
        logging.info(f"使用极性匹配的卦象：{selected_gua}")
    else:
        # 如果没有任何匹配，根据极性选择默认卦象
        if category == "positive":
            selected_gua = "泰卦（䷊）"  # 表示通达
        elif category == "negative":
            selected_gua = "否卦（䷋）"  # 表示闭塞
        else:
            selected_gua = "中孚卦（䷼）"  # 表示中正
        logging.warning(f"未找到匹配的卦象，使用默认卦象：{selected_gua}")
    
    try:
        # 获取卦象关键词
        gua_keywords = gua_df[gua_df["卦名"] == selected_gua]["关键词"].values[0]
    except (IndexError, KeyError):
        logging.error(f"未找到卦象'{selected_gua}'的关键词")
        gua_keywords = "未知"
    
    return {"gua_name": selected_gua, "gua_keywords": gua_keywords}

def main():
    try:
        # 读取卦象配置
        gua_df = pd.read_csv("64_gua.csv")
        logging.info("成功加载卦象配置文件")
        
        # 读取并清洗句子数据
        sentences_df = load_and_clean_sentences("text_s1.txt")
        logging.info(f"成功读取{len(sentences_df)}条句子数据")
        
        # 应用映射规则
        sentences_df[["gua_name", "gua_keywords"]] = sentences_df.apply(
            lambda row: pd.Series(map_gua(row["polarity"], row["intensity"], gua_df)), axis=1
        )
        
        # 生成带日期的文件名
        current_date = datetime.now().strftime("%Y%m%d")
        output_filename = f"sentiment_gua_mapping_{current_date}.csv"
        
        # 保存结果
        sentences_df.to_csv(
            output_filename,
            columns=["sentence_id", "text", "polarity", "intensity", "gua_name", "gua_keywords"],
            index=False,
            encoding="utf-8-sig"  # 支持中文字符
        )
        
        logging.info(f"文件已生成：{output_filename}")
        print(f"文件已生成：{output_filename}")
        
    except Exception as e:
        logging.error(f"程序执行出错：{e}")
        raise

if __name__ == "__main__":
    main()