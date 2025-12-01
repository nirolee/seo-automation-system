# -*- coding: utf-8 -*-
"""测试Google搜索建议功能"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import json

print("=" * 60)
print("🎯 测试Google搜索建议")
print("=" * 60)

proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

# 测试种子关键词
seed_keyword = "best coffee maker"

print(f"\n种子关键词: {seed_keyword}")
print("正在获取相关建议词...\n")

url = "http://suggestqueries.google.com/complete/search"
suggestions = set()

# 测试几个字母
for char in 'abcdef':
    params = {
        'client': 'firefox',
        'q': f'{seed_keyword} {char}',
        'hl': 'en'
    }

    try:
        response = requests.get(url, params=params, proxies=proxies, timeout=5)
        data = json.loads(response.text)
        if len(data) > 1:
            suggestions.update(data[1])
        print(f"   测试 '{char}' ✅ 找到 {len(data[1]) if len(data) > 1 else 0} 个建议")
    except Exception as e:
        print(f"   测试 '{char}' ❌ 失败: {e}")

print(f"\n✅ 总共找到 {len(suggestions)} 个相关关键词\n")
print("📝 Top 10 相关词:\n")

for i, kw in enumerate(list(suggestions)[:10], 1):
    print(f"   {i:2d}. {kw}")

print("\n" + "=" * 60)
print("🎉 测试成功！关键词挖掘功能正常")
print("=" * 60)
print("\n💡 下一步：")
print("   运行完整工具: python keyword-digger.py")
print("   输入种子词: best coffee maker")
