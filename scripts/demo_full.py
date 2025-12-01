# -*- coding: utf-8 -*-
"""自动演示 - 完整关键词挖掘流程"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import json
import time
from collections import Counter

print("=" * 60)
print("🎯 完整演示：关键词挖掘 - air fryer recipes")
print("=" * 60)

proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

seed_keyword = "air fryer recipes"

print(f"\n📌 种子关键词: {seed_keyword}")
print("🔍 开始挖掘相关关键词...\n")

# 获取关键词建议
url = "http://suggestqueries.google.com/complete/search"
all_keywords = set()

# 策略1: 加字母a-z
print("[1/3] 策略：关键词 + 字母...")
for char in 'abcdefghijklmnopqrstuvwxyz':
    params = {
        'client': 'firefox',
        'q': f'{seed_keyword} {char}',
        'hl': 'en'
    }

    try:
        response = requests.get(url, params=params, proxies=proxies, timeout=5)
        data = json.loads(response.text)
        if len(data) > 1:
            all_keywords.update(data[1])
        time.sleep(0.2)
    except:
        pass

print(f"   ✅ 找到 {len(all_keywords)} 个关键词")

# 策略2: 问题词前缀
print("\n[2/3] 策略：问题词前缀...")
question_words = ['how to', 'what is', 'why', 'best', 'easy', 'healthy']
for qw in question_words:
    params = {
        'client': 'firefox',
        'q': f'{qw} {seed_keyword}',
        'hl': 'en'
    }

    try:
        response = requests.get(url, params=params, proxies=proxies, timeout=5)
        data = json.loads(response.text)
        if len(data) > 1:
            all_keywords.update(data[1])
        time.sleep(0.2)
    except:
        pass

print(f"   ✅ 总共 {len(all_keywords)} 个关键词")

# 策略3: 评分排序
print("\n[3/3] 评分关键词...")

def score_keyword(keyword):
    score = 0
    kw_lower = keyword.lower()

    # 长度评分
    word_count = len(keyword.split())
    if word_count >= 4:
        score += 25
    elif word_count == 3:
        score += 20
    elif word_count == 2:
        score += 10

    # 商业意图
    high_intent = ['buy', 'best', 'review', 'easy', 'simple', 'quick']
    for word in high_intent:
        if word in kw_lower:
            score += 20
            break

    # 问题词
    if kw_lower.startswith(('how', 'what', 'why')):
        score += 15

    # 健康/流行词
    if any(w in kw_lower for w in ['healthy', 'crispy', 'chicken', 'potato']):
        score += 10

    return score

scored_keywords = []
for kw in all_keywords:
    score = score_keyword(kw)
    scored_keywords.append({
        'keyword': kw,
        'score': score,
        'words': len(kw.split())
    })

scored_keywords.sort(key=lambda x: x['score'], reverse=True)

print(f"   ✅ 完成评分")

# 显示结果
print("\n" + "=" * 60)
print(f"📊 挖掘结果统计")
print("=" * 60)
print(f"   总关键词数: {len(all_keywords)}")
print(f"   评分范围: {scored_keywords[0]['score']} - {scored_keywords[-1]['score']}")

print("\n🏆 Top 20 高价值关键词:\n")
for i, kw in enumerate(scored_keywords[:20], 1):
    print(f"   {i:2d}. [{kw['score']:2d}分] {kw['keyword']}")

# 提取热门主题
print("\n📈 热门主题分析:\n")
all_words = []
for kw in scored_keywords[:50]:
    words = kw['keyword'].lower().replace('air fryer recipes', '').split()
    all_words.extend([w for w in words if len(w) > 3])

word_freq = Counter(all_words)
print("   高频词汇:")
for word, count in word_freq.most_common(10):
    print(f"   • {word}: {count}次")

# 建站建议
print("\n" + "=" * 60)
print("💡 建站建议")
print("=" * 60)

print("\n🌐 推荐域名:")
print("   • airfryerhub.com")
print("   • airfryerrecipes.net")
print("   • easyairfryercooking.com")

print("\n📝 第一个月内容计划（30篇）:")
print("   - 10篇基础食谱（鸡肉、薯条、蔬菜等）")
print("   - 5篇对比文章（vs 烤箱、不同品牌）")
print("   - 10篇指南教程（如何使用、清洁技巧）")
print("   - 5篇列表文章（10大食谱、初学者必备）")

print("\n💰 变现方式:")
print("   • Amazon Associates（推荐空气炸锅，佣金$5-15/台）")
print("   • Google AdSense（每1000次浏览$2-5）")
print("   • 联盟营销（食材、厨具）")

print("\n📄 建议的前5篇文章:")
for i, kw in enumerate(scored_keywords[:5], 1):
    print(f"   {i}. {kw['keyword']}")

print("\n📊 预期收入（保守估计）:")
print("   • 第3个月: 500 PV/天 → $30/月")
print("   • 第6个月: 2000 PV/天 → $150-300/月")
print("   • 第12个月: 5000+ PV/天 → $500-1000/月")

print("\n" + "=" * 60)
print("✅ 演示完成！")
print("=" * 60)
print("\n💡 下一步:")
print("   1. 在 Namecheap 注册域名（$12/年）")
print("   2. 使用 Hostinger WordPress托管（$3/月）")
print("   3. 开始创建前5篇文章")
print("   4. 提交到 Google Search Console")

print("\n📁 完整数据已保存到:")
print("   air_fryer_recipes_demo.txt")

# 保存到文件
with open('air_fryer_recipes_demo.txt', 'w', encoding='utf-8') as f:
    f.write(f"Air Fryer Recipes - 关键词挖掘结果\n")
    f.write(f"{'='*60}\n\n")
    f.write(f"总关键词数: {len(all_keywords)}\n\n")
    f.write(f"Top 50 关键词:\n\n")
    for i, kw in enumerate(scored_keywords[:50], 1):
        f.write(f"{i:2d}. [{kw['score']:2d}分] {kw['keyword']}\n")
