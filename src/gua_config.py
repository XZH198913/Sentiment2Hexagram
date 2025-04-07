"""卦象配置模块

此模块定义了易经64卦的基本配置信息，包括：
1. 卦象的极性分类（积极、中性、消极）
2. 卦象的情感强度分级（高、中、低）
3. 卦象的基本属性和关键词
"""

from data_loader import load_gua_config
from pathlib import Path
import logging

# 加载卦象配置
try:
    GUAS, INTENSITY_RANK = load_gua_config()
except FileNotFoundError:
    # 如果配置文件不存在，使用默认配置
    logging.warning("未找到卦象配置文件，使用默认配置")
    GUAS = {
        "positive": ["乾", "离", "巽", "大有", "大壮", "泰", "同人", "履"],
        "neutral": ["艮", "坤", "中孚", "节", "蒙", "谦", "渐", "临"], 
        "negative": ["震", "兑", "坎", "复", "未济", "蹇", "否", "剥", "困"]
    }
    
    INTENSITY_RANK = {
        "high": ["乾", "离", "震", "复", "大壮", "革", "夬", "无妄"],
        "medium": ["巽", "兑", "坎", "大过", "明夷", "丰", "恒", "升"],
        "low": ["艮", "坤", "未济", "观", "比", "谦", "豫", "晋"]
    }

# 卦象属性定义
GUA_ATTRIBUTES = {
    "乾": {"element": "金", "nature": "刚健", "direction": "西"},
    "坤": {"element": "土", "nature": "柔顺", "direction": "西南"},
    "震": {"element": "木", "nature": "动", "direction": "东"},
    "巽": {"element": "木", "nature": "入", "direction": "东南"},
    "坎": {"element": "水", "nature": "陷", "direction": "北"},
    "离": {"element": "火", "nature": "丽", "direction": "南"},
    "艮": {"element": "土", "nature": "止", "direction": "东北"},
    "兑": {"element": "金", "nature": "悦", "direction": "西"}
}