import sqlite3
from openai import OpenAI
from datetime import datetime, timedelta

DB_PATH = 'news.db'
API_KEY = '你的DeepSeek API Key'

def get_weekly_articles():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    cursor.execute('''
        SELECT title, source, publish_date, summary, url 
        FROM news_articles 
        WHERE publish_date >= ? 
        ORDER BY publish_date DESC
    ''', (one_week_ago,))
    
    articles = cursor.fetchall()
    conn.close()
    return articles

def generate_weekly(articles):
    if not articles:
        return "本周暂无新文章入库，请先运行 fetch_news.py 采集新闻。"
    
    # 组装文章列表
    article_list = "\n".join([
        f"- [{a[2]}] {a[0]}（来源：{a[1]}）\n  摘要：{a[3][:200]}\n  链接：{a[4]}"
        for a in articles
    ])
    
    prompt = f"""你是一个专业的数字经济周刊编辑。请根据以下本周真实采集的新闻文章，生成一期数字经济周刊。

格式要求：
1. 标题格式：数字经济周刊第XXX期·{datetime.now().strftime('%Y.%m.%d')}-{(datetime.now() - timedelta(days=7)).strftime('%Y.%m.%d')}
2. 分为【数字经济政策】、【数字经济热点】、【数字经济学术】三个板块
3. 每条新闻格式：日期 标题（来源），然后附一段简短摘要
4. 只使用下方提供的真实文章，不要编造任何新闻
5. 如果某个板块没有相关文章，写"本周暂无相关动态"
6. 周刊末尾注明责任编辑和版权信息

以下是本周采集的文章：
{article_list}

请生成周刊全文："""
    
    client = OpenAI(
        api_key=API_KEY,
        base_url='https://api.deepseek.com'
    )
    
    response = client.chat.completions.create(
        model='deepseek-chat',
        messages=[{'role': 'user', 'content': prompt}],
        temperature=0.3,
        max_tokens=8192
    )
    
    return response.choices[0].message.content

if __name__ == '__main__':
    articles = get_weekly_articles()
    weekly = generate_weekly(articles)
    
    # 保存到文件
    filename = f'周刊_{datetime.now().strftime("%Y%m%d")}.md'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(weekly)
    
    print(f'周刊已生成：{filename}')
    print('\n' + weekly)