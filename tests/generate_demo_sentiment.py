import spacy
from process_text import YijingAnalyzer
from pathlib import Path
import math
import pkg_resources

def check_spacy_version():
    required_spacy = '3.8.4'
    required_model = 'zh_core_web_lg-3.8.0'
    
    # 检查spaCy版本
    spacy_version = pkg_resources.get_distribution('spacy').version
    if not spacy_version.startswith('3.8'):
        raise ImportError(f'需要spaCy版本3.8.x，当前版本为{spacy_version}')
    
    # 检查模型版本
    try:
        nlp = spacy.load('zh_core_web_lg')
        if not nlp.meta['version'].startswith('3.8'):
            raise ImportError(f'需要zh_core_web_lg模型版本3.8.x，当前版本为{nlp.meta["version"]}')
    except OSError as e:
        raise ImportError('未找到zh_core_web_lg模型，请确保已安装正确版本的模型')

def process_text(input_file: str, output_file: str):
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # 初始化分析器
    analyzer = YijingAnalyzer()
    
    # 加载spaCy模型
    nlp = spacy.load('zh_core_web_lg')
    
    # 分句并分析
    doc = nlp(text)
    sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    
    # 分析每个句子的情感
    results = []
    for i, sentence in enumerate(sentences, 1):
        # 计算情感分数
        sentiment_score = analyzer._calculate_sentiment(nlp(sentence))
        # 计算强度（使用tanh函数将分数映射到0-1范围）
        intensity = abs(math.tanh(sentiment_score))
        
        # 确定极性类型
        polarity_type = '积极' if sentiment_score > 0 else '消极' if sentiment_score < 0 else '中性'
        
        # 格式化输出
        result = f'句子 {i}: {sentence}\n极性：{sentiment_score:.1f}（{polarity_type}） 强度：{intensity:.1f}'
        results.append(result)
    
    # 写入输出文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))

def main():
    try:
        check_spacy_version()
    except ImportError as e:
        print(f'版本兼容性检查失败：{e}')
        return
        
    input_file = 'demo.txt'
    output_file = 'text_s1.txt'
    
    if not Path(input_file).exists():
        print(f'输入文件 {input_file} 不存在')
        return
    
    try:
        process_text(input_file, output_file)
        print(f'成功生成情感分析结果：{output_file}')
    except Exception as e:
        print(f'处理文件时出错：{e}')

if __name__ == '__main__':
    main()