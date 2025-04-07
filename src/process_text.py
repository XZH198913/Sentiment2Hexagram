"""
整合spaCy与易经卦象分析的系统
架构版本：2.0
功能模块：
1. 句子级情感-卦象映射
2. 动态卦象解释系统
3. 多层次分析报告
"""
import spacy
from pathlib import Path
from typing import List, Dict, Tuple
import argparse
import sys
import time
import math
from collections import defaultdict
from gua_config import GUAS, INTENSITY_RANK

# 配置参数
DEFAULT_MODEL = "zh_core_web_lg"

class YijingAnalyzer:
    """易经分析引擎（优化版）"""
    
    # 添加情感词库缓存
    SENTIMENT_LEXICON = {
        # 基础情感词
        "好": 0.5, "优秀": 0.7, "糟糕": -0.6,
        "快乐": 0.6, "悲伤": -0.5, "愤怒": -0.7,
        "喜悦": 0.8, "焦虑": -0.4, "平静": 0.3,
        "满意": 0.6, "失望": -0.5, "期待": 0.4,
        # 扩展情感词
        "美好": 0.7, "卓越": 0.8, "杰出": 0.8,
        "欢欣": 0.7, "愉悦": 0.6, "舒畅": 0.5,
        "忧伤": -0.6, "痛苦": -0.8, "恐惧": -0.7,
        "烦恼": -0.5, "沮丧": -0.6, "绝望": -0.9,
        "温暖": 0.4, "温馨": 0.5, "祥和": 0.6,
        "冷漠": -0.4, "阴郁": -0.5, "压抑": -0.6
    }
    NEGATION_WORDS = {"不", "没", "非", "未", "别", "莫", "勿", "无", "否", "休", "绝", "难", "决", "忌"}

    def __init__(self):
        if not hasattr(self.__class__, '_nlp'):
            self.__class__._nlp = self._load_model()
        self.nlp = self.__class__._nlp
        self.sentences = []
        self.gua_results = []
        self.polarity_stats = defaultdict(int)
        self.intensity_stats = defaultdict(int)
        
    def _load_model(self) -> spacy.language.Language:
        try:
            nlp = spacy.load(DEFAULT_MODEL)
            if not nlp.has_pipe("sentiment"):
                nlp.add_pipe("sentiment", last=True)
            return nlp
        except OSError:
            print(f"请先安装中文模型: python -m spacy download {DEFAULT_MODEL}")
            sys.exit(1)
    
    def analyze_text(self, text: str) -> None:
        doc = self.nlp(text)
        self.sentences = [sent.text for sent in doc.sents]
        self._analyze_sentiments(doc)
        self._analyze_polarity_and_intensity()
    
    def _analyze_sentiments(self, doc) -> None:
        for sent in doc.sents:
            sentiment = self._calculate_sentiment(sent)
            gua = self._map_to_gua(sentiment)
            self.gua_results.append({
                "sentence": sent.text,
                "sentiment": sentiment,
                "gua": gua[0],
                "explanation": gua[1]
            })
    
    def _analyze_polarity_and_intensity(self) -> None:
        for result in self.gua_results:
            gua_name = result["gua"]
            # 统计极性
            for polarity, guas in GUAS.items():
                if gua_name in guas:
                    self.polarity_stats[polarity] += 1
                    break
            # 统计强度
            for intensity, guas in INTENSITY_RANK.items():
                if gua_name in guas:
                    self.intensity_stats[intensity] += 1
                    break

    def _calculate_sentiment(self, sent) -> float:
        """增强型情感计算"""
        try:
            # 合并词性权重、情感词库和否定词处理
            pos_weights = {"VERB": 0.3, "ADJ": 0.5, "NOUN": 0.2}
            score = 0.0
            negation = False
            sent_length = len(sent)
            
            if sent_length == 0:  # 处理空句子
                return 0.0

            for i, token in enumerate(sent):
                # 情感词库优先
                if token.text in self.SENTIMENT_LEXICON:
                    word_score = self.SENTIMENT_LEXICON[token.text]
                    # 检查前三个词是否有否定词
                    negation = any(w.text in self.NEGATION_WORDS 
                                for w in sent[max(0,i-3):i])
                    score += -word_score if negation else word_score
                elif token.pos_ in pos_weights:
                    score += pos_weights[token.pos_]
            
            # 加入句子长度衰减因子
            return math.tanh(score * math.log(sent_length + 1) / sent_length)
        except Exception as e:
            logging.error(f"情感计算出错：{e}")
            return 0.0

    def _map_to_gua(self, score: float) -> Tuple[str, str]:
        """优化卦象映射逻辑"""
        try:
            # 按顺序检查区间（修正坤卦重复问题）
            intervals = [
                (0.8, 1.0, ("乾", "天行健，君子以自强不息")),
                (0.6, 0.8, ("离", "明两作，离，大人以继明照于四方")),
                (0.4, 0.6, ("巽", "随风巽，君子以申命行事")),
                (0.2, 0.4, ("艮", "兼山艮，君子以思不出其位")),
                (0.0, 0.2, ("坤", "地势坤，君子以厚德载物")),
                (-0.2, 0.0, ("震", "洊雷震，君子以恐惧修省")),
                (-0.4, -0.2, ("兑", "丽泽兑，君子以朋友讲习")),
                (-0.6, -0.4, ("坎", "水洊至，习坎，君子以常德行")),
                (-1.0, -0.6, ("复", "反复其道，七日来复"))  # 修正坤卦为复卦
            ]
            
            for lower, upper, gua in intervals:
                if lower < score <= upper:
                    return gua
            return ("未济", "物不可穷也，故受之以未济终焉")
        except Exception as e:
            logging.error(f"卦象映射出错：{e}")
            return ("未济", "映射出错，默认未济")

