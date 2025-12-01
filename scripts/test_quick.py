# -*- coding: utf-8 -*-
"""快速测试 - Google热搜获取"""
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
from bs4 import BeautifulSoup

print("=" * 60)
print("🔥 快速演示 - Google热搜获取")
print("=" * 60)
print("\n📡 正在连接Google Trends（通过7890代理）...\n")

proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
    response = requests.get(url, headers=headers, proxies=proxies, timeout=15)

    soup = BeautifulSoup(response.content, 'xml')
    items = soup.find_all('item')

    print(f"✅ 成功获取 {len(items)} 个Google热搜词\n")
    print("🏆 Top 10 美国热搜:\n")

    for i, item in enumerate(items[:10], 1):
        title = item.find('title')
        traffic = item.find('ht:approx_traffic')
        if title:
            traffic_text = traffic.text if traffic else 'N/A'
            print(f"   {i:2d}. {title.text.strip()} ({traffic_text} searches)")

    print("\n" + "=" * 60)
    print("✅ 测试成功！代理工作正常")
    print("=" * 60)
    print("\n💡 提示：运行完整工具获取更多数据：")
    print("   python trending-finder.py")

except requests.exceptions.ProxyError:
    print("❌ 代理连接失败\n")
    print("请检查：")
    print("   1. 代理软件是否在运行？")
    print("   2. 端口是否确实是7890？")
    print("   3. 浏览器能否打开 google.com？")

except Exception as e:
    print(f"❌ 获取失败: {e}\n")
    print("可能的原因：")
    print("   - 网络连接问题")
    print("   - 代理设置不正确")
    print("   - Google Trends服务暂时不可用")
