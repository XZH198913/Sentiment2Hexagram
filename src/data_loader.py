# data_loader.py
import pandas as pd
from pathlib import Path
from typing import Tuple, Dict, List
import logging

logging.basicConfig(level=logging.INFO)

def load_gua_config(csv_path: str = "64_gua.csv") -> Tuple[Dict[str, List[str]], Dict[str, List[str]]]:
    """从CSV加载64卦数据，生成GUAS（极性分类）和INTENSITY_RANK（强度分级）字典
    
    Args:
        csv_path: 64卦数据CSV文件路径
        
    Returns:
        包含极性分类和强度分级的两个字典的元组
        
    Raises:
        FileNotFoundError: 当CSV文件不存在时
        pd.errors.EmptyDataError: 当CSV文件为空时
    """
    if not Path(csv_path).exists():
        raise FileNotFoundError(f"卦象配置文件不存在：{csv_path}")
    """从CSV加载64卦数据，生成GUAS（极性分类）和INTENSITY_RANK（强度分级）字典"""
    gua_df = pd.read_csv(csv_path)
    
    # 定义极性分类规则
    positive_keywords = [
        "创造", "刚健", "进取", "和谐", "成功", "富足", "增益", "光明",
        "发展", "上升", "吉祥", "顺遂", "通达", "喜悦", "祥和", "昌盛",
        "丰盛", "繁荣", "团结", "合作", "共识", "信任", "诚信", "复兴",
        "回归", "新生", "自然", "稳固", "权力", "更新"
    ]
    neutral_keywords = [
        "实践", "观察", "稳定", "恒久", "调节", "渐进", "启蒙", "平和",
        "中庸", "持续", "平静", "等待", "思考", "积累", "沉淀", "适中",
        "教育", "探索", "需求", "准备", "领导", "监督", "学习", "装饰",
        "美化", "礼仪", "颐养", "自足", "修养", "依附"
    ]
    negative_keywords = [
        "困境", "损失", "冲突", "腐败", "闭塞", "危机", "束缚", "衰败",
        "退步", "阻碍", "凶险", "艰难", "混乱", "忧虑", "破坏", "动荡",
        "争讼", "调解", "剥落", "衰落", "过度", "非常", "险陷", "挑战",
        "隐退", "避让", "涣散", "分散", "化解", "未完成"
    ]
    
    # 定义强度分级规则
    high_intensity_keywords = [
        "冲突", "决断", "危机", "强制", "腐败", "束缚", "激烈",
        "剧变", "突破", "极端", "爆发", "革命", "斗争", "震动",
        "创造", "刚健", "进取", "强盛", "壮大", "行动", "果断"
    ]
    medium_intensity_keywords = [
        "解决", "调整", "阻碍", "变革", "损失", "整顿", "转化",
        "改变", "发展", "推进", "转折", "调和", "适应", "过渡",
        "渐进", "发展", "成长", "归宿", "婚姻", "结合", "和谐"
    ]
    low_intensity_keywords = [
        "稳定", "观察", "谦虚", "柔和", "实践", "渐进", "平静",
        "缓慢", "温和", "细微", "持久", "安详", "宁静", "舒缓",
        "包容", "柔顺", "承载", "等待", "需求", "准备", "亲近"
    ]
    
    try:
        gua_df = pd.read_csv(csv_path)
        if gua_df.empty:
            raise pd.errors.EmptyDataError("卦象配置文件为空")
    except pd.errors.EmptyDataError as e:
        logging.error(f"加载卦象配置失败：{e}")
        raise
    except Exception as e:
        logging.error(f"加载卦象配置时发生错误：{e}")
        raise

    # 初始化字典
    GUAS = {"positive": [], "neutral": [], "negative": []}
    INTENSITY_RANK = {"high": [], "medium": [], "low": []}
    
    # 记录未分类的卦象
    unclassified_guas = []
    
    for _, row in gua_df.iterrows():
        gua_name = row["卦名"]
        keywords = row["关键词"].split("、")
        
        # 极性分类（使用得分系统）
        scores = {
            "positive": sum(kw in positive_keywords for kw in keywords),
            "neutral": sum(kw in neutral_keywords for kw in keywords),
            "negative": sum(kw in negative_keywords for kw in keywords)
        }
        
        if any(scores.values()):
            max_score = max(scores.values())
            max_categories = [cat for cat, score in scores.items() if score == max_score]
            if len(max_categories) == 1:
                GUAS[max_categories[0]].append(gua_name)
            else:
                # 如果多个类别得分相同，默认选择中性
                GUAS["neutral"].append(gua_name)
        else:
            unclassified_guas.append(gua_name)
        
        # 强度分级
        if any(kw in high_intensity_keywords for kw in keywords):
            INTENSITY_RANK["high"].append(gua_name)
        elif any(kw in medium_intensity_keywords for kw in keywords):
            INTENSITY_RANK["medium"].append(gua_name)
        elif any(kw in low_intensity_keywords for kw in keywords):
            INTENSITY_RANK["low"].append(gua_name)
    
    # 记录分类结果
    logging.info(f"极性分类结果：积极={len(GUAS['positive'])}个, 中性={len(GUAS['neutral'])}个, 消极={len(GUAS['negative'])}个")
    if unclassified_guas:
        logging.warning(f"未能分类的卦象：{', '.join(unclassified_guas)}")
    
    return GUAS, INTENSITY_RANK