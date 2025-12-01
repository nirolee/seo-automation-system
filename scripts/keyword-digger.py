"""
免费关键词挖掘工具 - 完整版
功能：
1. 从Google/百度自动建议挖掘关键词
2. 分析竞争对手网站
3. 评估关键词价值
4. 生成站点建议
"""

# -*- coding: utf-8 -*-
import sys
import io

# 修复Windows中文编码问题
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import requests
import json
from urllib.parse import quote, urlparse
import time
from bs4 import BeautifulSoup
import re
from collections import Counter
import csv
from datetime import datetime

class KeywordDigger:
    """免费关键词挖掘器"""

    def __init__(self, use_proxy=True, proxy_port=7890):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

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

    def get_google_suggestions(self, seed_keyword, language='en'):
        """获取Google搜索建议"""
        print(f"🔍 正在从Google获取建议词...")
        suggestions = set()

        url = "http://suggestqueries.google.com/complete/search"

        # 策略1: 在关键词后加a-z
        for char in 'abcdefghijklmnopqrstuvwxyz':
            params = {
                'client': 'firefox',
                'q': f'{seed_keyword} {char}',
                'hl': language
            }
            try:
                response = requests.get(url, params=params, proxies=self.proxies, timeout=5)
                data = json.loads(response.text)
                if len(data) > 1:
                    suggestions.update(data[1])
                time.sleep(0.3)
            except Exception as e:
                print(f"   ⚠️  请求失败: {char}")
                continue

        # 策略2: 问题词前缀
        question_words = ['how to', 'what is', 'why', 'when', 'where', 'best', 'top']
        for qw in question_words:
            params = {
                'client': 'firefox',
                'q': f'{qw} {seed_keyword}',
                'hl': language
            }
            try:
                response = requests.get(url, params=params, proxies=self.proxies, timeout=5)
                data = json.loads(response.text)
                if len(data) > 1:
                    suggestions.update(data[1])
                time.sleep(0.3)
            except:
                continue

        print(f"   ✅ 找到 {len(suggestions)} 个Google建议词")
        return list(suggestions)

    def get_baidu_suggestions(self, seed_keyword):
        """获取百度搜索建议（中文）"""
        print(f"🔍 正在从百度获取建议词...")
        suggestions = set()

        url = "https://www.baidu.com/sugrec"

        for char in 'abcdefghijklmnopqrstuvwxyz0123456789':
            params = {
                'prod': 'pc',
                'wd': f'{seed_keyword} {char}',
                'cb': 'jQuery'
            }
            try:
                response = requests.get(url, params=params, proxies=self.proxies, timeout=5)
                # 解析返回的JSONP
                text = response.text
                if 'jQuery' in text:
                    json_str = text[text.find('(')+1:text.rfind(')')]
                    data = json.loads(json_str)
                    if 'g' in data:
                        for item in data['g']:
                            suggestions.add(item['q'])
                time.sleep(0.3)
            except:
                continue

        print(f"   ✅ 找到 {len(suggestions)} 个百度建议词")
        return list(suggestions)

    def search_google_for_competitors(self, keyword, num_results=10):
        """搜索Google找到排名靠前的竞争对手"""
        print(f"🔎 搜索Google找竞争对手: {keyword}")

        # 注意：直接爬Google可能被封，建议使用代理或者手动输入
        # 这里提供一个简化版本

        url = f"https://www.google.com/search?q={quote(keyword)}&num={num_results}"

        try:
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取搜索结果URL
            competitors = []
            for g in soup.find_all('div', class_='g'):
                link = g.find('a')
                if link and 'href' in link.attrs:
                    href = link['href']
                    if href.startswith('http'):
                        domain = urlparse(href).netloc
                        competitors.append({
                            'url': href,
                            'domain': domain,
                            'title': g.find('h3').text if g.find('h3') else ''
                        })

            print(f"   ✅ 找到 {len(competitors)} 个竞争网站")
            return competitors

        except Exception as e:
            print(f"   ⚠️  Google搜索失败: {e}")
            print(f"   💡 建议：手动搜索 '{keyword}' 并提供竞争对手URL")
            return []

    def analyze_competitor_site(self, url):
        """深度分析竞争对手网站"""
        print(f"\n📊 分析网站: {url}")

        analysis = {
            'url': url,
            'domain': urlparse(url).netloc,
            'title': '',
            'keywords': [],
            'content_structure': {},
            'monetization': [],
            'tech_stack': [],
            'article_count': 0,
            'internal_links': [],
            'categories': []
        }

        try:
            response = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. 基本信息
            title = soup.find('title')
            analysis['title'] = title.text.strip() if title else ''

            # 2. Meta信息
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and 'content' in meta_desc.attrs:
                analysis['meta_description'] = meta_desc['content']

            meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
            if meta_keywords and 'content' in meta_keywords.attrs:
                analysis['keywords'] = [k.strip() for k in meta_keywords['content'].split(',')]

            # 3. 内容结构分析
            h1_tags = soup.find_all('h1')
            h2_tags = soup.find_all('h2')
            h3_tags = soup.find_all('h3')

            analysis['content_structure'] = {
                'h1_count': len(h1_tags),
                'h2_count': len(h2_tags),
                'h3_count': len(h3_tags),
                'h1_texts': [h.text.strip() for h in h1_tags[:5]],
                'h2_texts': [h.text.strip() for h in h2_tags[:10]]
            }

            # 4. 检测变现方式
            html_text = response.text.lower()

            if 'adsense' in html_text or 'googlesyndication' in html_text:
                analysis['monetization'].append('Google AdSense')

            if 'amazon-adsystem' in html_text or 'amzn.to' in html_text:
                analysis['monetization'].append('Amazon Associates')

            if 'mediavine' in html_text:
                analysis['monetization'].append('Mediavine')

            if 'ezoic' in html_text:
                analysis['monetization'].append('Ezoic')

            # 5. 技术栈检测
            if 'wp-content' in html_text or 'wordpress' in html_text:
                analysis['tech_stack'].append('WordPress')

            if '__next' in html_text or '_next' in html_text:
                analysis['tech_stack'].append('Next.js')

            if 'gatsby' in html_text:
                analysis['tech_stack'].append('Gatsby')

            # 6. 文章/内容页面链接
            article_links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                # 识别文章URL模式
                if any(pattern in href for pattern in ['/blog/', '/post/', '/article/', '/review/']):
                    article_links.append(href)

            analysis['article_count'] = len(set(article_links))
            analysis['sample_articles'] = list(set(article_links))[:10]

            # 7. 分类/导航
            nav = soup.find('nav')
            if nav:
                categories = [a.text.strip() for a in nav.find_all('a') if a.text.strip()]
                analysis['categories'] = categories[:15]

            print(f"   ✅ 分析完成")
            print(f"   - 标题: {analysis['title'][:50]}...")
            print(f"   - 变现方式: {', '.join(analysis['monetization']) if analysis['monetization'] else '未检测到'}")
            print(f"   - 技术栈: {', '.join(analysis['tech_stack']) if analysis['tech_stack'] else '未检测到'}")
            print(f"   - 文章数量: {analysis['article_count']}")

            return analysis

        except Exception as e:
            print(f"   ❌ 分析失败: {e}")
            return analysis

    def score_keyword(self, keyword):
        """关键词评分（0-100）"""
        score = 0
        kw_lower = keyword.lower()

        # 1. 长度评分（长尾词更好）
        word_count = len(keyword.split())
        if word_count >= 4:
            score += 25  # 长尾词最佳
        elif word_count == 3:
            score += 20
        elif word_count == 2:
            score += 10
        else:
            score += 5

        # 2. 商业意图评分
        high_intent = ['buy', 'price', 'cost', 'cheap', 'affordable', 'discount', 'deal']
        medium_intent = ['best', 'top', 'review', 'vs', 'compare', 'alternative']

        for word in high_intent:
            if word in kw_lower:
                score += 30
                break
        else:
            for word in medium_intent:
                if word in kw_lower:
                    score += 20
                    break

        # 3. 内容类型评分
        question_words = ['how', 'what', 'why', 'when', 'where', 'who', 'which']
        for qw in question_words:
            if kw_lower.startswith(qw):
                score += 15
                break

        # 4. 具体性评分
        if any(char.isdigit() for char in keyword):
            score += 10  # 包含数字（如"top 10"）

        # 5. 年份评分（时效性）
        current_year = datetime.now().year
        if str(current_year) in keyword or str(current_year-1) in keyword:
            score += 10

        return min(score, 100)

    def generate_site_plan(self, keyword_data, competitor_analysis):
        """根据关键词和竞品分析生成站点方案"""
        print("\n" + "="*60)
        print("🎯 生成站点建设方案")
        print("="*60)

        plan = {
            'recommended_domain': '',
            'niche': '',
            'content_strategy': {},
            'monetization_plan': [],
            'tech_stack': '',
            'initial_articles': []
        }

        # 分析最佳利基市场
        top_keywords = sorted(keyword_data, key=lambda x: x['score'], reverse=True)[:20]

        # 提取共同主题
        all_words = []
        for kw in top_keywords:
            all_words.extend(kw['keyword'].lower().split())

        word_freq = Counter(all_words)
        common_words = [w for w, c in word_freq.most_common(10)
                       if w not in ['the', 'a', 'an', 'of', 'to', 'in', 'for', 'and', 'or']]

        plan['niche'] = ' '.join(common_words[:3])

        # 域名建议
        domain_base = ''.join(common_words[:2])
        plan['recommended_domain'] = f"{domain_base}hub.com 或 {domain_base}guide.com"

        # 内容策略
        plan['content_strategy'] = {
            'total_articles': 30,  # 第一个月目标
            'article_types': {
                '产品评测': 10,  # "best XXX", "XXX review"
                '对比文章': 5,   # "XXX vs YYY"
                '指南教程': 10,  # "how to XXX"
                '列表文章': 5    # "top 10 XXX"
            },
            'publishing_frequency': '每天1篇',
            'word_count': '1500-2500字/篇'
        }

        # 变现方案
        monetization_methods = set()
        for comp in competitor_analysis:
            monetization_methods.update(comp.get('monetization', []))

        if monetization_methods:
            plan['monetization_plan'] = list(monetization_methods)
        else:
            plan['monetization_plan'] = ['Google AdSense', 'Amazon Associates']

        # 技术栈推荐
        tech_stacks = []
        for comp in competitor_analysis:
            tech_stacks.extend(comp.get('tech_stack', []))

        if 'WordPress' in tech_stacks:
            plan['tech_stack'] = 'WordPress (最常用，插件丰富)'
        elif 'Next.js' in tech_stacks:
            plan['tech_stack'] = 'Next.js (性能好，SEO友好)'
        else:
            plan['tech_stack'] = 'Next.js (推荐，适合自动化)'

        # 初始文章建议
        plan['initial_articles'] = [kw['keyword'] for kw in top_keywords[:10]]

        # 打印方案
        print(f"\n📌 利基市场: {plan['niche']}")
        print(f"🌐 推荐域名: {plan['recommended_domain']}")
        print(f"\n📝 内容策略:")
        print(f"   - 总文章数: {plan['content_strategy']['total_articles']}篇（第一个月）")
        print(f"   - 发布频率: {plan['content_strategy']['publishing_frequency']}")
        print(f"   - 文章类型:")
        for article_type, count in plan['content_strategy']['article_types'].items():
            print(f"     • {article_type}: {count}篇")

        print(f"\n💰 变现方式: {', '.join(plan['monetization_plan'])}")
        print(f"⚙️  技术栈: {plan['tech_stack']}")

        print(f"\n📄 前10篇文章标题建议:")
        for i, title in enumerate(plan['initial_articles'], 1):
            print(f"   {i:2d}. {title}")

        return plan

    def export_to_csv(self, keyword_data, filename='keywords.csv'):
        """导出关键词到CSV"""
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['keyword', 'score', 'word_count'])
            writer.writeheader()
            writer.writerows(keyword_data)

        print(f"\n💾 关键词已导出到: {filename}")

    def run_complete_workflow(self, seed_keyword, language='en', analyze_competitors=True):
        """完整工作流"""
        print("\n" + "="*60)
        print(f"🚀 开始完整关键词挖掘流程")
        print(f"🎯 种子关键词: {seed_keyword}")
        print(f"🌍 语言: {language}")
        print("="*60 + "\n")

        # 步骤1: 挖掘关键词
        all_keywords = set()

        if language == 'zh' or language == 'zh-CN':
            # 中文市场
            google_kws = self.get_google_suggestions(seed_keyword, 'zh-CN')
            baidu_kws = self.get_baidu_suggestions(seed_keyword)
            all_keywords.update(google_kws)
            all_keywords.update(baidu_kws)
        else:
            # 英文市场
            google_kws = self.get_google_suggestions(seed_keyword, language)
            all_keywords.update(google_kws)

        # 步骤2: 评分
        print(f"\n⭐ 评分 {len(all_keywords)} 个关键词...")
        keyword_data = []
        for kw in all_keywords:
            score = self.score_keyword(kw)
            keyword_data.append({
                'keyword': kw,
                'score': score,
                'word_count': len(kw.split())
            })

        keyword_data.sort(key=lambda x: x['score'], reverse=True)

        # 步骤3: 显示top关键词
        print(f"\n🏆 Top 20 关键词:\n")
        for i, kw in enumerate(keyword_data[:20], 1):
            print(f"{i:2d}. [{kw['score']:3d}分] {kw['keyword']}")

        # 步骤4: 分析竞争对手（如果需要）
        competitor_analysis = []
        if analyze_competitors:
            print(f"\n{'='*60}")
            print("🔍 分析竞争对手网站")
            print(f"{'='*60}")

            # 让用户输入竞争对手URL（因为自动搜索Google可能被封）
            print("\n💡 请手动搜索Google找到排名前3的网站，然后输入URL")
            print("   (如果不想分析，直接按Enter跳过)\n")

            competitor_urls = []
            for i in range(3):
                url = input(f"   竞争对手{i+1} URL: ").strip()
                if url:
                    competitor_urls.append(url)

            for url in competitor_urls:
                analysis = self.analyze_competitor_site(url)
                competitor_analysis.append(analysis)

        # 步骤5: 生成站点方案
        if competitor_analysis:
            plan = self.generate_site_plan(keyword_data, competitor_analysis)

        # 步骤6: 导出
        self.export_to_csv(keyword_data, f'{seed_keyword.replace(" ", "_")}_keywords.csv')

        print(f"\n{'='*60}")
        print("✅ 完整流程完成！")
        print(f"{'='*60}\n")

        return {
            'keywords': keyword_data,
            'competitors': competitor_analysis,
            'plan': plan if competitor_analysis else None
        }


# 使用示例
if __name__ == '__main__':
    print("🎯 免费关键词挖掘 + 竞品分析工具")
    print("="*60)

    # 代理设置
    print("\n是否使用代理访问Google? (推荐: 是)")
    use_proxy_input = input("使用代理 (y/n) [默认: y]: ").strip().lower() or 'y'
    use_proxy = use_proxy_input == 'y'

    proxy_port = 7890
    if use_proxy:
        proxy_input = input(f"代理端口 [默认: {proxy_port}]: ").strip()
        if proxy_input:
            proxy_port = int(proxy_input)

    digger = KeywordDigger(use_proxy=use_proxy, proxy_port=proxy_port)

    # 用户输入
    seed = input("\n请输入种子关键词 (例如: coffee maker): ").strip()
    lang = input("语言 (en/zh) [默认: en]: ").strip() or 'en'

    # 运行完整流程
    results = digger.run_complete_workflow(seed, language=lang, analyze_competitors=True)

    print("\n🎉 所有数据已保存！现在你可以:")
    print("   1. 查看CSV文件获取完整关键词列表")
    print("   2. 根据方案注册域名")
    print("   3. 开始创建网站和内容")
    print("   4. 申请广告联盟账号")
