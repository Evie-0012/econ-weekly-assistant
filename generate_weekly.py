import sqlite3
from openai import OpenAI
from datetime import datetime, timedelta
import os

DB_PATH = 'wewe-rss.db'

def get_weekly_articles():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    one_week_ago = int((datetime.now() - timedelta(days=7)).timestamp())
    
    cursor.execute('''
        SELECT title, mp_id, id, publish_time 
        FROM articles 
        WHERE publish_time >= ? 
        ORDER BY publish_time DESC
    ''', (one_week_ago,))
    
    articles = []
    for title, mp_id, article_id, pub_time in cursor.fetchall():
        url = f'https://mp.weixin.qq.com/s/{article_id}'
        date_str = datetime.fromtimestamp(pub_time).strftime('%Y-%m-%d')
        articles.append((title, mp_id, date_str, url))
    
    conn.close()
    return articles

def generate_weekly(articles, api_key=None):
    if not api_key:
        api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        if not api_key:
            return "未配置 DeepSeek API Key，请先在侧边栏输入。"
    
    if not articles:
        return "本周暂无新文章，请先运行 fetch_news.py 或上传最新的 weekly_articles.json。"
    
    article_list = "\n".join([
        f"- [{a[2]}] {a[0]}（来源：{a[1]}）\n  链接：{a[3]}"
        for a in articles
    ])
    
    prompt = f"""你是一个专业的《数字经济周刊》主编。请根据下面提供的真实文章，生成一期周刊。

要求：
1. 标题格式：数字经济周刊第XXX期·{datetime.now().strftime('%Y.%m.%d')}-{(datetime.now()-timedelta(days=7)).strftime('%Y.%m.%d')}
2. 分为【数字经济政策】、【数字经济热点】、【数字经济学术】三个板块。
3. 每条新闻包含：
   - 日期 + 新闻标题
   - 正文：写一段约500字的详细摘要，要求语言专业、信息完整，适合课题组成员快速把握要点。可以适当补充背景知识，但核心事实必须基于原文。
   - 在正文末尾另起一行，注明来源和原文链接，格式为：（来源：公众号名称，链接：URL）
4. 只使用下方提供的真实文章，不要编造任何新闻。如果某个板块没有合适的文章，写“本周暂无相关动态”。
5. 周刊末尾注明“责任编辑：课题组”及版权信息。

以下是本周采集的文章：
{article_list}

请生成周刊全文："""
    
    client = OpenAI(
        api_key=api_key,
        base_url='https://api.deepseek.com'
    )
    
    response = client.chat.completions.create(
        model='deepseek-chat',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.3,
        max_tokens=16384
    )
    
    return response.choices[0].message.content