class ReportGenerator:
    def __init__(self, analyzer: YijingAnalyzer):
        self.analyzer = analyzer
        self.report = []
        
    def generate(self) -> List[str]:
        self._add_header()
        self._add_statistics()
        self._add_polarity_analysis()
        self._add_intensity_analysis()
        self._add_gua_analysis()
        self._add_detailed_mapping()
        return self.report
    
    def _add_polarity_analysis(self):
        """添加极性分析报告"""
        total = sum(self.analyzer.polarity_stats.values())
        if total == 0:
            return
            
        self.report.extend([
            "文本极性分析",
            "-" * 40,
            "📊 极性分布："
        ])
        
        for polarity, count in self.analyzer.polarity_stats.items():
            percentage = count / total * 100
            polarity_cn = {"positive": "积极", "neutral": "中性", "negative": "消极"}[polarity]
            self.report.append(f"  - {polarity_cn}：{count}次 ({percentage:.1f}%)")
        self.report.append("")
    
    def _add_intensity_analysis(self):
        """添加强度分析报告"""
        total = sum(self.analyzer.intensity_stats.values())
        if total == 0:
            return
            
        self.report.extend([
            "情感强度分析",
            "-" * 40,
            "📈 强度分布："
        ])
        
        for intensity, count in self.analyzer.intensity_stats.items():
            percentage = count / total * 100
            intensity_cn = {"high": "高", "medium": "中", "low": "低"}[intensity]
            self.report.append(f"  - {intensity_cn}强度：{count}次 ({percentage:.1f}%)")
        self.report.append("")

    def _add_header(self):
        """报告头部信息"""
        self.report.extend([
            "易经文本分析报告",
            "=" * 40,
            f"生成时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"分析模型：{DEFAULT_MODEL} (spaCy v{spacy.__version__})",
            ""
        ])
    
    def _add_statistics(self):
        """统计信息模块"""
        stats = {
            "总句子数": len(self.analyzer.sentences),
            "卦象分布": defaultdict(int)
        }
        for res in self.analyzer.gua_results:
            stats["卦象分布"][res["gua"]] += 1
        
        self.report.extend([
            "统计摘要",
            "-" * 40,
            f"📊 总句子数：{stats['总句子数']}",
            "📈 卦象分布："
        ])
        for gua, count in stats["卦象分布"].items():
            self.report.append(f"  - {gua}卦：{count}次 ({count/stats['总句子数']:.1%})")
        self.report.append("")
    
    def _add_gua_analysis(self):
        """卦象深度解析"""
        self.report.extend([
            "卦象特征分析",
            "-" * 40
        ])
        gua_explanations = {}
        gua_attributes = {}
        
        for res in self.analyzer.gua_results:
            gua = res["gua"]
            if gua not in gua_explanations:
                gua_explanations[gua] = res["explanation"]
                # 获取卦象属性
                if gua in GUA_ATTRIBUTES:
                    gua_attributes[gua] = GUA_ATTRIBUTES[gua]
        
        for gua, exp in gua_explanations.items():
            self.report.extend([
                f"【{gua}卦】解析：",
                f"  卦辞：{exp}"
            ])
            
            # 添加卦象属性信息
            if gua in gua_attributes:
                attrs = gua_attributes[gua]
                self.report.extend([
                    f"  五行：{attrs['element']}",
                    f"  性质：{attrs['nature']}",
                    f"  方位：{attrs['direction']}"
                ])
            
            self.report.append("  典型例句：")
            examples = [r["sentence"] for r in self.analyzer.gua_results if r["gua"] == gua][:3]
            for ex in examples:
                self.report.append(f"  - {ex[:50]}...")
            self.report.append("")
    
    def _add_detailed_mapping(self):
        """详细映射表"""
        self.report.extend([
            "句子-卦象映射明细",
            "-" * 40,
            "序号 | 卦象 | 情感值 | 句子摘要"
        ])
        for idx, res in enumerate(self.analyzer.gua_results, 1):
            self.report.append(
                f"{idx:04d} | {res['gua']:2} | {res['sentiment']:+.2f} | "
                f"{res['sentence'][:60].replace('\n', ' ')}..."
            )

def main():
    """主控程序"""
    parser = argparse.ArgumentParser(description="易经文本分析系统")
    parser.add_argument("-i", "--input", type=Path, required=True)
    parser.add_argument("-o", "--output", type=Path)
    args = parser.parse_args()

    analyzer = YijingAnalyzer()
    analyzer.analyze_text(args.input.read_text(encoding="utf-8"))
    
    report = ReportGenerator(analyzer).generate()
    
    # 控制台输出
    print("\n".join(report[:50]))
    
    # 文件输出
    if args.output:
        args.output.write_text("\n".join(report), encoding="utf-8")
        print(f"报告已保存至：{args.output}")

if __name__ == "__main__":
    main()