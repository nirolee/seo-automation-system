"""
热词自动发现工具
功能：自动从多个来源发现当前热门关键词和趋势话题
数据源：Google Trends, 百度热搜, Reddit, 知乎热榜等
"""

# -*- coding: utf-8 -*-
import sys
import io

# 修复Windows中文编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import csv
from collections import Counter

class TrendingKeywordFinder:
    """热词发现器"""

    def __init__(self, use_proxy=True, proxy_port=7890):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.all_trends = []

        # 设置代理（用于访问Google）
        if use_proxy:
            self.proxies = {
                'http': f'http://127.0.0.1:{proxy_port}',
                'https': f'http://127.0.0.1:{proxy_port}'
            }
            print(f"✅ 已启用代理: 127.0.0.1:{proxy_port}")
        else:
            self.proxies = None
            print("⚠️  未使用代理")

    def get_google_trends_daily(self, geo='US'):
        """
        获取Google Trends每日热搜
        geo: 国家代码 (US=美国, CN=中国, GB=英国等)
        """
        print(f"\n[1/6] 正在获取Google每日热搜 ({geo})...")

        try:
            # Google Trends RSS Feed（免费！）
            url = f"https://trends.google.com/trends/trendingsearches/daily/rss?geo={geo}"
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)

            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')

            trends = []
            for item in items[:20]:  # 取前20个
                title = item.find('title')
                traffic = item.find('ht:approx_traffic')

                if title:
                    trend = {
                        'keyword': title.text.strip(),
                        'source': f'Google Trends ({geo})',
                        'traffic': traffic.text if traffic else 'N/A',
                        'category': '热搜',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                    }
                    trends.append(trend)

            print(f"   ✅ 找到 {len(trends)} 个Google热搜词")
            return trends

        except Exception as e:
            print(f"   ⚠️  获取失败: {e}")
            return []

    def get_baidu_hot(self):
        """获取百度热搜榜"""
        print(f"\n[2/6] 正在获取百度热搜榜...")

        try:
            url = "https://top.baidu.com/board?tab=realtime"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            trends = []
            # 百度热搜的HTML结构可能变化，这里提供一个基础版本
            items = soup.find_all('div', class_='c-single-text-ellipsis')

            for item in items[:20]:
                keyword = item.text.strip()
                if keyword and len(keyword) > 2:
                    trends.append({
                        'keyword': keyword,
                        'source': '百度热搜',
                        'traffic': 'N/A',
                        'category': '热搜',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                    })

            print(f"   ✅ 找到 {len(trends)} 个百度热搜词")
            return trends

        except Exception as e:
            print(f"   ⚠️  获取失败: {e}")
            return []

    def get_reddit_trending(self, subreddit='all'):
        """获取Reddit热门话题"""
        print(f"\n[3/6] 正在获取Reddit热门话题...")

        try:
            url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=25"
            response = requests.get(url, headers={**self.headers, 'User-Agent': 'TrendFinder/1.0'}, proxies=self.proxies, timeout=15)
            data = response.json()

            trends = []
            for post in data['data']['children'][:20]:
                post_data = post['data']
                title = post_data['title']
                score = post_data['score']

                trends.append({
                    'keyword': title,
                    'source': f'Reddit r/{subreddit}',
                    'traffic': f'{score} upvotes',
                    'category': post_data.get('subreddit', 'general'),
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                })

            print(f"   ✅ 找到 {len(trends)} 个Reddit热门话题")
            return trends

        except Exception as e:
            print(f"   ⚠️  获取失败: {e}")
            return []

    def get_zhihu_hot(self):
        """获取知乎热榜"""
        print(f"\n[4/6] 正在获取知乎热榜...")

        try:
            # 知乎热榜API（可能需要更新）
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total"
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()

            trends = []
            for item in data.get('data', [])[:20]:
                target = item.get('target', {})
                title = target.get('title', '')

                if title:
                    trends.append({
                        'keyword': title,
                        'source': '知乎热榜',
                        'traffic': f"{item.get('detail_text', 'N/A')}",
                        'category': '热搜',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M')
                    })

            print(f"   ✅ 找到 {len(trends)} 个知乎热榜词")
            return trends

        except Exception as e:
            print(f"   ⚠️  获取失败: {e}")
            return []

    def get_google_trends_rising(self, geo='US', category=''):
        """
        获取Google Trends上升趋势词
        category: 分类 (e.g., 'business', 'technology', 'health')
        """
        print(f"\n[5/6] 正在获取Google上升趋势词...")

        try:
            # 使用pytrends库会更好，但这里提供一个简化版本
            # 实际使用时建议安装: pip install pytrends

            # 这里提供一个基于RSS的替代方案
            trends = []
            print(f"   💡 提示: 安装pytrends库可获取更多数据")
            print(f"      命令: pip install pytrends")

            return trends

        except Exception as e:
            print(f"   ⚠️  获取失败: {e}")
            return []

    def get_youtube_trending(self, region='US'):
        """获取YouTube热门视频标题（可提取关键词）"""
        print(f"\n[6/6] 正在获取YouTube热门话题...")

        try:
            # YouTube RSS Feed
            url = "https://www.youtube.com/feed/trending"
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            trends = []
            # 提取视频标题作为热门话题
            scripts = soup.find_all('script')

            # YouTube的数据在JavaScript中，需要解析
            # 这里提供一个简化版本
            print(f"   💡 提示: YouTube需要API密钥才能获取更准确数据")

            return trends

        except Exception as e:
            print(f"   ⚠️  获取失败: {e}")
            return []

    def extract_keywords_from_trends(self, trends):
        """从热门话题中提取关键词"""
        print(f"\n📊 从 {len(trends)} 个话题中提取关键词...")

        all_words = []
        for trend in trends:
            # 移除标点和分词
            text = trend['keyword'].lower()
            # 简单分词（英文按空格，中文需要jieba）
            words = text.split()
            all_words.extend([w for w in words if len(w) > 3])

        # 统计高频词
        word_freq = Counter(all_words)
        top_keywords = word_freq.most_common(30)

        print(f"   ✅ 提取出 {len(top_keywords)} 个高频关键词")
        return top_keywords

    def categorize_trends(self, trends):
        """将趋势词分类到不同利基市场"""
        print(f"\n🏷️  对热词进行分类...")

        categories = {
            '科技数码': ['tech', 'phone', 'laptop', 'software', 'ai', 'app', 'game', 'iphone', 'android'],
            '健康健身': ['health', 'fitness', 'diet', 'workout', 'weight', 'yoga', 'nutrition'],
            '金融理财': ['stock', 'crypto', 'bitcoin', 'investment', 'money', 'finance', 'trading'],
            '生活家居': ['home', 'kitchen', 'furniture', 'decor', 'garden', 'cleaning'],
            '时尚美妆': ['fashion', 'beauty', 'makeup', 'skincare', 'clothing', 'style'],
            '旅游': ['travel', 'hotel', 'flight', 'vacation', 'trip', 'destination'],
            '美食': ['food', 'recipe', 'cooking', 'restaurant', 'coffee', 'wine'],
            '教育': ['course', 'learn', 'tutorial', 'education', 'study', 'training'],
            '娱乐': ['movie', 'music', 'celebrity', 'tv', 'show', 'entertainment']
        }

        categorized = {cat: [] for cat in categories.keys()}
        categorized['其他'] = []

        for trend in trends:
            keyword_lower = trend['keyword'].lower()
            matched = False

            for category, keywords in categories.items():
                if any(kw in keyword_lower for kw in keywords):
                    categorized[category].append(trend)
                    matched = True
                    break

            if not matched:
                categorized['其他'].append(trend)

        # 打印分类结果
        for category, items in categorized.items():
            if items:
                print(f"   {category}: {len(items)}个")

        return categorized

    def score_trend_opportunity(self, trend):
        """评估热词的商业机会分数"""
        score = 0
        keyword = trend['keyword'].lower()

        # 1. 商业意图词
        commercial_keywords = ['best', 'buy', 'review', 'vs', 'how to', 'top', 'cheap', 'price']
        for ck in commercial_keywords:
            if ck in keyword:
                score += 20
                break

        # 2. 长度适中
        word_count = len(keyword.split())
        if 2 <= word_count <= 5:
            score += 15

        # 3. 包含数字
        if any(char.isdigit() for char in keyword):
            score += 10

        # 4. 流量指标
        traffic = trend.get('traffic', '')
        if traffic != 'N/A' and traffic:
            # 提取数字
            import re
            numbers = re.findall(r'\d+', str(traffic))
            if numbers:
                traffic_num = int(numbers[0])
                if traffic_num > 100000:
                    score += 30
                elif traffic_num > 50000:
                    score += 20
                elif traffic_num > 10000:
                    score += 10

        # 5. 时效性（新闻类热词分数低）
        news_keywords = ['死', '去世', '事故', '新闻', '快讯']
        if any(nk in keyword for nk in news_keywords):
            score -= 20

        return max(0, min(100, score))

    def generate_niche_ideas(self, categorized_trends):
        """根据热词生成利基市场建议"""
        print(f"\n💡 生成利基市场建议...")

        suggestions = []

        for category, trends in categorized_trends.items():
            if not trends or category == '其他':
                continue

            # 找出该分类下最高分的趋势
            scored_trends = []
            for trend in trends:
                score = self.score_trend_opportunity(trend)
                scored_trends.append((trend, score))

            scored_trends.sort(key=lambda x: x[1], reverse=True)

            if scored_trends and scored_trends[0][1] > 30:  # 只推荐高分的
                top_trend, top_score = scored_trends[0]

                suggestion = {
                    'category': category,
                    'seed_keyword': top_trend['keyword'],
                    'opportunity_score': top_score,
                    'related_trends': [t[0]['keyword'] for t in scored_trends[1:4]],
                    'suggested_domain': self._generate_domain_idea(top_trend['keyword']),
                    'content_ideas': self._generate_content_ideas(top_trend['keyword'])
                }
                suggestions.append(suggestion)

        return suggestions

    def _generate_domain_idea(self, keyword):
        """根据关键词生成域名建议"""
        # 提取核心词
        words = keyword.lower().split()[:2]
        core = ''.join([w for w in words if len(w) > 3])

        return [
            f"{core}hub.com",
            f"{core}guide.com",
            f"best{core}.com",
            f"{core}review.com"
        ]

    def _generate_content_ideas(self, keyword):
        """生成内容创意"""
        return [
            f"Best {keyword} in 2024",
            f"How to choose {keyword}",
            f"{keyword} review and comparison",
            f"Top 10 {keyword} for beginners",
            f"{keyword} buying guide"
        ]

    def export_results(self, trends, categorized, suggestions, filename='trending_keywords'):
        """导出结果到多个文件"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # 1. 导出所有热词
        with open(f'{filename}_{timestamp}.csv', 'w', newline='', encoding='utf-8-sig') as f:
            fieldnames = ['keyword', 'source', 'traffic', 'category', 'opportunity_score', 'timestamp']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for trend in trends:
                trend['opportunity_score'] = self.score_trend_opportunity(trend)
                writer.writerow(trend)

        print(f"\n💾 已导出到: {filename}_{timestamp}.csv")

        # 2. 导出利基市场建议
        with open(f'{filename}_suggestions_{timestamp}.txt', 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("利基市场建议报告\n")
            f.write("=" * 60 + "\n\n")

            for i, sug in enumerate(suggestions, 1):
                f.write(f"\n建议 #{i}: {sug['category']}\n")
                f.write(f"{'='*40}\n")
                f.write(f"核心关键词: {sug['seed_keyword']}\n")
                f.write(f"机会评分: {sug['opportunity_score']}/100\n")
                f.write(f"\n相关热词:\n")
                for rt in sug['related_trends']:
                    f.write(f"  - {rt}\n")
                f.write(f"\n推荐域名:\n")
                for domain in sug['suggested_domain'][:2]:
                    f.write(f"  - {domain}\n")
                f.write(f"\n内容创意:\n")
                for idea in sug['content_ideas']:
                    f.write(f"  - {idea}\n")
                f.write("\n")

        print(f"💾 已导出到: {filename}_suggestions_{timestamp}.txt")

    def run(self, regions=['US', 'CN']):
        """运行完整流程"""
        print("=" * 60)
        print("🔥 热词自动发现工具")
        print("=" * 60)

        all_trends = []

        # 收集各个来源的热词
        for region in regions:
            if region == 'US':
                trends = self.get_google_trends_daily('US')
                all_trends.extend(trends)

                reddit_trends = self.get_reddit_trending('all')
                all_trends.extend(reddit_trends)

            elif region == 'CN':
                baidu_trends = self.get_baidu_hot()
                all_trends.extend(baidu_trends)

                zhihu_trends = self.get_zhihu_hot()
                all_trends.extend(zhihu_trends)

        # 分类
        categorized = self.categorize_trends(all_trends)

        # 生成建议
        suggestions = self.generate_niche_ideas(categorized)

        # 显示建议
        print("\n" + "=" * 60)
        print("🎯 利基市场机会推荐")
        print("=" * 60)

        suggestions.sort(key=lambda x: x['opportunity_score'], reverse=True)

        for i, sug in enumerate(suggestions[:5], 1):
            print(f"\n【推荐 #{i}】{sug['category']} - 评分: {sug['opportunity_score']}/100")
            print(f"   核心词: {sug['seed_keyword']}")
            print(f"   域名建议: {sug['suggested_domain'][0]}")
            print(f"   相关热词: {', '.join(sug['related_trends'][:3])}")

        # 导出
        self.export_results(all_trends, categorized, suggestions)

        print("\n" + "=" * 60)
        print("✅ 完成！")
        print("=" * 60)

        return {
            'trends': all_trends,
            'categorized': categorized,
            'suggestions': suggestions
        }


if __name__ == '__main__':
    print("\n是否使用代理访问Google? (推荐: 是)")
    use_proxy_input = input("使用代理 (y/n) [默认: y]: ").strip().lower() or 'y'
    use_proxy = use_proxy_input == 'y'

    proxy_port = 7890
    if use_proxy:
        proxy_input = input(f"代理端口 [默认: {proxy_port}]: ").strip()
        if proxy_input:
            proxy_port = int(proxy_input)

    finder = TrendingKeywordFinder(use_proxy=use_proxy, proxy_port=proxy_port)

    print("\n请选择市场:")
    print("1. 美国市场 (US)")
    print("2. 中国市场 (CN)")
    print("3. 双市场 (US + CN)")

    choice = input("\n请输入选择 [默认: 3]: ").strip() or '3'

    regions = []
    if choice == '1':
        regions = ['US']
    elif choice == '2':
        regions = ['CN']
    else:
        regions = ['US', 'CN']

    results = finder.run(regions=regions)

    print("\n💡 下一步:")
    print("   1. 查看生成的CSV文件，找到感兴趣的热词")
    print("   2. 使用 keyword-digger.py 深入挖掘该热词")
    print("   3. 分析竞争对手，制定建站计划")
