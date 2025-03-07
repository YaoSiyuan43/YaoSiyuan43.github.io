from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import jieba
import nltk
from nltk.tokenize import word_tokenize
import pandas as pd
from docx import Document
import io
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import base64
import random
import numpy as np
from PIL import Image, ImageDraw

app = Flask(__name__)
CORS(app)

# 下载NLTK数据
nltk.download('punkt')

def create_mask(shape, width, height):
    """创建不同形状的遮罩"""
    # 创建白色背景的遮罩
    mask = Image.new('RGB', (width, height), (255, 255, 255))  # 白色背景
    draw = ImageDraw.Draw(mask)
    
    if shape == 'circle':
        # 绘制圆形
        draw.ellipse([0, 0, width-1, height-1], fill='black')
    elif shape == 'heart':
        # 绘制心形
        points = [
            (width//2, height//4),  # 顶部中点
            (width//4, height//4),  # 左上
            (0, height//2),         # 左中
            (width//4, 3*height//4), # 左下
            (width//2, height),     # 底部中点
            (3*width//4, 3*height//4), # 右下
            (width, height//2),     # 右中
            (3*width//4, height//4), # 右上
        ]
        draw.polygon(points, fill='black')
    elif shape == 'star':
        # 绘制星形
        points = []
        for i in range(10):
            angle = i * 36 * np.pi / 180
            radius = width//2 if i % 2 == 0 else width//4
            x = width//2 + radius * np.cos(angle)
            y = height//2 + radius * np.sin(angle)
            points.append((x, y))
        draw.polygon(points, fill='black')
    elif shape == 'cloud':
        # 绘制云形
        # 主体圆形
        draw.ellipse([width//4, height//4, 3*width//4, 3*height//4], fill='black')
        # 左侧圆形
        draw.ellipse([0, height//3, width//3, 2*height//3], fill='black')
        # 右侧圆形
        draw.ellipse([2*width//3, height//3, width, 2*height//3], fill='black')
        # 顶部圆形
        draw.ellipse([width//3, 0, 2*width//3, height//3], fill='black')
        # 底部圆形
        draw.ellipse([width//3, 2*height//3, 2*width//3, height], fill='black')
        
        # 添加连接部分
        # 左上连接
        draw.rectangle([width//4, height//3, width//2, 2*height//3], fill='black')
        # 右上连接
        draw.rectangle([width//2, height//3, 3*width//4, 2*height//3], fill='black')
        # 顶部连接
        draw.rectangle([width//3, height//4, 2*width//3, height//2], fill='black')
        # 底部连接
        draw.rectangle([width//3, height//2, 2*width//3, 3*height//4], fill='black')
    
    # 将图像转换为灰度图
    mask = mask.convert('L')
    
    return np.array(mask)

def process_text_file(file_content):
    """处理文本文件"""
    text = file_content.decode('utf-8')
    return process_text(text)

def process_docx_file(file_content):
    """处理Word文档"""
    doc = Document(io.BytesIO(file_content))
    text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
    return process_text(text)

def process_excel_file(file_content):
    """处理Excel文件"""
    df = pd.read_excel(io.BytesIO(file_content))
    text = ' '.join(df.astype(str).values.flatten())
    return process_text(text)

def process_csv_file(file_content):
    """处理CSV文件"""
    df = pd.read_csv(io.BytesIO(file_content))
    text = ' '.join(df.astype(str).values.flatten())
    return process_text(text)

def process_text(text):
    """处理文本内容，进行中英文分词和词频统计"""
    # 中文分词
    chinese_words = jieba.cut(text)
    chinese_word_freq = {}
    for word in chinese_words:
        if len(word.strip()) > 1:  # 只统计长度大于1的词
            chinese_word_freq[word] = chinese_word_freq.get(word, 0) + 1

    # 英文分词
    english_words = word_tokenize(text)
    english_word_freq = {}
    for word in english_words:
        if word.isalpha() and len(word) > 1:  # 只统计纯字母且长度大于1的词
            word = word.lower()
            english_word_freq[word] = english_word_freq.get(word, 0) + 1

    # 合并结果
    result = {
        'chinese': sorted(chinese_word_freq.items(), key=lambda x: x[1], reverse=True),
        'english': sorted(english_word_freq.items(), key=lambda x: x[1], reverse=True)
    }
    
    return result

@app.route('/')
def index():
    return "词云服务正在运行"

@app.route('/api/process', methods=['POST'])
def process_file():
    print("收到文件处理请求")  # 添加调试信息
    if 'file' not in request.files:
        print("没有文件上传")  # 添加调试信息
        return jsonify({'error': '没有文件上传'}), 400
    
    file = request.files['file']
    if file.filename == '':
        print("文件名为空")  # 添加调试信息
        return jsonify({'error': '没有选择文件'}), 400

    try:
        print(f"开始处理文件: {file.filename}")  # 添加调试信息
        file_content = file.read()
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension == '.txt':
            result = process_text_file(file_content)
        elif file_extension == '.docx':
            result = process_docx_file(file_content)
        elif file_extension in ['.xlsx', '.xls']:
            result = process_excel_file(file_content)
        elif file_extension == '.csv':
            result = process_csv_file(file_content)
        else:
            print(f"不支持的文件格式: {file_extension}")  # 添加调试信息
            return jsonify({'error': '不支持的文件格式'}), 400

        print("文件处理完成")  # 添加调试信息
        return jsonify(result)

    except Exception as e:
        print(f"处理文件时出错: {str(e)}")  # 添加调试信息
        return jsonify({'error': str(e)}), 500

@app.route('/api/generate-wordcloud', methods=['POST'])
def generate_wordcloud():
    try:
        data = request.json
        words = data.get('words', [])
        settings = data.get('settings', {})
        
        # 检查是否有词数据
        if not words:
            return jsonify({'error': '没有词频数据'}), 400
            
        # 尝试使用系统字体
        try:
            font_path = 'SimHei.ttf'  # 首选黑体
            if not os.path.exists(font_path):
                font_path = 'C:/Windows/Fonts/simhei.ttf'  # Windows 系统黑体
            if not os.path.exists(font_path):
                font_path = 'C:/Windows/Fonts/msyh.ttc'  # Windows 系统微软雅黑
            if not os.path.exists(font_path):
                font_path = None  # 如果都找不到，使用默认字体
        except Exception as e:
            print(f"字体加载失败: {str(e)}")
            font_path = None
        
        # 创建遮罩
        width, height = 800, 400
        mask = create_mask(settings.get('shape', 'circle'), width, height)
        
        # 创建词云对象
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color=settings.get('backgroundColor', '#ffffff'),
            font_path=font_path,  # 可能为None，使用默认字体
            max_words=settings.get('maxWords', 200),
            max_font_size=settings.get('fontSize', [8, 120])[1],
            min_font_size=settings.get('fontSize', [8, 120])[0],
            prefer_horizontal=settings.get('orientation', 'horizontal') == 'horizontal',
            relative_scaling=settings.get('density', 50) / 100,
            mask=mask,  # 添加遮罩
            contour_width=0,  # 移除轮廓
            contour_color='black'  # 设置轮廓颜色
        )
        
        # 生成词云
        wordcloud.generate_from_frequencies(dict(words))
        
        # 应用自定义颜色方案
        if 'colors' in settings and settings['colors']:
            colors = settings['colors']
            wordcloud.recolor(color_func=lambda *args, **kwargs: random.choice(colors))
        
        # 将词云图像转换为base64
        img = io.BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(img, format='png', bbox_inches='tight', pad_inches=0)
        plt.close()
        img.seek(0)
        img_base64 = base64.b64encode(img.getvalue()).decode()
        
        return jsonify({
            'success': True,
            'image': img_base64
        })
        
    except Exception as e:
        print(f"生成词云时出错: {str(e)}")
        return jsonify({'error': f'生成词云失败: {str(e)}'}), 500

if __name__ == '__main__':
    print("启动词云服务...")  # 添加调试信息
    app.run(host='0.0.0.0', port=5000, debug=True) 